"""Put data into database lambda"""
import os
import re
import json
from functools import partial, wraps
import boto3
import psycopg2
from psycopg2.extras import RealDictCursor
from common.util import get_or_default
from common.logger import with_logger, log_environment, log_document_context
from common.transform.transform_config import get_config


LOGGER_NAME = "main"
DOCUMENT_IMPORT_FAILURE_THRESHOLD = 0.2


def _validate_config(local_config):
    errors = []
    # Validate RDS endpoint and credentials
    attributes = [
        "db_host",
        "db_port",
        "db_name",
        "db_user",
        "db_password",
        "db_connect_timeout",
    ]
    for attribute in attributes:
        if not get_or_default(local_config, attribute):
            errors.append(f"mandatory {attribute} is not provided")
    return errors


def _parse_request(event):
    request = {}
    # Parse S3 objects from the event with S3 bucket name and S3 object key
    if get_or_default(event, "Records"):
        request["documents"] = []
        for record in event["Records"]:
            document = {}
            document["s3_bucket_name"] = get_or_default(record, "s3.bucket.name")
            document["s3_object_key"] = get_or_default(record, "s3.object.key")
            request["documents"].append(document)
    return request


def _validate_request(request):
    errors = []
    # Validate S3 objects with S3 bucket name and S3 object key
    attributes = ["s3_bucket_name", "s3_object_key"]
    documents = get_or_default(request, "documents")
    if not documents:
        errors.append("mandatory docuemnts are not provided")
        return errors
    for document in request["documents"]:
        for attribute in attributes:
            if not get_or_default(document, attribute):
                errors.append(f"mandatory {attribute} is not provided")
    return errors


def _download_document(document, s3):
    data_file = re.sub(r".+/", "", document["s3_object_key"])
    # Download data file to the /tmp directory
    # as in AWS Lambda environment only the /tmp directlry is wirtable
    data_file = f"/tmp/{data_file}"
    s3.download_file(document["s3_bucket_name"], document["s3_object_key"], data_file)
    return data_file


def _parse_document(data_file):
    with open(data_file, "r") as opened_file:
        raw_data = opened_file.read()
        raw_records = raw_data.strip().split("\n")
        raw_records = list(filter(len, raw_records))
        return raw_records


def _parse_record(raw_record):
    record = json.loads(raw_record)
    return record


@with_logger(LOGGER_NAME)
# pylint: disable=too-many-arguments
def _process_record(
    logger, validate_record, put_record_in_db, raw_record, document_statistics, rds
):
    try:
        record = _parse_record(raw_record)
        errors = validate_record(record)
        if not errors:
            try:
                logger.debug(record)
                result = put_record_in_db(record, rds)
                logger.debug(result)
                document_statistics["success_records"] += 1
            except Exception as error:
                logger.error(f"Put record in database {record}: {error}")
                document_statistics["failure_records"] += 1
                rds.rollback()
        else:
            logger.error(f"Validate record {record}: {errors}")
            document_statistics["failure_records"] += 1
    except Exception as error:
        logger.error(f"Parse record {raw_record}: {error}")
        document_statistics["failure_records"] += 1


def track_document_statistics(document_import_failure_threshold):
    """Track document status and total, success, and failure record count"""

    def decorator(original):
        def _put_document_statistics_in_db(logger, document_statistics, rds):
            try:
                with rds.cursor() as cursor:
                    sql = """
                    SELECT ingest.put_document_statistics(
                        %(document_name)s,
                        %(document_status)s,
                        %(total_records)s,
                        %(success_records)s,
                        %(failure_records)s,
                        %(status_reason)s
                    ) document_statistics_id
                    """
                    cursor.execute(sql, document_statistics)
                    rds.commit()
            except Exception as error:
                logger.error(f"Put document statistics in database: {error}")
                rds.rollback()

        def _log_document_statistics(
            logger, document_statistics, document_import_failure_threshold
        ):
            document_status = document_statistics["document_status"]
            total_records = document_statistics["total_records"]
            failure_records = document_statistics["failure_records"]
            if total_records == 0:
                document_statistics["metric_type"] = "EMPTY_DOCUMENT"
                logger.warn(document_statistics)
                return
            failure_ratio = failure_records / total_records
            if document_status == "SUCCESS" and failure_records == 0:
                document_statistics["metric_type"] = "IMPORT_SUCCESS"
                logger.info(document_statistics)
            elif (
                document_status == "SUCCESS"
                and failure_ratio < document_import_failure_threshold
            ):
                document_statistics["metric_type"] = "FAILED_RECORDS_BELOW_THRESHOLD"
                logger.warn(document_statistics)
            else:
                document_statistics["metric_type"] = "IMPORT_FAILURE"
                logger.error(document_statistics)

        @wraps(original)
        def decorated(logger, f1, document, s3, rds, *args, **kwargs):
            document_statistics = {
                "document_name": document["s3_object_key"],
                "document_status": "SUCCESS",
                "metric_type": "IMPORT_SUCCESS",
                "status_reason": None,
                "total_records": 0,
                "success_records": 0,
                "failure_records": 0,
            }
            result = original(
                logger, f1, document, document_statistics, s3, rds, *args, **kwargs
            )
            _log_document_statistics(
                logger, document_statistics, document_import_failure_threshold
            )
            _put_document_statistics_in_db(logger, document_statistics, rds)
            return result

        return decorated

    return decorator


@with_logger(LOGGER_NAME)
def _move_document_to_processed(logger, document, s3):
    try:
        source_bucket = document["s3_bucket_name"]
        source_key = document["s3_object_key"]
        destination_bucket = source_bucket
        destinaiton_key = f"PROCESSED/{source_key}"
        copy_source = {"Bucket": source_bucket, "Key": source_key}
        s3.copy_object(
            Bucket=destination_bucket, CopySource=copy_source, Key=destinaiton_key
        )
        s3.delete_object(Bucket=source_bucket, Key=source_key)
    except Exception as error:
        logger.error(f"Move document to processed: {error}")


def _track_document_failure(document_statistics, error_type, error_message):
    document_statistics["document_status"] = "FAILURE"
    status_reason = {"error_type": error_type, "error_message": error_message}
    document_statistics["status_reason"] = json.dumps(status_reason)


@with_logger(LOGGER_NAME)
@log_document_context
@track_document_statistics(DOCUMENT_IMPORT_FAILURE_THRESHOLD)
# pylint: disable=too-many-arguments
def _process_document(logger, process_record, document, document_statistics, s3, rds):
    try:
        data_file = _download_document(document, s3)
        try:
            raw_records = _parse_document(data_file)
            if not raw_records:
                logger.warn("Empty document")
            for raw_record in raw_records:
                document_statistics["total_records"] += 1
                process_record(raw_record, document_statistics, rds)
            _move_document_to_processed(document, s3)
        except Exception as error:
            logger.error(f"Parse document: {error}")
            _track_document_failure(
                document_statistics, "Parse document error", str(error)
            )
        finally:
            if os.path.exists(data_file):
                os.remove(data_file)
    except Exception as error:
        logger.error(f"Download document: {error}")
        _track_document_failure(
            document_statistics, "Download document error", str(error)
        )


def _process_request(process_document, request, s3, rds):
    for document in request["documents"]:
        process_document(document, s3, rds)


@with_logger(LOGGER_NAME)
@log_environment
# pylint: disable=unused-argument
def _lambda_handler(logger, process_request, event, context):
    local_config = get_config()
    errors = _validate_config(local_config)
    if not errors:
        request = _parse_request(event)
        errors = _validate_request(request)
        if not errors:
            try:
                s3 = boto3.client("s3")
                local_config["s3"] = s3
                try:
                    rds_config = {
                        "host": local_config["db_host"],
                        "port": local_config["db_port"],
                        "dbname": local_config["db_name"],
                        "user": local_config["db_user"],
                        "password": local_config["db_password"],
                        "connect_timeout": local_config["db_connect_timeout"],
                        "cursor_factory": RealDictCursor,
                    }
                    rds = psycopg2.connect(**rds_config)
                    local_config["rds"] = rds
                    try:
                        process_request(request, s3, rds)
                    finally:
                        rds.close()
                except Exception as error:
                    logger.critical(f"Connect to RDS: {error}")
            except Exception as error:
                logger.critical(f"Create S3 client: {error}")
        else:
            logger.error(f"Validate request: {errors}")
    else:
        logger.critical(f"Validate configuration: {errors}")


def create_lambda_handler(validate_record, put_record_in_db):
    """Create labmda handler for provided specific functions and configuration"""
    process_record = partial(_process_record, validate_record, put_record_in_db)
    process_document = partial(_process_document, process_record)
    process_request = partial(_process_request, process_document)
    lambda_handler = partial(_lambda_handler, process_request)
    return lambda_handler

"""Put data into database lambda"""
import os
import re
import json
from functools import partial, wraps
import boto3
import psycopg2
from psycopg2.extras import RealDictCursor
from common.logger import with_logger, log_environment, log_document_context


LOGGER_NAME = "main"


def _validate_config(local_config):
    errors = []
    # Validate RDS endpoint and credentials
    attributes = ["db_host", "db_port", "db_name", "db_user", "db_password"]
    for attribute in attributes:
        if not local_config.get(attribute):
            errors.append(f"mandatory {attribute} is not provided")
    return errors


def _prepare_request(event):
    request = {}
    # Prepare S3 objects from the event with S3 bucket name and S3 object key
    if event.get("Records"):
        request["documents"] = []
        for record in event["Records"]:
            document = {}
            document["s3_bucket_name"] = (
                record.get("s3", {}).get("bucket", {}).get("name")
            )
            document["s3_object_key"] = (
                record.get("s3", {}).get("object", {}).get("key")
            )
            request["documents"].append(document)
    return request


def _validate_request(request):
    errors = []
    # Validate S3 objects with S3 bucket name and S3 object key
    attributes = ["s3_bucket_name", "s3_object_key"]
    for document in request["documents"]:
        for attribute in attributes:
            if not document.get(attribute):
                errors.append(
                    f"Document {document}: mandatory {attribute} is not provided"
                )
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
        return raw_records


def _prepare_record(raw_record):
    record = json.loads(raw_record)
    return record


@with_logger(LOGGER_NAME)
def _process_record(
    logger, validate_record, put_record_in_db, raw_record, document_statictics, rds
):
    try:
        record = _prepare_record(raw_record)
        errors = validate_record(record)
        if not errors:
            try:
                logger.info(record)
                result = put_record_in_db(record, rds)
                logger.info(result)
                document_statictics["success_records"] += 1
            except Exception as error:
                logger.error(f"Put record in database {record}: {error}")
                document_statictics["failure_records"] += 1
                rds.rollback()
        else:
            logger.error(f"Validate record {record}: {errors}")
            document_statictics["failure_records"] += 1
    except Exception as error:
        logger.error(f"Prepare record {raw_record}: {error}")
        document_statictics["failure_records"] += 1


def track_document_statistics(original):
    """Track document status and total, success, and failure record count"""

    def _put_document_statistics_in_db(logger, document_statictics, rds):
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
                cursor.execute(sql, document_statictics)
                rds.commit()
        except Exception as error:
            logger.error(
                f"Put document statistics in database {document_statictics}: {error}"
            )
            rds.rollback()

    @wraps(original)
    def decorated(logger, f1, document, s3, rds, *args, **kwargs):
        document_statictics = {
            "document_name": document["s3_object_key"],
            "document_status": "SUCCESS",
            "status_reason": None,
            "total_records": 0,
            "success_records": 0,
            "failure_records": 0,
        }
        result = original(
            logger, f1, document, document_statictics, s3, rds, *args, **kwargs
        )
        logger.debug(document_statictics)
        _put_document_statistics_in_db(logger, document_statictics, rds)
        return result

    return decorated


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
        logger.error(f"Move document to processed {document}: {error}")


@with_logger(LOGGER_NAME)
@log_document_context
@track_document_statistics
def _process_document(logger, process_record, document, document_statictics, s3, rds):
    try:
        data_file = _download_document(document, s3)
        try:
            raw_records = _parse_document(data_file)
            for raw_record in raw_records:
                document_statictics["total_records"] += 1
                process_record(raw_record, document_statictics, rds)
            _move_document_to_processed(document, s3)
        except Exception as error:
            logger.error(f"Parse document {data_file}: {error}")
            document_statictics["document_status"] = "FAILURE"
            status_reason = {
                "error_type": "Parse document error",
                "error_message": f"{error}",
                "context_data": f"{data_file}",
            }
            document_statictics["status_reason"] = json.dumps(status_reason)
        finally:
            os.remove(data_file)
    except Exception as error:
        logger.error(f"Downlaod document {document}: {error}")
        document_statictics["document_status"] = "FAILURE"
        status_reason = {
            "error_type": "Downlaod document error",
            "error_message": f"{error}",
            "context_data": f"{document}",
        }
        document_statictics["status_reason"] = json.dumps(status_reason)


def _process_request(process_document, request, s3, rds):
    for document in request["documents"]:
        process_document(document, s3, rds)


@with_logger(LOGGER_NAME)
@log_environment
def _lambda_handler(logger, process_request, local_config, event, context):
    errors = _validate_config(local_config)
    if not errors:
        request = _prepare_request(event)
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
            logger.error(f"Validate request {request}: {errors}")
    else:
        logger.critical(f"Validate configuration {local_config}: {errors}")


def create_lambda_handler(validate_record, put_record_in_db, local_config):
    """Create labmda handler for provided specific functions and configuration"""
    process_record = partial(_process_record, validate_record, put_record_in_db)
    process_document = partial(_process_document, process_record)
    process_request = partial(_process_request, process_document)
    lambda_handler = partial(_lambda_handler, process_request, local_config)
    return lambda_handler

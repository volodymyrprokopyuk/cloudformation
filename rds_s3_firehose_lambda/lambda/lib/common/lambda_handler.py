"""Put data into database lambda"""
import os
import re
import json
from functools import partial
import boto3
import psycopg2
from psycopg2.extras import RealDictCursor


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


def _process_record(validate_record, put_record_in_db, raw_record, rds):
    try:
        record = _prepare_record(raw_record)
        errors = validate_record(record)
        if not errors:
            try:
                print(record)
                result = put_record_in_db(rds, record)
                print(result)
            except Exception as error:
                print(f"ERROR: put record in database {record}: {error}")
                rds.rollback()
        else:
            print(f"ERROR: validate record {record}: {errors}")
    except Exception as error:
        print(f"ERROR: prepare record {raw_record}: {error}")


def _process_document(process_record, document, s3, rds):
    try:
        data_file = _download_document(document, s3)
        try:
            raw_records = _parse_document(data_file)
            for raw_record in raw_records:
                process_record(raw_record, rds)
        except Exception as error:
            print(f"ERROR: parse data file {data_file}: {error}")
        finally:
            os.remove(data_file)
    except Exception as error:
        print(f"ERROR: downlaod document {document}: {error}")


def _process_request(process_document, request, s3, rds):
    for document in request["documents"]:
        process_document(document, s3, rds)


def _lambda_handler(process_request, local_config, event, context):
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
                    print(f"ERROR: connect to RDS: {error}")
            except Exception as error:
                print(f"ERROR: create S3 client: {error}")
        else:
            print(f"ERROR: validate request {request}: {errors}")
    else:
        print(f"ERROR: validate configuration {local_config}: {errors}")


def create_lambda_handler(validate_record, put_record_in_db, local_config):
    """Create labmda handler for provided specific functions and configuration"""
    process_record = partial(_process_record, validate_record, put_record_in_db)
    process_document = partial(_process_document, process_record)
    process_request = partial(_process_request, process_document)
    lambda_handler = partial(_lambda_handler, process_request, local_config)
    return lambda_handler

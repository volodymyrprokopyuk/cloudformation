"""Put product into database lambda"""
import os
import re
import json
import boto3
import psycopg2
from config import get_config


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
        request["s3_objects"] = []
        for record in event["Records"]:
            s3_object = {}
            s3_object["s3_bucket_name"] = (
                record.get("s3", {}).get("bucket", {}).get("name")
            )
            s3_object["s3_object_key"] = (
                record.get("s3", {}).get("object", {}).get("key")
            )
            request["s3_objects"].append(s3_object)
    return request


def _validate_request(request):
    errors = []
    # Validate S3 objects with S3 bucket name and S3 object key
    attributes = ["s3_bucket_name", "s3_object_key"]
    for s3_object in request["s3_objects"]:
        for attribute in attributes:
            if not s3_object.get(attribute):
                errors.append(
                    f"S3 object {s3_object}: mandatory {attribute} is not provided"
                )
    return errors


def _download_s3_object(s3, s3_object):
    data_file = re.sub(r".+/", "", s3_object["s3_object_key"])
    s3.download_file(s3_object["s3_bucket_name"], s3_object["s3_object_key"], data_file)
    return data_file


def _parse_data_file(data_file):
    with open(data_file, "r") as opened_data_file:
        raw_data = opened_data_file.read()
        raw_records = raw_data.strip().split("\n")
        return raw_records


def _prepare_record(raw_record):
    record = json.loads(raw_record)
    return record


def _validate_record(record):
    errors = []
    attributes = [
        "product_external_id",
        "product_title",
        "first_protection_ts",
        "registration_ts",
        "protection_status",
    ]
    for attribute in attributes:
        if not record.get(attribute):
            errors.append(f"mandatory {attribute} is not provided")
    attribute = "product_image_url"
    if attribute in record and not record.get(attribute):
        errors.append(f"optional {attribute} is empty")
    return errors


def _put_record_in_db(rds, record):
    with rds.cursor() as cursor:
        cursor.execute("SELECT 1234;")
        row = cursor.fetchone()
        print(row)


def _process_request(request):
    local_config = get_config()
    s3 = local_config["s3"]
    rds = local_config["rds"]
    for s3_object in request["s3_objects"]:
        try:
            data_file = _download_s3_object(s3, s3_object)
            try:
                raw_records = _parse_data_file(data_file)
                for raw_record in raw_records:
                    try:
                        record = _prepare_record(raw_record)
                        errors = _validate_record(record)
                        if not errors:
                            try:
                                record_id = _put_record_in_db(rds, record)
                                print(record_id)
                            except Exception as error:
                                print(
                                    f"ERROR: put record in database {record}: {error}"
                                )
                        else:
                            print(f"ERROR: validate record {record}: {errors}")
                    except Exception as error:
                        print(f"ERROR: prepare record {raw_record}: {error}")
            except Exception as error:
                print(f"ERROR: parse data file {data_file}: {error}")
            finally:
                os.remove(data_file)
        except Exception as error:
            print(f"ERROR: downlaod S3 object {s3_object}: {error}")


def lambda_handler(event, context):
    """Put product into database lambda handler"""
    local_config = get_config()
    errors = _validate_config(local_config)
    if not errors:
        request = _prepare_request(event)
        errors = _validate_request(request)
        if not errors:
            try:
                s3 = boto3.client("s3")
                local_config["s3"] = s3
                try:
                    rds = psycopg2.connect(
                        host=local_config["db_host"],
                        port=local_config["db_port"],
                        dbname=local_config["db_name"],
                        user=local_config["db_user"],
                        password=local_config["db_password"],
                    )
                    local_config["rds"] = rds
                    try:
                        _process_request(request)
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


if __name__ == "__main__":
    test_event = {
        "Records": [
            {
                "s3": {
                    "bucket": {"name": "vlad-stack-firehose-delivery-stream"},
                    "object": {
                        "key": "product/2019/06/23/18/ProductDeliveryStream-1-2019-06-23-18-09-28-6b84569e-91e6-4ef7-81d9-fce3ac6384b7"
                    },
                }
            },
            {
                "s3": {
                    "bucket": {"name": "vlad-stack-firehose-delivery-stream"},
                    "object": {
                        "key": "product/2019/06/24/09/ProductDeliveryStream-1-2019-06-24-09-18-32-beef7cae-dc75-4d56-a17f-2b075c8c5592"
                    },
                }
            },
        ]
    }
    lambda_handler(test_event, None)

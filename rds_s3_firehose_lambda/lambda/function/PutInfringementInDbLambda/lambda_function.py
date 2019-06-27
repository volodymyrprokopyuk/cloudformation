"""Put infirngement into database lambda"""
from config import get_config
from common.lambda_handler import create_lambda_handler


def _validate_infringement_record(record):
    errors = []
    attributes = [
        "product_external_id",
        "pirate_source_external_id",
        "detection_ts",
        "infringement_url",
        "infringement_status",
    ]
    for attribute in attributes:
        if not record.get(attribute):
            errors.append(f"mandatory {attribute} is not provided")
    return errors


def _put_infringement_record_in_db(rds, record):
    with rds.cursor() as cursor:
        sql = """
        SELECT put_infringement(
            %(product_external_id)s,
            %(pirate_source_external_id)s,
            %(detection_ts)s,
            %(infringement_url)s,
            %(infringement_status)s
        ) infringement_id;
        """
        cursor.execute(sql, record)
        result = cursor.fetchone()
        rds.commit()
        return result


lambda_handler = create_lambda_handler(
    _validate_infringement_record, _put_infringement_record_in_db, get_config()
)


if __name__ == "__main__":
    test_event = {
        "Records": [
            {
                "s3": {
                    "bucket": {"name": "vlad-stack-firehose-delivery-stream"},
                    "object": {
                        "key": "infringement/2019/06/27/12/InfringementDeliveryStream"
                        + "-1-2019-06-27-12-51-31-35c3ce6b-f80c-42f0-8159-1811ccd161a4"
                    },
                }
            },
        ]
    }
    lambda_handler(test_event, None)

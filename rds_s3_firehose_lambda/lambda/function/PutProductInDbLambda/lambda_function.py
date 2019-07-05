"""Put product into database lambda"""
from config import get_config
from common.lambda_handler import create_lambda_handler


def _validate_product_record(record):
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


def _put_product_record_in_db(rds, record):
    with rds.cursor() as cursor:
        sql = """
        SELECT ingest.put_product(
            %(product_external_id)s,
            %(product_title)s,
            %(first_protection_ts)s,
            %(registration_ts)s,
            %(protection_status)s,
            %(product_image_url)s
        ) product_id;
        """
        cursor.execute(sql, record)
        result = cursor.fetchone()
        rds.commit()
        return result


lambda_handler = create_lambda_handler(
    _validate_product_record, _put_product_record_in_db, get_config()
)


if __name__ == "__main__":
    test_event = {
        "Records": [
            {
                "s3": {
                    "bucket": {
                        "name": "infringement-ingest-dev-firehose-infringement-delivery"
                    },
                    "object": {
                        "key": "product/2019/07/04/11/"
                        + "infringement-ingest-DEV-ProductDeliveryStream"
                        + "-1-2019-07-04-11-57-42-d55d2f5d-b0d4-4743-a84f-147dd201a670"
                    },
                }
            }
        ]
    }
    lambda_handler(test_event, None)

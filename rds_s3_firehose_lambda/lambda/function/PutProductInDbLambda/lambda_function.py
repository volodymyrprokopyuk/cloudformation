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
        SELECT put_product(
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
                    "bucket": {"name": "vlad-stack-firehose-delivery-stream"},
                    "object": {
                        "key": "product/2019/06/23/18/ProductDeliveryStream"
                        + "-1-2019-06-23-18-09-28-6b84569e-91e6-4ef7-81d9-fce3ac6384b7"
                    },
                }
            },
            {
                "s3": {
                    "bucket": {"name": "vlad-stack-firehose-delivery-stream"},
                    "object": {
                        "key": "product/2019/06/24/09/ProductDeliveryStream"
                        + "-1-2019-06-24-09-18-32-beef7cae-dc75-4d56-a17f-2b075c8c5592"
                    },
                }
            },
        ]
    }
    lambda_handler(test_event, None)

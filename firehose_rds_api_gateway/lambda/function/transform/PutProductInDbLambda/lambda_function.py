"""Put product into database lambda"""
from common.util import get_or_default
from common.transform.transform_lambda_handler import create_lambda_handler


def _validate_product_record(record):
    errors = []
    attributes = [
        "partner_uuid",
        "product_external_id",
        "product_title",
        "first_protection_ts",
        "registration_ts",
        "protection_status",
    ]
    for attribute in attributes:
        if not get_or_default(record, attribute):
            errors.append(f"mandatory {attribute} is not provided")
    attribute = "product_image_url"
    if attribute in record and not get_or_default(record, attribute):
        errors.append(f"optional {attribute} is not provided")
    return errors


def _put_product_record_in_db(record, rds):
    with rds.cursor() as cursor:
        sql = """
        SELECT ingest.put_product(
            %(partner_uuid)s,
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
    _validate_product_record, _put_product_record_in_db
)

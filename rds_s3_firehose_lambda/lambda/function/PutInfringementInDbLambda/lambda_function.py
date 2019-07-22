"""Put infirngement into database lambda"""
from common.transform_lambda_handler import create_lambda_handler


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


def _put_infringement_record_in_db(record, rds):
    with rds.cursor() as cursor:
        sql = """
        SELECT ingest.put_infringement(
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
    _validate_infringement_record, _put_infringement_record_in_db
)


# if __name__ == "__main__":
#     lambda_handler({}, None)

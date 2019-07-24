from pytest import fixture
from common.test.util import create_transform_event


# Transform event fixture
@fixture
def invalid_records_above_threshold_event():
    event = create_transform_event(
        "bucket_name", "infringement_invalid_records_above_threshold.txt"
    )
    return event


@fixture
def invalid_records_below_threshold_event():
    event = create_transform_event(
        "bucket_name", "infringement_invalid_records_below_threshold.txt"
    )
    return event


@fixture
def success_event():
    event = create_transform_event("bucket_name", "infringement_success.txt")
    return event


# Database fixture
def _put_product_in_db(rds, products):
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
        for product in products:
            cursor.execute(sql, product)
        rds.commit()
        yield
        sql = """DELETE FROM ingest.product;"""
        cursor.execute(sql)
        rds.commit()


@fixture
def post_delete_all_from_infringement(rds):
    yield
    with rds.cursor() as cursor:
        sql = """DELETE FROM ingest.infringement;"""
        cursor.execute(sql)
        rds.commit()


@fixture
def create_and_delete_product(rds):
    products = [
        {
            "product_external_id": "PROD001",
            "product_title": "Product title 1",
            "first_protection_ts": "2019-01-06 21:34:54+0200",
            "product_image_url":  "https://api.movies.com/movies/1",
            "registration_ts": "2019-06-02 12:23:57+0200",
            "protection_status": "ACTIVE",
        },
        {
            "product_external_id": "PROD002",
            "product_title": "Product title 2",
            "first_protection_ts": "2019-02-07 22:35:55+0200",
            "product_image_url": "https://api.movies.com/movies/2",
            "registration_ts": "2019-06-02 12:23:57+0200",
            "protection_status": "INACTIVE"
        }
    ]
    yield from _put_product_in_db(rds, products)

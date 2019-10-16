from pytest import fixture
import common.test.util as test_util
from common.transform.test.util import create_transform_event


# Put partner in database fixture
@fixture
def put_partner_in_db_ids(rds):
    yield from test_util.put_partner_in_db_ids(rds, test_util.PARTNERS)


# Put product in database fixture
@fixture
def put_product_in_db_ids(rds, put_partner_in_db_ids):
    yield from test_util.put_product_in_db_ids(rds, test_util.PRODUCTS)


# Put pirate source in database fixture
@fixture
def put_pirate_source_in_db_ids(rds, put_partner_in_db_ids):
    yield from test_util.put_pirate_source_in_db_ids(rds, test_util.PIRATE_SOURCES)


@fixture
def post_delete_dummy_infringement(rds):
    yield from test_util.post_delete_dummy_infringement(rds)


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

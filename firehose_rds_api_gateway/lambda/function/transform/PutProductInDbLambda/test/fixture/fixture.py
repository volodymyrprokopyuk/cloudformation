from pytest import fixture
import common.test.util as test_util
from common.transform.test.util import create_transform_event


# Put partner in database fixture
@fixture
def put_partner_in_db_ids(rds):
    yield from test_util.put_partner_in_db_ids(rds, test_util.PARTNERS)


# Transform event fixture
@fixture
def invalid_records_above_threshold_event():
    event = create_transform_event(
        "bucket_name", "product_invalid_records_above_threshold.txt"
    )
    return event


@fixture
def invalid_records_below_threshold_event():
    event = create_transform_event(
        "bucket_name", "product_invalid_records_below_threshold.txt"
    )
    return event


@fixture
def non_existing_partner_event():
    event = create_transform_event("bucket_name", "product_non_existing_partner.txt")
    return event


@fixture
def success_event():
    event = create_transform_event("bucket_name", "product_success.txt")
    return event

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

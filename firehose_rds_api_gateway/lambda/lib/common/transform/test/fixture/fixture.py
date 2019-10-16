from pytest import fixture
from common.transform.test.util import create_transform_event


# Transform event fixture
@fixture
def invalid_event():
    event = create_transform_event("", "")
    return event


@fixture
def non_existing_document_event():
    event = create_transform_event("bucket_name", "object_key")
    return event


@fixture
def empty_document_event():
    event = create_transform_event("bucket_name", "document_empty.txt")
    return event


@fixture
def invalid_document_event():
    event = create_transform_event("bucket_name", "document_invalid.txt")
    return event


@fixture
def event():
    event = create_transform_event("bucket_name", "object_key")
    return event

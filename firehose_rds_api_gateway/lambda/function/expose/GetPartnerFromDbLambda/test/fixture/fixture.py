from pytest import fixture
import common.test.util as test_util
from common.expose.test.util import create_expose_event


# Put partner in database fixture
@fixture
def put_partner_in_db_ids(rds):
    yield from test_util.put_partner_in_db_ids(rds, test_util.PARTNERS)


# Get partner request fixture
@fixture
def invalid_partner_id_request():
    event = create_expose_event(
        "GET", "/partners", path_parameters={"partnerId": "invalidId"}
    )
    return event


@fixture
def invalid_partner_uuid_request():
    event = create_expose_event(
        "GET", "/partners", querystring_parameters={"partnerUuid": "invalidUuid"}
    )
    return event


@fixture
def invalid_partner_name_and_partner_status_request():
    event = create_expose_event(
        "GET",
        "/partners",
        querystring_parameters={"partnerName": "x", "partnerStatus": "x"},
    )
    return event


@fixture
def invalid_partner_id_and_partner_uuid_combination_request():
    event = create_expose_event(
        "GET",
        "/partners",
        path_parameters={"partnerId": "1"},
        querystring_parameters={"partnerUuid": "aa61382a-a98d-4ddf-a4a7-6d3543328af5"},
    )
    return event


@fixture
def invalid_partner_parameters_combination_request():
    event = create_expose_event(
        "GET",
        "/partners",
        path_parameters={"partnerId": "1"},
        querystring_parameters={"partnerName": "partner 1"},
    )
    return event


@fixture
def all_partners_request():
    event = create_expose_event("GET", "/partners")
    return event


@fixture
def single_partner_by_id_request():
    event = create_expose_event("GET", "/partners", path_parameters={"partnerId": "1"})
    return event


@fixture
def single_partner_by_uuid_request():
    event = create_expose_event(
        "GET", "/partners", path_parameters={"partnerUuid": "1"}
    )
    return event


@fixture
def non_existing_partner_id_request():
    event = create_expose_event("GET", "/partners", path_parameters={"partnerId": "0"})
    return event


@fixture
def query_partner_request():
    event = create_expose_event(
        "GET",
        "/partners",
        querystring_parameters={"partnerName": "partner 1", "partnerStatus": "ACTIVE"},
    )
    return event

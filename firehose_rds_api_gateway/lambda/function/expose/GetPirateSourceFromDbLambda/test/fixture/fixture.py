from pytest import fixture
import common.test.util as test_util
from common.expose.test.util import create_expose_event


# Put partner in database fixture
@fixture
def put_partner_in_db_ids(rds):
    yield from test_util.put_partner_in_db_ids(rds, test_util.PARTNERS)


# Put Pirate source in database fixture
@fixture
def put_pirate_source_in_db_ids(rds, put_partner_in_db_ids):
    yield from test_util.put_pirate_source_in_db_ids(rds, test_util.PIRATE_SOURCES)


# Get pirate source request fixture
@fixture
def missing_partner_id_request():
    event = create_expose_event("GET", "/pirate-sources")
    return event


@fixture
def invalid_partner_id_request():
    event = create_expose_event(
        "GET", "/pirate-sources", querystring_parameters={"partnerId": "invalidId"}
    )
    return event


@fixture
def invalid_pirate_source_id_request():
    event = create_expose_event(
        "GET", "/pirate-sources", path_parameters={"pirateSourceId": "invalidId"}
    )
    return event


@fixture
def invalid_pirate_source_name_and_type_request():
    event = create_expose_event(
        "GET",
        "/pirate-sources",
        querystring_parameters={"pirateSourceName": "x", "pirateSourceType": "x"},
    )
    return event


@fixture
def invalid_pirate_source_parameters_combination_request():
    event = create_expose_event(
        "GET",
        "/pirate-sources",
        path_parameters={"pirateSourceId": "1"},
        querystring_parameters={"pirateSourceName": "name 1"},
    )
    return event


@fixture
def all_pirate_sources_for_partner_request():
    event = create_expose_event(
        "GET", "/pirate-sources", querystring_parameters={"partnerId": "1"}
    )
    return event


@fixture
def single_pirate_source_request():
    event = create_expose_event(
        "GET", "/pirate-sources", path_parameters={"pirateSourceId": "1"}
    )
    return event


@fixture
def non_existing_pirate_source_id_request():
    event = create_expose_event(
        "GET", "/pirate-sources", path_parameters={"pirateSourceId": "0"}
    )
    return event


@fixture
def query_pirate_source_request():
    event = create_expose_event(
        "GET",
        "/pirate-sources",
        querystring_parameters={
            "pirateSourceName": "name 1",
            "pirateSourceType": "DUMMY_SEARCH_ENGINE",
        },
    )
    return event

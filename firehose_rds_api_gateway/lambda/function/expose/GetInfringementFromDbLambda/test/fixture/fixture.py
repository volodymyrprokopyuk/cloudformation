from pytest import fixture
import common.test.util as test_util
from common.expose.test.util import create_expose_event


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


# Put infringement in database fixture
@fixture
def put_infringement_in_db_ids(rds, put_product_in_db_ids, put_pirate_source_in_db_ids):
    yield from test_util.put_infringement_in_db_ids(rds, test_util.INFRINGEMENTS)


# Get infringement request fixture
@fixture
def missing_any_of_mandatory_parameters_request():
    event = create_expose_event("GET", "/infringements")
    return event


@fixture
def invalid_partner_id_and_partner_uuid_combination_request():
    event = create_expose_event(
        "GET",
        "/infringements",
        querystring_parameters={
            "partnerId": "1",
            "partnerUuid": "aa61382a-a98d-4ddf-a4a7-6d3543328af5",
        },
    )
    return event


@fixture
def invalid_partner_id_and_partner_uuid_request():
    event = create_expose_event(
        "GET",
        "/infringements",
        querystring_parameters={"partnerId": "invalidId", "partnerUuid": "invalidUuid"},
    )
    return event


@fixture
def invalid_product_id_request():
    event = create_expose_event(
        "GET", "/infringements", querystring_parameters={"productId": "invalidId"}
    )
    return event


@fixture
def invalid_pirate_source_id_request():
    event = create_expose_event(
        "GET",
        "/infringements",
        querystring_parameters={"productId": "1", "pirateSourceId": "invalidId"},
    )
    return event


@fixture
def invalid_infringement_status_request():
    event = create_expose_event(
        "GET",
        "/infringements",
        querystring_parameters={"productId": "1", "infringementStatus": "x"},
    )
    return event


@fixture
def invalid_since_ts_request():
    event = create_expose_event(
        "GET",
        "/infringements",
        querystring_parameters={"productId": "1", "sinceTs": "invalidTs"},
    )
    return event


@fixture
def invalid_till_ts_request():
    event = create_expose_event(
        "GET",
        "/infringements",
        querystring_parameters={"productId": "1", "tillTs": "invalidTs"},
    )
    return event


@fixture
def invalid_limit_request():
    event = create_expose_event(
        "GET",
        "/infringements",
        querystring_parameters={"productId": "1", "limit": "invalidLimit"},
    )
    return event


@fixture
def invalid_offset_request():
    event = create_expose_event(
        "GET",
        "/infringements",
        querystring_parameters={"productId": "1", "offset": "invalidOffset"},
    )
    return event


@fixture
def too_big_limit_request():
    event = create_expose_event(
        "GET",
        "/infringements",
        querystring_parameters={"productId": "1", "limit": "1001"},
    )
    return event


@fixture
def too_big_offset_request():
    event = create_expose_event(
        "GET",
        "/infringements",
        querystring_parameters={"productId": "1", "offset": "101"},
    )
    return event


@fixture
def infringements_by_product_id_request():
    event = create_expose_event(
        "GET", "/infringements", querystring_parameters={"productId": "1"}
    )
    return event


@fixture
def infringements_by_non_existing_product_id_request():
    event = create_expose_event(
        "GET", "/infringements", querystring_parameters={"productId": "0"}
    )
    return event


@fixture
def infringements_by_partner_id_request():
    event = create_expose_event(
        "GET", "/infringements", querystring_parameters={"partnerId": "1"}
    )
    return event


@fixture
def infringements_by_partner_uuid_request():
    event = create_expose_event(
        "GET",
        "/infringements",
        querystring_parameters={"partnerUuid": "aa61382a-a98d-4ddf-a4a7-6d3543328af5"},
    )
    return event


@fixture
def infringements_by_product_id_and_pirate_source_id_request():
    event = create_expose_event(
        "GET",
        "/infringements",
        querystring_parameters={"productId": "1", "pirateSourceId": "1"},
    )
    return event


@fixture
def infringements_by_product_id_and_with_infringement_status_request():
    event = create_expose_event(
        "GET",
        "/infringements",
        querystring_parameters={"productId": "0", "infringementStatus": "ACTIVE"},
    )
    return event


@fixture
def infringements_by_product_id_since_ts_request():
    event = create_expose_event(
        "GET",
        "/infringements",
        querystring_parameters={
            "productId": "0",
            "sinceTs": "2000-01-01 00:00:01+0000",
        },
    )
    return event


@fixture
def infringements_by_product_id_till_ts_request():
    event = create_expose_event(
        "GET",
        "/infringements",
        querystring_parameters={"productId": "0", "tillTs": "2000-01-01 00:00:02+0000"},
    )
    return event


@fixture
def infringements_by_product_id_since_ts_till_ts_request():
    event = create_expose_event(
        "GET",
        "/infringements",
        querystring_parameters={
            "productId": "0",
            "sinceTs": "2000-01-01 00:00:01+0000",
            "tillTs": "2000-01-01 00:00:02+0000",
        },
    )
    return event


@fixture
def infringements_by_product_id_limit_request():
    event = create_expose_event(
        "GET", "/infringements", querystring_parameters={"productId": "0", "limit": "1"}
    )
    return event

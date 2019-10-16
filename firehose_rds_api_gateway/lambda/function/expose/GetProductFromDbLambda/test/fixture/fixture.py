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


# Get product request fixture
@fixture
def missing_partner_id_request():
    event = create_expose_event("GET", "/products")
    return event


@fixture
def invalid_partner_id_request():
    event = create_expose_event(
        "GET", "/products", querystring_parameters={"partnerId": "invalidId"}
    )
    return event


@fixture
def invalid_product_id_request():
    event = create_expose_event(
        "GET", "/products", path_parameters={"productId": "invalidId"}
    )
    return event


@fixture
def invalid_product_title_and_protection_status_request():
    event = create_expose_event(
        "GET",
        "/products",
        querystring_parameters={"productTitle": "x", "protectionStatus": "x"},
    )
    return event


@fixture
def invalid_product_parameters_combination_request():
    event = create_expose_event(
        "GET",
        "/products",
        path_parameters={"productId": "1"},
        querystring_parameters={"productTitle": "title 1"},
    )
    return event


@fixture
def all_products_for_partner_request():
    event = create_expose_event(
        "GET", "/products", querystring_parameters={"partnerId": "1"}
    )
    return event


@fixture
def single_product_request():
    event = create_expose_event("GET", "/products", path_parameters={"productId": "1"})
    return event


@fixture
def non_existing_product_id_request():
    event = create_expose_event("GET", "/products", path_parameters={"productId": "0"})
    return event


@fixture
def query_product_request():
    event = create_expose_event(
        "GET",
        "/products",
        querystring_parameters={
            "productTitle": "title 1",
            "protectionStatus": "ACTIVE",
        },
    )
    return event

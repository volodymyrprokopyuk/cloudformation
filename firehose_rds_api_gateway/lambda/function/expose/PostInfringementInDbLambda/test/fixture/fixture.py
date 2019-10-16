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


@fixture
def post_delete_dummy_infringement(rds):
    yield from test_util.post_delete_dummy_infringement(rds)


# Post infringement request fixture
@fixture
def empty_body_request():
    event = create_expose_event("POST", "/infringements")
    return event


@fixture
def invalid_body_request():
    event = create_expose_event("POST", "/infringements", body='{"invalidBody"')
    return event


@fixture
def missing_mandatory_properties_request():
    event = create_expose_event("POST", "/infringements", body={"missing": None})
    return event


@fixture
def invalid_properties_request():
    event = create_expose_event(
        "POST",
        "/infringements",
        body={
            "partnerUuid": "invalidUuid",
            "productExternalId": "",
            "pirateSourceExternalId": "",
            "detectionTs": "invalidTs",
            "infringementUrl": "x",
            "infringementStatus": "x",
            "infringementScreenshot": "x",
        },
    )
    return event


@fixture
def invalid_properties_without_infringement_screenshot_request():
    event = create_expose_event(
        "POST",
        "/infringements",
        body={
            "partnerUuid": "invalidUuid",
            "productExternalId": "",
            "pirateSourceExternalId": "",
            "detectionTs": "invalidTs",
            "infringementUrl": "x",
            "infringementStatus": "x",
        },
    )
    return event


@fixture
def valid_infringement_request():
    event = create_expose_event(
        "POST",
        "/infringements",
        body={
            "partnerUuid": "aa61382a-a98d-4ddf-a4a7-6d3543328af5",
            "productExternalId": "PROD001",
            "pirateSourceExternalId": "PSRC001",
            "detectionTs": "2000-01-01 00:00:00+0000",
            "infringementUrl": "https://www.pirate1.com/movies/1",
            # pylint: disable=line-too-long
            "infringementScreenshot": {
                "screenshotUrl": ["https://s3.aws.com/screenshot-01.jpg"]
            },
            "infringementStatus": "ACTIVE",
        },
    )
    return event

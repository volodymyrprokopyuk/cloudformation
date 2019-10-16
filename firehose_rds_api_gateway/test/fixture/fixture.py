from pytest import fixture
import common.test.util as test_util


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


@fixture
def post_delete_dummy_infringement(rds):
    yield from test_util.post_delete_dummy_infringement(rds)


@fixture
def valid_infringement_json_request():
    infringement_request = """{
        "partnerUuid": "aa61382a-a98d-4ddf-a4a7-6d3543328af5",
        "productExternalId": "PROD001",
        "pirateSourceExternalId": "PSRC001",
        "detectionTs": "2000-01-01 00:00:00+0000",
        "infringementUrl": "https://www.pirate1.com/movies/1",
        "infringementScreenshot": {
            "screenshotUrl": ["https://s3.aws.com/screenshot-01.jpg"]
        },
        "infringementStatus": "ACTIVE"
    }"""
    return infringement_request

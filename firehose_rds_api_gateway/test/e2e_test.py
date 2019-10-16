import os
import json
import requests
from common.test.util import (
    get_dummy_product_count,
    get_dummy_infringement_count,
    get_infringement_by_id,
)


API = os.getenv("API")


# Ingest E2E test
def test_import_document_success(rds, post_delete_dummy_infringement):
    product_count = get_dummy_product_count(rds)
    assert product_count > 0
    infringement_count = get_dummy_infringement_count(rds)
    assert infringement_count > 0


# Expose E2E test
def test_get_partner_by_name_success(put_partner_in_db_ids):
    partner_name = "dummy"
    response = requests.get(f"{API}/partners?partnerName={partner_name}")
    assert response.status_code == 200
    body = response.json()
    assert len(body["data"]) > 0
    assert partner_name in body["data"][0]["partnerName"].lower()


def test_get_pirate_source_by_name_success(put_pirate_source_in_db_ids):
    pirate_source_name = "dummy"
    response = requests.get(
        f"{API}/pirate-sources?pirateSourceName={pirate_source_name}"
    )
    assert response.status_code == 200
    body = response.json()
    assert len(body["data"]) > 0
    assert pirate_source_name in body["data"][0]["pirateSourceName"].lower()


def test_get_product_by_title_success(put_product_in_db_ids):
    product_title = "dummy"
    response = requests.get(f"{API}/products?productTitle={product_title}")
    assert response.status_code == 200
    body = response.json()
    assert len(body["data"]) > 0
    assert product_title in body["data"][0]["productTitle"].lower()


def test_get_infringement_by_partner_uuid_success(
    put_partner_in_db_ids,
    put_product_in_db_ids,
    put_pirate_source_in_db_ids,
    put_infringement_in_db_ids,
):
    partner_uuid = "aa61382a-a98d-4ddf-a4a7-6d3543328af5"
    response = requests.get(f"{API}/infringements?partnerUuid={partner_uuid}")
    assert response.status_code == 200
    body = response.json()
    assert len(body["data"]) > 0
    assert body["data"][0]["partnerUuid"] == partner_uuid


def test_get_infringement_by_product_id_and_pirate_source_id_success(
    put_product_in_db_ids, put_pirate_source_in_db_ids, put_infringement_in_db_ids
):
    product_id = min(put_product_in_db_ids)
    pirate_source_id = min(put_pirate_source_in_db_ids)
    response = requests.get(
        f"{API}/infringements?productId={product_id}&pirateSourceId={pirate_source_id}"
    )
    assert response.status_code == 200
    body = response.json()
    assert len(body["data"]) > 0
    assert body["data"][0]["productId"] == product_id
    assert body["data"][0]["pirateSourceId"] == pirate_source_id


def test_post_infringement_success(
    put_product_in_db_ids,
    put_pirate_source_in_db_ids,
    valid_infringement_json_request,
    rds,
    post_delete_dummy_infringement,
):
    response = requests.post(
        f"{API}/infringements", data=valid_infringement_json_request
    )
    body = response.json()
    assert response.status_code == 200
    infringement_id = body["data"]["infringementId"]
    infringement_from_db = get_infringement_by_id(rds, infringement_id)
    request_body = json.loads(valid_infringement_json_request)
    assert request_body["infringementUrl"] == infringement_from_db["infringement_url"]

import os
import json
import requests
from common.test.util import get_dummy_infringement_count, get_infringement_by_id


API = os.getenv("API")


# Ingest smoke test
def test_import_document_success(rds, post_delete_dummy_infringement):
    infringement_count = get_dummy_infringement_count(rds)
    assert infringement_count > 0


# Expose smoke test
def test_get_partner_by_id_success(put_partner_in_db_ids):
    partner_id = min(put_partner_in_db_ids)
    response = requests.get(f"{API}/partners/{partner_id}")
    assert response.status_code == 200
    body = response.json()
    assert len(body["data"]) == 1
    assert body["data"][0]["partnerId"] == partner_id


def test_get_pirate_source_by_id_success(put_pirate_source_in_db_ids):
    pirate_source_id = min(put_pirate_source_in_db_ids)
    response = requests.get(f"{API}/pirate-sources/{pirate_source_id}")
    assert response.status_code == 200
    body = response.json()
    assert len(body["data"]) == 1
    assert body["data"][0]["pirateSourceId"] == pirate_source_id


def test_get_product_by_id_success(put_product_in_db_ids):
    product_id = min(put_product_in_db_ids)
    response = requests.get(f"{API}/products/{product_id}")
    assert response.status_code == 200
    body = response.json()
    assert len(body["data"]) == 1
    assert body["data"][0]["productId"] == product_id


def test_get_infringement_by_partner_id_success(
    put_partner_in_db_ids,
    put_product_in_db_ids,
    put_pirate_source_in_db_ids,
    put_infringement_in_db_ids,
):
    partner_id = min(put_partner_in_db_ids)
    response = requests.get(f"{API}/infringements?partnerId={partner_id}")
    assert response.status_code == 200
    body = response.json()
    assert len(body["data"]) > 0
    assert body["data"][0]["partnerId"] == partner_id


def test_get_infringement_by_product_id_success(
    put_product_in_db_ids, put_infringement_in_db_ids
):
    product_id = min(put_product_in_db_ids)
    response = requests.get(f"{API}/infringements?productId={product_id}")
    assert response.status_code == 200
    body = response.json()
    assert len(body["data"]) > 0
    assert body["data"][0]["productId"] == product_id


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

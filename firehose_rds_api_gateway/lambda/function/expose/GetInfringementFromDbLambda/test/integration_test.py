import json
from lambda_function import lambda_handler


def test_infringements_by_product_id_request_success(
    put_product_in_db_ids,
    put_infringement_in_db_ids,
    infringements_by_product_id_request,
):
    request = infringements_by_product_id_request
    product_id = min(put_product_in_db_ids)
    request["queryStringParameters"]["productId"] = product_id
    response = lambda_handler(infringements_by_product_id_request, None)
    body = json.loads(response["body"])
    assert response["statusCode"] == 200
    assert len(body["data"]) > 0


def test_infringements_by_non_existing_product_id_request_success(
    put_infringement_in_db_ids, infringements_by_non_existing_product_id_request
):
    response = lambda_handler(infringements_by_non_existing_product_id_request, None)
    body = json.loads(response["body"])
    assert response["statusCode"] == 200
    assert len(body["data"]) == 0


def test_infringements_by_partner_id_request_success(
    put_partner_in_db_ids,
    put_product_in_db_ids,
    put_pirate_source_in_db_ids,
    put_infringement_in_db_ids,
    infringements_by_partner_id_request,
):
    request = infringements_by_partner_id_request
    partner_id = min(put_partner_in_db_ids)
    request["queryStringParameters"]["partnerId"] = partner_id
    response = lambda_handler(infringements_by_partner_id_request, None)
    body = json.loads(response["body"])
    assert response["statusCode"] == 200
    assert len(body["data"]) > 0


def test_infringements_by_partner_uuid_request_success(
    put_partner_in_db_ids,
    put_product_in_db_ids,
    put_pirate_source_in_db_ids,
    put_infringement_in_db_ids,
    infringements_by_partner_uuid_request,
):
    request = infringements_by_partner_uuid_request
    partner_uuid = "aa61382a-a98d-4ddf-a4a7-6d3543328af5"
    request["queryStringParameters"]["partnerUuid"] = partner_uuid
    response = lambda_handler(infringements_by_partner_uuid_request, None)
    body = json.loads(response["body"])
    assert response["statusCode"] == 200
    assert len(body["data"]) > 0
    assert body["data"][0]["partnerUuid"] == partner_uuid


def test_infringements_by_product_id_and_pirate_source_id_request_success(
    put_product_in_db_ids,
    put_pirate_source_in_db_ids,
    put_infringement_in_db_ids,
    infringements_by_product_id_and_pirate_source_id_request,
):
    request = infringements_by_product_id_and_pirate_source_id_request
    product_id = min(put_product_in_db_ids)
    pirate_source_id = min(put_pirate_source_in_db_ids)
    request["queryStringParameters"]["productId"] = product_id
    request["queryStringParameters"]["pirateSourceId"] = pirate_source_id
    response = lambda_handler(
        infringements_by_product_id_and_pirate_source_id_request, None
    )
    body = json.loads(response["body"])
    assert response["statusCode"] == 200
    assert len(body["data"]) > 0


def test_infringements_by_product_id_and_with_infringement_status_request_success(
    put_product_in_db_ids,
    put_infringement_in_db_ids,
    infringements_by_product_id_and_with_infringement_status_request,
):
    request = infringements_by_product_id_and_with_infringement_status_request
    product_id = min(put_product_in_db_ids)
    request["queryStringParameters"]["productId"] = product_id
    response = lambda_handler(
        infringements_by_product_id_and_with_infringement_status_request, None
    )
    body = json.loads(response["body"])
    assert response["statusCode"] == 200
    assert len(body["data"]) > 0
    assert body["data"][0]["infringementStatus"] == "ACTIVE"


def test_infringements_by_product_id_since_ts_request_success(
    put_product_in_db_ids,
    put_infringement_in_db_ids,
    infringements_by_product_id_since_ts_request,
):
    request = infringements_by_product_id_since_ts_request
    product_id = min(put_product_in_db_ids)
    request["queryStringParameters"]["productId"] = product_id
    response = lambda_handler(infringements_by_product_id_since_ts_request, None)
    body = json.loads(response["body"])
    assert response["statusCode"] == 200
    assert len(body["data"]) > 0


def test_infringements_by_product_id_till_ts_request_success(
    put_product_in_db_ids,
    put_infringement_in_db_ids,
    infringements_by_product_id_till_ts_request,
):
    request = infringements_by_product_id_till_ts_request
    product_id = min(put_product_in_db_ids)
    request["queryStringParameters"]["productId"] = product_id
    response = lambda_handler(infringements_by_product_id_till_ts_request, None)
    body = json.loads(response["body"])
    assert response["statusCode"] == 200
    assert len(body["data"]) > 0


def test_infringements_by_product_id_since_ts_till_ts_request_success(
    put_product_in_db_ids,
    put_infringement_in_db_ids,
    infringements_by_product_id_since_ts_till_ts_request,
):
    request = infringements_by_product_id_since_ts_till_ts_request
    product_id = min(put_product_in_db_ids)
    request["queryStringParameters"]["productId"] = product_id
    response = lambda_handler(
        infringements_by_product_id_since_ts_till_ts_request, None
    )
    body = json.loads(response["body"])
    assert response["statusCode"] == 200
    assert len(body["data"]) > 0


def test_infringements_by_product_id_limit_request_success(
    put_product_in_db_ids,
    put_infringement_in_db_ids,
    infringements_by_product_id_limit_request,
):
    request = infringements_by_product_id_limit_request
    product_id = min(put_product_in_db_ids)
    request["queryStringParameters"]["productId"] = product_id
    response = lambda_handler(infringements_by_product_id_limit_request, None)
    body = json.loads(response["body"])
    assert response["statusCode"] == 200
    assert len(body["data"]) == 1

import json
from lambda_function import lambda_handler


def test_all_partners_request_success(put_partner_in_db_ids, all_partners_request):
    response = lambda_handler(all_partners_request, None)
    body = json.loads(response["body"])
    assert response["statusCode"] == 200
    assert len(body["data"]) >= len(put_partner_in_db_ids)


def test_single_partner_by_id_request_success(
    put_partner_in_db_ids, single_partner_by_id_request
):
    partner_id = min(put_partner_in_db_ids)
    single_partner_by_id_request["pathParameters"]["partnerId"] = partner_id
    response = lambda_handler(single_partner_by_id_request, None)
    body = json.loads(response["body"])
    assert response["statusCode"] == 200
    assert len(body["data"]) == 1
    assert body["data"][0]["partnerId"] == partner_id


def test_single_partner_by_uuid_request_success(
    put_partner_in_db_ids, single_partner_by_uuid_request
):
    partner_id = min(put_partner_in_db_ids)
    single_partner_by_uuid_request["pathParameters"]["partnerId"] = partner_id
    response = lambda_handler(single_partner_by_uuid_request, None)
    body = json.loads(response["body"])
    assert response["statusCode"] == 200
    assert len(body["data"]) == 1
    assert body["data"][0]["partnerId"] == partner_id


def test_non_existing_partner_id_request_success(
    put_partner_in_db_ids, non_existing_partner_id_request
):
    response = lambda_handler(non_existing_partner_id_request, None)
    body = json.loads(response["body"])
    assert response["statusCode"] == 200
    assert len(body["data"]) == 0


def test_query_partner_request_success(put_partner_in_db_ids, query_partner_request):
    partner_name = query_partner_request["queryStringParameters"]["partnerName"]
    response = lambda_handler(query_partner_request, None)
    body = json.loads(response["body"])
    assert response["statusCode"] == 200
    assert len(body["data"]) > 0
    assert partner_name in body["data"][0]["partnerName"]

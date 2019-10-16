import json
from lambda_function import lambda_handler


def test_all_products_for_partner_request_success(
    put_partner_in_db_ids, put_product_in_db_ids, all_products_for_partner_request
):
    partner_id = min(put_partner_in_db_ids)
    all_products_for_partner_request["queryStringParameters"]["partnerId"] = partner_id
    response = lambda_handler(all_products_for_partner_request, None)
    body = json.loads(response["body"])
    assert response["statusCode"] == 200
    assert len(body["data"]) == len(put_product_in_db_ids)


def test_single_product_request_success(put_product_in_db_ids, single_product_request):
    product_id = min(put_product_in_db_ids)
    single_product_request["pathParameters"]["productId"] = product_id
    response = lambda_handler(single_product_request, None)
    body = json.loads(response["body"])
    assert response["statusCode"] == 200
    assert len(body["data"]) == 1
    assert body["data"][0]["productId"] == product_id


def test_non_existing_product_id_request_success(
    put_product_in_db_ids, non_existing_product_id_request
):
    response = lambda_handler(non_existing_product_id_request, None)
    body = json.loads(response["body"])
    assert response["statusCode"] == 200
    assert len(body["data"]) == 0


def test_query_product_request_success(put_product_in_db_ids, query_product_request):
    product_title = query_product_request["queryStringParameters"]["productTitle"]
    response = lambda_handler(query_product_request, None)
    body = json.loads(response["body"])
    assert response["statusCode"] == 200
    assert len(body["data"]) > 0
    assert product_title in body["data"][0]["productTitle"]

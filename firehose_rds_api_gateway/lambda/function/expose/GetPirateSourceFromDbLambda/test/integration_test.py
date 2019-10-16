import json
from lambda_function import lambda_handler


def test_all_pirate_sources_for_partner_request_success(
    put_partner_in_db_ids,
    put_pirate_source_in_db_ids,
    all_pirate_sources_for_partner_request,
):
    partner_id = min(put_partner_in_db_ids)
    all_pirate_sources_for_partner_request["queryStringParameters"][
        "partnerId"
    ] = partner_id
    response = lambda_handler(all_pirate_sources_for_partner_request, None)
    body = json.loads(response["body"])
    assert response["statusCode"] == 200
    assert len(body["data"]) >= len(put_pirate_source_in_db_ids)


def test_single_pirate_source_request_success(
    put_pirate_source_in_db_ids, single_pirate_source_request
):
    pirate_source_id = min(put_pirate_source_in_db_ids)
    single_pirate_source_request["pathParameters"]["pirateSourceId"] = pirate_source_id
    response = lambda_handler(single_pirate_source_request, None)
    body = json.loads(response["body"])
    assert response["statusCode"] == 200
    assert len(body["data"]) == 1
    assert body["data"][0]["pirateSourceId"] == pirate_source_id


def test_non_existing_pirate_source_id_request_success(
    put_pirate_source_in_db_ids, non_existing_pirate_source_id_request
):
    response = lambda_handler(non_existing_pirate_source_id_request, None)
    body = json.loads(response["body"])
    assert response["statusCode"] == 200
    assert len(body["data"]) == 0


def test_query_pirate_source_request_success(
    put_pirate_source_in_db_ids, query_pirate_source_request
):
    pirate_source_name = query_pirate_source_request["queryStringParameters"][
        "pirateSourceName"
    ]
    response = lambda_handler(query_pirate_source_request, None)
    body = json.loads(response["body"])
    assert response["statusCode"] == 200
    assert len(body["data"]) > 0
    assert pirate_source_name in body["data"][0]["pirateSourceName"]

import json
from common.test.util import get_infringement_by_id
from lambda_function import lambda_handler


def test_post_infringement_success(
    put_product_in_db_ids,
    put_pirate_source_in_db_ids,
    valid_infringement_request,
    rds,
    post_delete_dummy_infringement,
):
    response = lambda_handler(valid_infringement_request, None)
    body = json.loads(response["body"])
    assert response["statusCode"] == 200
    infringement_id = body["data"]["infringementId"]
    infringement_from_db = get_infringement_by_id(rds, infringement_id)
    request_body = json.loads(valid_infringement_request["body"])
    assert request_body["infringementUrl"] == infringement_from_db["infringement_url"]

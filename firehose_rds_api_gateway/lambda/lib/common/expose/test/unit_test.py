import json
from lambda_function import lambda_handler


# Expose lambda common test
def test_validate_empty_configuration_error(event):
    response = lambda_handler(event, None)
    body = json.loads(response["body"])
    assert response["statusCode"] == 500
    assert body["error"]["message"] == "Validate configuration error"


def test_validate_invalid_configuration_error(event, invalid_db_config, caplog):
    response = lambda_handler(event, None)
    body = json.loads(response["body"])
    assert response["statusCode"] == 500
    assert body["error"]["message"] == "Validate configuration error"

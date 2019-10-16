import json
from unittest.mock import patch, MagicMock
from common.test.util import mock_pg_fetchone
from lambda_function import lambda_handler


# Post Infringement lambda test
def test_empty_body_request_error(db_config, empty_body_request):
    response = lambda_handler(empty_body_request, None)
    body = json.loads(response["body"])
    assert response["statusCode"] == 400
    assert body["error"]["message"] == "Validate request error"


def test_invalid_body_request_error(db_config, invalid_body_request):
    invalid_body_request["body"] = '{"invalidBody"'
    response = lambda_handler(invalid_body_request, None)
    body = json.loads(response["body"])
    assert response["statusCode"] == 400
    assert body["error"]["message"] == "Validate request error"


def test_missing_mandatory_properties_request_error(
    db_config, missing_mandatory_properties_request
):
    response = lambda_handler(missing_mandatory_properties_request, None)
    body = json.loads(response["body"])
    assert response["statusCode"] == 400
    assert body["error"]["message"] == "Validate request error"


def test_invalid_properties_request_error(db_config, invalid_properties_request):
    response = lambda_handler(invalid_properties_request, None)
    body = json.loads(response["body"])
    assert response["statusCode"] == 400
    assert body["error"]["message"] == "Validate request error"


def test_invalid_properties_without_infringement_screenshot_request_error(
    db_config, invalid_properties_without_infringement_screenshot_request
):
    response = lambda_handler(
        invalid_properties_without_infringement_screenshot_request, None
    )
    body = json.loads(response["body"])
    assert response["statusCode"] == 400
    assert body["error"]["message"] == "Validate request error"


@patch("psycopg2.connect", side_effect=Exception("Connect to RDS error"))
def test_connect_to_rds_error(pg_connect_mock, db_config, valid_infringement_request):
    response = lambda_handler(valid_infringement_request, None)
    body = json.loads(response["body"])
    assert response["statusCode"] == 500
    assert body["error"]["message"] == "Connect to RDS error"


@patch("psycopg2.connect")
def test_put_infringement_into_db_error(
    pg_connect_mock, db_config, valid_infringement_request
):
    rds_mock = MagicMock()
    pg_connect_mock.return_value = rds_mock
    rds_mock.cursor.side_effect = Exception("Put data into database error")
    response = lambda_handler(valid_infringement_request, None)
    body = json.loads(response["body"])
    assert response["statusCode"] == 500
    assert body["error"]["message"] == "Database error"
    rds_mock.close.assert_called_once()


@patch("psycopg2.connect")
def test_post_infringement_success(
    pg_connect_mock, db_config, valid_infringement_request
):
    infringement_id = 1
    mock_pg_fetchone(pg_connect_mock, {"infringement_id": infringement_id})
    response = lambda_handler(valid_infringement_request, None)
    body = json.loads(response["body"])
    assert response["statusCode"] == 200
    assert body["data"]["infringementId"] == infringement_id

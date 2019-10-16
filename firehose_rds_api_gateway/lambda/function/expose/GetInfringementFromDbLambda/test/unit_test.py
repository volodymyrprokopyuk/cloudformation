import json
from unittest.mock import patch, MagicMock
from common.test.util import mock_pg_fetchall
from lambda_function import lambda_handler


# Expose Infringement lambda test
def test_missing_any_of_mandatory_parameters_request_error(
    db_config, missing_any_of_mandatory_parameters_request
):
    response = lambda_handler(missing_any_of_mandatory_parameters_request, None)
    body = json.loads(response["body"])
    assert response["statusCode"] == 400
    assert body["error"]["message"] == "Validate request error"


def test_invalid_partner_id_and_partner_uuid_combination_request_error(
    db_config, invalid_partner_id_and_partner_uuid_combination_request
):
    response = lambda_handler(
        invalid_partner_id_and_partner_uuid_combination_request, None
    )
    body = json.loads(response["body"])
    assert response["statusCode"] == 400
    assert body["error"]["message"] == "Validate request error"


def test_invalid_partner_id_and_partner_uuid_request_error(
    db_config, invalid_partner_id_and_partner_uuid_request
):
    response = lambda_handler(invalid_partner_id_and_partner_uuid_request, None)
    body = json.loads(response["body"])
    assert response["statusCode"] == 400
    assert body["error"]["message"] == "Validate request error"


def test_invalid_product_id_request_error(db_config, invalid_product_id_request):
    response = lambda_handler(invalid_product_id_request, None)
    body = json.loads(response["body"])
    assert response["statusCode"] == 400
    assert body["error"]["message"] == "Validate request error"


def test_invalid_pirate_source_id_request_error(
    db_config, invalid_pirate_source_id_request
):
    response = lambda_handler(invalid_pirate_source_id_request, None)
    body = json.loads(response["body"])
    assert response["statusCode"] == 400
    assert body["error"]["message"] == "Validate request error"


def test_invalid_infringement_status_request_error(
    db_config, invalid_infringement_status_request
):
    response = lambda_handler(invalid_infringement_status_request, None)
    body = json.loads(response["body"])
    assert response["statusCode"] == 400
    assert body["error"]["message"] == "Validate request error"


def test_invalid_since_ts_request_error(db_config, invalid_since_ts_request):
    response = lambda_handler(invalid_since_ts_request, None)
    body = json.loads(response["body"])
    assert response["statusCode"] == 400
    assert body["error"]["message"] == "Validate request error"


def test_invalid_till_ts_request_error(db_config, invalid_till_ts_request):
    response = lambda_handler(invalid_till_ts_request, None)
    body = json.loads(response["body"])
    assert response["statusCode"] == 400
    assert body["error"]["message"] == "Validate request error"


def test_invalid_limit_request_error(db_config, invalid_limit_request):
    response = lambda_handler(invalid_limit_request, None)
    body = json.loads(response["body"])
    assert response["statusCode"] == 400
    assert body["error"]["message"] == "Validate request error"


def test_invalid_offset_request_error(db_config, invalid_offset_request):
    response = lambda_handler(invalid_offset_request, None)
    body = json.loads(response["body"])
    assert response["statusCode"] == 400
    assert body["error"]["message"] == "Validate request error"


def test_too_big_limit_request_error(db_config, too_big_limit_request):
    response = lambda_handler(too_big_limit_request, None)
    body = json.loads(response["body"])
    assert response["statusCode"] == 400
    assert body["error"]["message"] == "Validate request error"


def test_too_big_offset_request_error(db_config, too_big_offset_request):
    response = lambda_handler(too_big_offset_request, None)
    body = json.loads(response["body"])
    assert response["statusCode"] == 400
    assert body["error"]["message"] == "Validate request error"


@patch("psycopg2.connect", side_effect=Exception("Connect to RDS error"))
def test_connect_to_rds_error(
    pg_connect_mock, db_config, infringements_by_product_id_request
):
    response = lambda_handler(infringements_by_product_id_request, None)
    body = json.loads(response["body"])
    assert response["statusCode"] == 500
    assert body["error"]["message"] == "Connect to RDS error"


@patch("psycopg2.connect")
def test_get_data_from_db_error(
    pg_connect_mock, db_config, infringements_by_product_id_request
):
    rds_mock = MagicMock()
    pg_connect_mock.return_value = rds_mock
    rds_mock.cursor.side_effect = Exception("Get data from database error")
    response = lambda_handler(infringements_by_product_id_request, None)
    body = json.loads(response["body"])
    assert response["statusCode"] == 500
    assert body["error"]["message"] == "Database error"
    rds_mock.close.assert_called_once()


@patch("psycopg2.connect")
def test_infringements_by_product_id_request_success(
    pg_connect_mock, db_config, infringements_by_product_id_request
):
    mock_pg_fetchall(pg_connect_mock, [])
    response = lambda_handler(infringements_by_product_id_request, None)
    assert response["statusCode"] == 200


@patch("psycopg2.connect")
def test_infringements_by_product_id_and_pirate_source_id_request_success(
    pg_connect_mock, db_config, infringements_by_product_id_and_pirate_source_id_request
):
    mock_pg_fetchall(pg_connect_mock, [])
    response = lambda_handler(
        infringements_by_product_id_and_pirate_source_id_request, None
    )
    assert response["statusCode"] == 200

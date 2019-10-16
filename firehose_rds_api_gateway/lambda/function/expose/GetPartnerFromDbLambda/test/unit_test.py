import json
from unittest.mock import patch, MagicMock
from common.test.util import mock_pg_fetchall
from lambda_function import lambda_handler


# Expose Product lambda test
def test_invalid_partner_id_request_error(db_config, invalid_partner_id_request):
    response = lambda_handler(invalid_partner_id_request, None)
    body = json.loads(response["body"])
    assert response["statusCode"] == 400
    assert body["error"]["message"] == "Validate request error"


def test_invalid_partner_uuid_request_error(db_config, invalid_partner_uuid_request):
    response = lambda_handler(invalid_partner_uuid_request, None)
    body = json.loads(response["body"])
    assert response["statusCode"] == 400
    assert body["error"]["message"] == "Validate request error"


def test_invalid_partner_name_and_partner_status_request_error(
    db_config, invalid_partner_name_and_partner_status_request
):
    response = lambda_handler(invalid_partner_name_and_partner_status_request, None)
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


def test_invalid_partner_parameters_combination_request_error(
    db_config, invalid_partner_parameters_combination_request
):
    response = lambda_handler(invalid_partner_parameters_combination_request, None)
    body = json.loads(response["body"])
    assert response["statusCode"] == 400
    assert body["error"]["message"] == "Validate request error"


@patch("psycopg2.connect", side_effect=Exception("Connect to RDS error"))
def test_connect_to_rds_error(pg_connect_mock, db_config, all_partners_request):
    response = lambda_handler(all_partners_request, None)
    body = json.loads(response["body"])
    assert response["statusCode"] == 500
    assert body["error"]["message"] == "Connect to RDS error"


@patch("psycopg2.connect")
def test_get_data_from_db_error(pg_connect_mock, db_config, all_partners_request):
    rds_mock = MagicMock()
    pg_connect_mock.return_value = rds_mock
    rds_mock.cursor.side_effect = Exception("Get data from database error")
    response = lambda_handler(all_partners_request, None)
    body = json.loads(response["body"])
    assert response["statusCode"] == 500
    assert body["error"]["message"] == "Database error"
    rds_mock.close.assert_called_once()


@patch("psycopg2.connect")
def test_all_partners_request_success(pg_connect_mock, db_config, all_partners_request):
    mock_pg_fetchall(pg_connect_mock, [])
    response = lambda_handler(all_partners_request, None)
    assert response["statusCode"] == 200


@patch("psycopg2.connect")
def test_single_partner_by_id_request_success(
    pg_connect_mock, db_config, single_partner_by_id_request
):
    mock_pg_fetchall(pg_connect_mock, [])
    response = lambda_handler(single_partner_by_id_request, None)
    assert response["statusCode"] == 200


@patch("psycopg2.connect")
def test_single_partner_by_uuid_request_success(
    pg_connect_mock, db_config, single_partner_by_uuid_request
):
    mock_pg_fetchall(pg_connect_mock, [])
    response = lambda_handler(single_partner_by_uuid_request, None)
    assert response["statusCode"] == 200


@patch("psycopg2.connect")
def test_query_partner_request_success(
    pg_connect_mock, db_config, query_partner_request
):
    mock_pg_fetchall(pg_connect_mock, [])
    response = lambda_handler(query_partner_request, None)
    assert response["statusCode"] == 200

import json
from unittest.mock import patch, MagicMock
from common.test.util import mock_pg_fetchall
from lambda_function import lambda_handler


# Expose Pirate source lambda test
def test_missing_partner_id_request_error(db_config, missing_partner_id_request):
    response = lambda_handler(missing_partner_id_request, None)
    body = json.loads(response["body"])
    assert response["statusCode"] == 400
    assert body["error"]["message"] == "Validate request error"


def test_invalid_partner_id_request_error(db_config, invalid_partner_id_request):
    response = lambda_handler(invalid_partner_id_request, None)
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


def test_invalid_pirate_source_name_and_type_request_error(
    db_config, invalid_pirate_source_name_and_type_request
):
    response = lambda_handler(invalid_pirate_source_name_and_type_request, None)
    body = json.loads(response["body"])
    assert response["statusCode"] == 400
    assert body["error"]["message"] == "Validate request error"


def test_invalid_pirate_source_parameters_combination_request_error(
    db_config, invalid_pirate_source_parameters_combination_request
):
    response = lambda_handler(
        invalid_pirate_source_parameters_combination_request, None
    )
    body = json.loads(response["body"])
    assert response["statusCode"] == 400
    assert body["error"]["message"] == "Validate request error"


@patch("psycopg2.connect", side_effect=Exception("Connect to RDS error"))
def test_connect_to_rds_error(
    pg_connect_mock, db_config, all_pirate_sources_for_partner_request
):
    response = lambda_handler(all_pirate_sources_for_partner_request, None)
    body = json.loads(response["body"])
    assert response["statusCode"] == 500
    assert body["error"]["message"] == "Connect to RDS error"


@patch("psycopg2.connect")
def test_get_data_from_db_error(
    pg_connect_mock, db_config, all_pirate_sources_for_partner_request
):
    rds_mock = MagicMock()
    pg_connect_mock.return_value = rds_mock
    rds_mock.cursor.side_effect = Exception("Get data from database error")
    response = lambda_handler(all_pirate_sources_for_partner_request, None)
    body = json.loads(response["body"])
    assert response["statusCode"] == 500
    assert body["error"]["message"] == "Database error"
    rds_mock.close.assert_called_once()


@patch("psycopg2.connect")
def test_all_products_request_success(
    pg_connect_mock, db_config, all_pirate_sources_for_partner_request
):
    mock_pg_fetchall(pg_connect_mock, [])
    response = lambda_handler(all_pirate_sources_for_partner_request, None)
    assert response["statusCode"] == 200


@patch("psycopg2.connect")
def test_single_pirate_source_request_success(
    pg_connect_mock, db_config, single_pirate_source_request
):
    mock_pg_fetchall(pg_connect_mock, [])
    response = lambda_handler(single_pirate_source_request, None)
    assert response["statusCode"] == 200


@patch("psycopg2.connect")
def test_query_pirate_source_request_success(
    pg_connect_mock, db_config, query_pirate_source_request
):
    mock_pg_fetchall(pg_connect_mock, [])
    response = lambda_handler(query_pirate_source_request, None)
    assert response["statusCode"] == 200

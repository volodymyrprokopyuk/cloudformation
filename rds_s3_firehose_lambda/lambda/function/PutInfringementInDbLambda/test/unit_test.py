from unittest.mock import patch, MagicMock
from pytest import fixture
from lambda_function import lambda_handler
from common.test.util import all_in, create_transform_event


# Configuration fixture
@fixture
def db_config(monkeypatch):
    config = {
        "DB_HOST": "host",
        "DB_PORT": "port",
        "DB_NAME": "name",
        "DB_USER": "user",
        "DB_PASSWORD": "password",
    }
    for key, value in config.items():
        monkeypatch.setenv(key, value)
    return config


# Transform event fixture
@fixture
def invalid_records_above_threshold_event():
    event = create_transform_event(
        "bucket_name", "infringement_invalid_records_above_threshold.txt"
    )
    return event


@fixture
def invalid_records_below_threshold_event():
    event = create_transform_event(
        "bucket_name", "infringement_invalid_records_below_threshold.txt"
    )
    return event


@fixture
def success_event():
    event = create_transform_event("bucket_name", "infringement_success.txt")
    return event


# Transform Infringement lambda test
@patch("os.remove")
@patch("psycopg2.connect")
@patch("boto3.client")
def test_validate_record_error(
    boto3_client_mock,
    pg_connect_mock,
    os_remove_mock,
    db_config,
    invalid_records_above_threshold_event,
    caplog,
):
    lambda_handler(invalid_records_above_threshold_event, None)
    assert all_in(["ERROR", "Validate record"], caplog.text)


@patch("os.remove")
@patch("psycopg2.connect")
@patch("boto3.client")
def test_put_record_in_db_error(
    boto3_client_mock, pg_connect_mock, os_remove_mock, db_config, success_event, caplog
):
    rds_mock = MagicMock()
    rds_mock.cursor.side_effect = Exception("Put record in database error")
    pg_connect_mock.return_value = rds_mock
    lambda_handler(success_event, None)
    assert all_in(["ERROR", "Put record in database"], caplog.text)


@patch("os.remove")
@patch("psycopg2.connect")
@patch("boto3.client")
def test_move_document_to_processed_error(
    boto3_client_mock, pg_connect_mock, os_remove_mock, db_config, success_event, caplog
):
    s3_mock = MagicMock()
    s3_mock.copy_object.side_effect = Exception("Move document to processed error")
    boto3_client_mock.return_value = s3_mock
    lambda_handler(success_event, None)
    assert all_in(
        ["ERROR", "Move document to processed", "INFO", "SUCCESS", "IMPORT_SUCCESS"],
        caplog.text,
    )


@patch("os.remove")
@patch("psycopg2.connect")
@patch("boto3.client")
def test_process_request_with_invalid_records_below_threshold_success(
    boto3_client_mock,
    pg_connect_mock,
    os_remove_mock,
    db_config,
    invalid_records_below_threshold_event,
    caplog,
):
    lambda_handler(invalid_records_below_threshold_event, None)
    assert all_in(["WARNING", "SUCCESS", "FAILED_RECORDS_BELOW_THRESHOLD"], caplog.text)


@patch("os.remove")
@patch("psycopg2.connect")
@patch("boto3.client")
def test_process_request_success(
    boto3_client_mock, pg_connect_mock, os_remove_mock, db_config, success_event, caplog
):
    lambda_handler(success_event, None)
    assert all_in(["INFO", "SUCCESS", "IMPORT_SUCCESS"], caplog.text)

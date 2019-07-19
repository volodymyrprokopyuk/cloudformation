from unittest.mock import patch, MagicMock
from pytest import fixture
from lambda_function import lambda_handler

# Util
def _all_in(messages, log):
    return all([message in log for message in messages])


# Configuration fixtures
@fixture
def invalid_db_config(monkeypatch):
    config = {
        "DB_HOST": "host",
        "DB_PORT": "port",
        "DB_NAME": "name",
        "DB_USER": "user",
    }
    for key, value in config.items():
        monkeypatch.setenv(key, value)
    return config


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


# Event fixtures
def _create_event(bucket_name, object_key):
    event = {
        "Records": [
            {
                "s3": {
                    "bucket": {
                        "name": bucket_name
                    },
                    "object": {
                        "key": object_key
                    },
                }
            }
        ]
    }
    return event


@fixture
def invalid_event():
    event = _create_event("", "")
    return event

@fixture
def non_existing_document_event():
    event = _create_event("bucket_name", "object_key")
    return event


@fixture
def empty_document_event():
    event = _create_event("bucket_name", "product_empty.txt")
    return event


@fixture
def invalid_document_event():
    event = _create_event("bucket_name", "product_invalid.txt")
    return event


@fixture
def invalid_records_above_threshold_event():
    event = _create_event("bucket_name", "product_invalid_records_above_threshold.txt")
    return event


@fixture
def invalid_records_below_threshold_event():
    event = _create_event("bucket_name", "product_invalid_records_below_threshold.txt")
    return event


@fixture
def success_event():
    event = _create_event("bucket_name", "product_success.txt")
    return event


@fixture
def event():
    event = _create_event("bucket_name", "object_key")
    return event


def test_validate_empty_configuration_error(caplog):
    lambda_handler({}, None)
    assert _all_in(["CRITICAL", "Validate configuration"], caplog.text)


def test_validate_invalid_configuration_error(invalid_db_config, caplog):
    lambda_handler({}, None)
    assert _all_in(["CRITICAL", "Validate configuration"], caplog.text)


def test_validate_empty_event_error(db_config, caplog):
    empty_event = {}
    lambda_handler(empty_event, None)
    assert _all_in(["ERROR", "Validate request"], caplog.text)


def test_validate_invalid_event_error(db_config, invalid_event, caplog):
    lambda_handler(invalid_event, None)
    assert _all_in(["ERROR", "Validate request"], caplog.text)


@patch("boto3.client", side_effect=Exception("Create S3 client error"))
def test_create_s3_client_error(boto3_client_mock, db_config, event, caplog):
    lambda_handler(event, None)
    assert _all_in(["CRITICAL", "Create S3 client"], caplog.text)


@patch("psycopg2.connect", side_effect=Exception("Connect to RDS error"))
@patch("boto3.client")
def test_connect_to_rds_error(
    boto3_client_mock, pg_connect_mock, db_config, event, caplog
):
    lambda_handler(event, None)
    assert _all_in(["CRITICAL", "Connect to RDS"], caplog.text)


@patch("psycopg2.connect")
@patch("boto3.client")
def test_download_document_error(
    boto3_client_mock, pg_connect_mock, db_config, event, caplog
):
    s3_mock = MagicMock()
    s3_mock.download_file.side_effect = Exception("Download document error")
    boto3_client_mock.return_value = s3_mock
    lambda_handler(event, None)
    assert _all_in(["ERROR", "Download document"], caplog.text)


@patch("os.remove")
@patch("psycopg2.connect")
@patch("boto3.client")
def test_parse_non_existing_document_error(
    boto3_client_mock, pg_connect_mock, os_remove_mock,
    db_config, non_existing_document_event, caplog,
):
    lambda_handler(non_existing_document_event, None)
    assert _all_in(
        ["ERROR", "Parse document", "No such file or directory"], caplog.text
    )


@patch("os.remove")
@patch("psycopg2.connect")
@patch("boto3.client")
def test_parse_empty_document_error(
    boto3_client_mock, pg_connect_mock, os_remove_mock,
    db_config, empty_document_event, caplog,
):
    lambda_handler(empty_document_event, None)
    assert _all_in(["WARNING", "Empty document", "EMPTY_DOCUMENT"], caplog.text)


@patch("os.remove")
@patch("psycopg2.connect")
@patch("boto3.client")
def test_parse_invalid_document_error(
    boto3_client_mock, pg_connect_mock, os_remove_mock,
    db_config, invalid_document_event, caplog,
):
    lambda_handler(invalid_document_event, None)
    assert _all_in(
        ["ERROR", "Parse record", "Expecting value", "IMPORT_FAILURE"], caplog.text
    )


@patch("os.remove")
@patch("psycopg2.connect")
@patch("boto3.client")
def test_validate_record_error(
    boto3_client_mock, pg_connect_mock, os_remove_mock,
    db_config, invalid_records_above_threshold_event, caplog,
):
    lambda_handler(invalid_records_above_threshold_event, None)
    assert _all_in(["ERROR", "Validate record"], caplog.text)


@patch("os.remove")
@patch("psycopg2.connect")
@patch("boto3.client")
def test_put_product_in_db_error(
    boto3_client_mock, pg_connect_mock, os_remove_mock,
    db_config, success_event, caplog,
):
    rds_mock = MagicMock()
    rds_mock.cursor.side_effect = Exception("Put product in database error")
    pg_connect_mock.return_value = rds_mock
    lambda_handler(success_event, None)
    assert _all_in(["ERROR", "Put record in database"], caplog.text)


@patch("os.remove")
@patch("psycopg2.connect")
@patch("boto3.client")
def test_move_document_to_processed_error(
    boto3_client_mock, pg_connect_mock, os_remove_mock,
    db_config, success_event, caplog,
):
    s3_mock = MagicMock()
    s3_mock.copy_object.side_effect = Exception("Move document to processed error")
    boto3_client_mock.return_value = s3_mock
    lambda_handler(success_event, None)
    assert _all_in([
        "ERROR", "Move document to processed", "INFO", "SUCCESS", "IMPORT_SUCCESS"
    ], caplog.text)


@patch("os.remove")
@patch("psycopg2.connect")
@patch("boto3.client")
def test_process_request_with_invalid_records_below_threshold_success(
    boto3_client_mock, pg_connect_mock, os_remove_mock,
    db_config, invalid_records_below_threshold_event, caplog,
):
    lambda_handler(invalid_records_below_threshold_event, None)
    assert _all_in(["WARNING", "SUCCESS", "FAILED_RECORDS_BELOW_THRESHOLD"], caplog.text)


@patch("os.remove")
@patch("psycopg2.connect")
@patch("boto3.client")
def test_process_request_success(
    boto3_client_mock, pg_connect_mock, os_remove_mock,
    db_config, success_event, caplog,
):
    lambda_handler(success_event, None)
    assert _all_in(["INFO", "SUCCESS", "IMPORT_SUCCESS"], caplog.text)

from unittest.mock import patch
from lambda_function import lambda_handler
from common.test.util import all_in, all_not_in, get_infringement_count


@patch("os.remove")
@patch("boto3.client")
def test_non_existing_product_error(
    boto3_client_mock,
    os_remove_mock,
    success_event,
    rds,
    post_delete_all_from_infringement,
    caplog,
):
    lambda_handler(success_event, None)
    assert all_in(["ERROR", "Put record in database", "IMPORT_FAILURE"], caplog.text)
    infringement_count = get_infringement_count(rds)
    assert infringement_count == 0


@patch("os.remove")
@patch("boto3.client")
def test_import_document_error(
    boto3_client_mock,
    os_remove_mock,
    create_and_delete_product,
    invalid_records_above_threshold_event,
    rds,
    post_delete_all_from_infringement,
    caplog,
):
    lambda_handler(invalid_records_above_threshold_event, None)
    assert all_in(["ERROR", "IMPORT_FAILURE"], caplog.text)
    infringement_count = get_infringement_count(rds)
    assert infringement_count == 2


@patch("os.remove")
@patch("boto3.client")
def test_process_request_success(
    boto3_client_mock,
    os_remove_mock,
    create_and_delete_product,
    success_event,
    rds,
    post_delete_all_from_infringement,
    caplog,
):
    lambda_handler(success_event, None)
    assert all_not_in(["CRITICAL", "ERROR", "WARNING"], caplog.text)
    assert all_in(["INFO", "SUCCESS", "IMPORT_SUCCESS"], caplog.text)
    infringement_count = get_infringement_count(rds)
    assert infringement_count == 2

from unittest.mock import patch, MagicMock
from lambda_function import lambda_handler
from common.test.util import all_in, all_not_in


@patch("boto3.client")
def test_process_request_success(boto3_client_mock, success_event, caplog):
    lambda_handler(success_event, None)
    assert all_not_in(["CRITICAL", "ERROR", "WARNING"], caplog.text)
    assert all_in(["INFO", "SUCCESS", "IMPORT_SUCCESS"], caplog.text)

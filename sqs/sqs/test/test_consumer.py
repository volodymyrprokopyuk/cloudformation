import json
from unittest.mock import MagicMock, patch
from pytest import fixture
from sqs.consumer import sqs_create_consumer


@fixture
def sqs_config():
    sqs_config = {
        "sqs_url": "SQS_URL",
        "sqs_max_message_retries": 3,
        "sqs_receive_message_delay_seconds": 5
    }
    return sqs_config


@fixture
def sqs_message():
    sqs_message = {"name": "Vlad"}
    return sqs_message


@fixture
def sqs_success_response(sqs_message):
    sqs_success_response = {"Messages": [{
        "MessageId": 1,
        "ReceiptHandle": "ReceiptHandle",
        "Body": json.dumps(sqs_message),
        "Attributes": {
            "SentTimestamp": "SentTimestamp",
            "ApproximateReceiveCount": "1"
        }
    }]}
    return sqs_success_response


@patch("boto3.client")
def test_sqs_create_consumer_success(mocked_boto3_client, sqs_config, sqs_success_response):
    mocked_sqs_client = MagicMock()
    mocked_sqs_client.receive_message.return_value = sqs_success_response
    mocked_boto3_client.return_value = mocked_sqs_client
    mocked_sqs_process_message = MagicMock()
    sqs_run_consumer = sqs_create_consumer(sqs_config, mocked_sqs_process_message)
    sqs_message = sqs_run_consumer()
    mocked_boto3_client.assert_called_once_with("sqs")
    mocked_sqs_client.receive_message.assert_called_once()
    sqs_success_message = sqs_success_response["Messages"][0]
    payload = json.loads(sqs_success_message["Body"])
    mocked_sqs_process_message.assert_called_once_with(payload)
    mocked_sqs_client.delete_message.assert_called_once()
    assert sqs_message["meta"]["message_id"] == sqs_success_message["MessageId"]
    assert sqs_message["payload"] == payload

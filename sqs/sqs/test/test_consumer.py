import time
import json
from unittest.mock import MagicMock, patch
from pytest import fixture, raises
from sqs.consumer import sqs_create_consumer


@fixture
def sqs_config():
    sqs_config = {
        "sqs_url": "SQS_URL",
        "sqs_max_message_retries": 3,
        "sqs_receive_message_delay_seconds": 5,
    }
    return sqs_config


@fixture
def sqs_message_payload():
    sqs_message_payload = {"name": "Vlad"}
    return sqs_message_payload


@fixture
def sqs_success_response(sqs_message_payload):
    sqs_response = {
        "Messages": [
            {
                "MessageId": 1,
                "ReceiptHandle": "ReceiptHandle",
                "Body": json.dumps(sqs_message_payload),
                "Attributes": {
                    "SentTimestamp": "SentTimestamp",
                    "ApproximateReceiveCount": "1",
                },
            }
        ]
    }
    return sqs_response


@fixture
def sqs_max_message_retries_exceeded_response(sqs_message_payload):
    sqs_response = {
        "Messages": [
            {
                "MessageId": 1,
                "ReceiptHandle": "ReceiptHandle",
                "Body": json.dumps(sqs_message_payload),
                "Attributes": {
                    "SentTimestamp": "SentTimestamp",
                    "ApproximateReceiveCount": "3",
                },
            }
        ]
    }
    return sqs_response


@fixture
def sqs_empty_response():
    sqs_response = {}
    return sqs_response


@patch("boto3.client")
def test_sqs_create_consumer_success(
    mocked_boto3_client, sqs_config, sqs_success_response
):
    sqs_expected_message = sqs_success_response["Messages"][0]
    sqs_expected_message_payload = json.loads(sqs_expected_message["Body"])
    mocked_sqs_client = MagicMock()
    mocked_sqs_client.receive_message.return_value = sqs_success_response
    mocked_boto3_client.return_value = mocked_sqs_client
    mocked_sqs_process_message = MagicMock()
    sqs_run_consumer = sqs_create_consumer(sqs_config, mocked_sqs_process_message)
    sqs_message = sqs_run_consumer()
    mocked_boto3_client.assert_called_once_with("sqs")
    mocked_sqs_client.receive_message.assert_called_once()
    mocked_sqs_process_message.assert_called_once_with(sqs_expected_message_payload)
    mocked_sqs_client.delete_message.assert_called_once()
    assert sqs_message["payload"] == sqs_expected_message_payload
    assert sqs_message["meta"]["message_id"] == sqs_expected_message["MessageId"]


@patch("boto3.client")
def test_sqs_create_consumer_max_message_retries_exceeded_failure(
    mocked_boto3_client, sqs_config, sqs_max_message_retries_exceeded_response
):
    sqs_expected_message = sqs_max_message_retries_exceeded_response["Messages"][0]
    sqs_expected_message_payload = json.loads(sqs_expected_message["Body"])
    mocked_sqs_client = MagicMock()
    mocked_sqs_client.receive_message.return_value = (
        sqs_max_message_retries_exceeded_response
    )
    mocked_boto3_client.return_value = mocked_sqs_client
    mocked_sqs_process_message = MagicMock()
    mocked_sqs_process_message.side_effect = Exception("SQS process message failure")
    sqs_run_consumer = sqs_create_consumer(sqs_config, mocked_sqs_process_message)
    with raises(Exception) as error:
        sqs_run_consumer()
    assert error.match("SQS process message failure")
    mocked_boto3_client.assert_called_once_with("sqs")
    mocked_sqs_client.receive_message.assert_called_once()
    mocked_sqs_process_message.assert_called_once_with(sqs_expected_message_payload)
    mocked_sqs_client.delete_message.assert_called_once()


@patch("boto3.client")
def test_sqs_create_consumer_receive_message_delay(
    mocked_boto3_client, sqs_config, sqs_empty_response, sqs_success_response
):
    sqs_expected_message = sqs_success_response["Messages"][0]
    sqs_expected_message_payload = json.loads(sqs_expected_message["Body"])
    mocked_sqs_client = MagicMock()
    mocked_sqs_client.receive_message.side_effect = [
        sqs_empty_response,
        sqs_success_response,
        sqs_success_response,
    ]
    mocked_boto3_client.return_value = mocked_sqs_client
    mocked_sqs_process_message = MagicMock()
    sqs_run_consumer = sqs_create_consumer(sqs_config, mocked_sqs_process_message)

    # First SQS.ReceiveMessage call
    sqs_message = sqs_run_consumer()
    mocked_boto3_client.assert_called_once_with("sqs")
    mocked_sqs_client.receive_message.assert_called_once()
    assert not mocked_sqs_process_message.called
    assert not mocked_sqs_client.delete_message.called
    assert sqs_message is None

    # Second SQS.ReceiveMessage call
    start_ts = time.time()
    sqs_message = sqs_run_consumer()
    stop_ts = time.time()
    assert stop_ts - start_ts >= sqs_config["sqs_receive_message_delay_seconds"]
    assert mocked_sqs_client.receive_message.call_count == 2
    mocked_sqs_process_message.assert_called_once_with(sqs_expected_message_payload)
    mocked_sqs_client.delete_message.assert_called_once()
    assert sqs_message["payload"] == sqs_expected_message_payload
    assert sqs_message["meta"]["message_id"] == sqs_expected_message["MessageId"]

    # Third SQS.ReceiveMessage call
    start_ts = time.time()
    sqs_message = sqs_run_consumer()
    stop_ts = time.time()
    assert stop_ts - start_ts < sqs_config["sqs_receive_message_delay_seconds"]
    assert mocked_sqs_client.receive_message.call_count == 3
    mocked_sqs_process_message.call_count == 2
    mocked_sqs_client.delete_message.call_count == 2
    assert sqs_message["payload"] == sqs_expected_message_payload
    assert sqs_message["meta"]["message_id"] == sqs_expected_message["MessageId"]

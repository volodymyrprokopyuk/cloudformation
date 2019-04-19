import json
from unittest.mock import MagicMock, patch
from pytest import fixture
from sqs.producer import sqs_send_message


@fixture
def sqs_message_payload():
    sqs_message_payload = {"name": "Vlad"}
    return sqs_message_payload


@fixture
def sqs_success_response():
    sqs_response = {"MessageId": 1}
    return sqs_response


@patch("boto3.client")
def test_sqs_send_message_success(mocked_boto3_client, sqs_message_payload, sqs_success_response):
    expected_message_id = sqs_success_response["MessageId"]
    mocked_sqs_client = MagicMock()
    mocked_sqs_client.send_message.return_value = sqs_success_response
    mocked_boto3_client.return_value = mocked_sqs_client
    message_id = sqs_send_message("SQS_URL", sqs_message_payload)
    mocked_boto3_client.assert_called_once_with("sqs")
    mocked_sqs_client.send_message.assert_called_once_with(
        QueueUrl="SQS_URL", MessageBody=json.dumps(sqs_message_payload)
    )
    assert message_id == expected_message_id

import json
from unittest.mock import MagicMock, patch
from pytest import fixture
from sqs.producer import sqs_send_message


@fixture
def sqs_message():
    sqs_message = {"name": "Vlad"}
    return sqs_message


@patch("boto3.client")
def test_sqs_send_message_success(mocked_boto3_client, sqs_message):
    mocked_sqs_client = MagicMock()
    mocked_sqs_client.send_message.return_value = {"MessageId": 1}
    mocked_boto3_client.return_value = mocked_sqs_client
    message_id = sqs_send_message("SQS_URL", sqs_message)
    mocked_boto3_client.assert_called_once_with("sqs")
    mocked_sqs_client.send_message.assert_called_once_with(QueueUrl="SQS_URL", MessageBody=json.dumps(sqs_message))
    assert message_id == 1

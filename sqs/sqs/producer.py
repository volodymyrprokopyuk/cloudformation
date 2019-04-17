"""SQS message producer using SQS.SendMessage"""
import json
import boto3


SQS_URL = "https://sqs.eu-central-1.amazonaws.com/059870358805/Vlad-Queue"


def sqs_send_message(sqs_url, message):
    """
        Send the SQS `message` to the SQS queue identified by the `sqs_url`
        Return SQS MessageId
    """
    sqs = boto3.client("sqs")
    response = sqs.send_message(QueueUrl=sqs_url, MessageBody=json.dumps(message))
    message_id = response["MessageId"]
    return message_id


def main():
    """Send SQS message"""
    message = {"name": "Vlad"}
    message_id = sqs_send_message(SQS_URL, message)
    print(f">> SQS message {message} sent. MessageId: {message_id}")


if __name__ == "__main__":
    main()

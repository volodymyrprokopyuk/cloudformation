"""SQS message consumer using SQS.ReceiveMessage and SQS.DeleteMessage"""
import json
import boto3


SQS_URL = "https://sqs.eu-central-1.amazonaws.com/059870358805/Vlad-Queue"


def sqs_receive_and_delete_message(sqs_url):
    """
        Receive an SQS message from the SQS queue identified by the `sqs_url`.
        Delete the SQS message after successfull processing
    """
    sqs = boto3.client("sqs")
    response = sqs.receive_message(QueueUrl=sqs_url, MaxNumberOfMessages=1, AttributeNames=["SentTimestamp"])
    if response.get("Messages") and response["Messages"]:
        sqs_message = response["Messages"][0]
        message_id = sqs_message["MessageId"]
        receipt_handle = sqs_message["ReceiptHandle"]
        payload = json.loads(sqs_message["Body"])
        sent_timestamp = sqs_message["Attributes"]["SentTimestamp"]
        receive_count = sqs_message["Attributes"]["ApproximateReceiveCount"]
        # Process SQS message before deleting it from the queue
        # On SQS message processing failure
        #     if receive_count > SQS_MAX_MESSAGE_RETRIES:
        #         sqs.delete_message(QueueUrl=SQS_URL, ReceiptHandle=receipt_handle)
        # On SQS message processing success
        sqs.delete_message(QueueUrl=SQS_URL, ReceiptHandle=receipt_handle)
        message = {"payload": payload, "meta": {"message_id": message_id, "sent_timestamp": sent_timestamp}}
        return message
    return None


def main():
    """Receive and delete SQS message"""
    message = sqs_receive_and_delete_message(SQS_URL)
    if message:
        print(f"<< SQS message {message} received")
    else:
        print("<< SQS empty response")


main()

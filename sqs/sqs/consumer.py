"""SQS message consumer using SQS.ReceiveMessage and SQS.DeleteMessage"""
import json
from time import sleep
import boto3


SQS_URL = "https://sqs.eu-central-1.amazonaws.com/059870358805/Vlad-Queue"
SQS_MAX_MESSAGE_RETRIES = 3
SQS_RECEIVE_MESSAGE_DELAY_SECONDS = 5


def sqs_create_consumer(sqs_config, sqs_process_message):
    """
        Create SQS consumer configured with `sqs_config` for processing SQS messages using `sqs_process_message`
        function. The function delays the next SQS.ReceiveMessage call by `sqs_config.sqs_receive_message_delay_seconds`
        if the previos call returnted an empty response. The function deletes the message on failure when the
        `sqs_config.sqs_max_message_retries` has been exceeded

        Input
            - sqs_config
                - sqs_url
                - sqs_max_message_retries
                - sqs_receive_message_delay_seconds
            - sqs_process_message(message) - function that processes an SQS message

        Output
            - On receving SQS message from a queue the function returns the SQS message in a format
                - payload - SQS message JSON
                - meta.message_id
                - meta.sent_timestamp
                - meta.receive_count
            - On empty reponse from a queue the function returns None
    """
    sqs = boto3.client("sqs")
    # The is no empty reponse initial
    sqs_was_empty_response = False

    def sqs_consumer():
        nonlocal sqs_was_empty_response
        if sqs_was_empty_response:
            # Delay the next SQS.ReceiveMessage call if the previos call returned an empty response
            sleep(sqs_config.sqs_receive_message_delay_seconds)
            sqs_was_empty_response = False
        # Perform the SQS.ReceiveMessage call
        response = sqs.receive_message(
            QueueUrl=sqs_config["sqs_url"], MaxNumberOfMessages=1,
            AttributeNames=["SentTimestamp", "ApproximateReceiveCount"]
        )
        # Check whether the SQS response is not empty
        if response.get("Messages") and response["Messages"]:
            # Retrieve the first SQS message
            sqs_message = response["Messages"][0]
            message_id = sqs_message["MessageId"]
            receipt_handle = sqs_message["ReceiptHandle"]
            payload = json.loads(sqs_message["Body"])
            sent_timestamp = sqs_message["Attributes"]["SentTimestamp"]
            receive_count = sqs_message["Attributes"]["ApproximateReceiveCount"]
            try:
                # Process the SQS message
                sqs_process_message(payload)
                # Delete the SQS message after succesfull processing
                sqs.delete_message(QueueUrl=sqs_config["sqs_url"], ReceiptHandle=receipt_handle)
            except Exception as error:
                if receive_count > sqs_config["sqs_max_message_retries"]:
                    # Delete the SQS message on SQS message processing failure if the the
                    # `sqs_config.sqs_max_message_retries` has been exceeded
                    sqs.delete_message(QueueUrl=sqs_config.sqs_url, ReceiptHandle=receipt_handle)
                raise error
            # Format the SQS message paload along with metadata to be returned to the caller
            message = {"payload": payload, "meta": {
                "message_id": message_id, "sent_timestamp": sent_timestamp, "receive_count": receive_count
            }}
            return message
        # The SQS response is empty
        sqs_was_empty_response = True
        return None

    # Return SQS consumer configured closure
    return sqs_consumer


def sqs_process_message(message):
    """Process SQS message"""
    print(f"* Processing message {message}")


def main():
    """Receive, process, and delete SQS message"""
    sqs_config = {
        "sqs_url": SQS_URL,
        "sqs_max_message_retries": SQS_MAX_MESSAGE_RETRIES,
        "sqs_receive_message_delay_seconds": SQS_RECEIVE_MESSAGE_DELAY_SECONDS
    }
    # Create SQS consumer to process SQS messages
    sqs_run_consumer = sqs_create_consumer(sqs_config, sqs_process_message)
    # Receive, process, and delete SQS message
    sqs_message = sqs_run_consumer()
    if sqs_message:
        print(f"<< SQS message {sqs_message} received")
    else:
        print("<< SQS empty response")


if __name__ == "__main__":
    main()

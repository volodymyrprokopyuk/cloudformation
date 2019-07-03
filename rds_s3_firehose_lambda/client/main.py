"""Send product and infringement files to Kinesis Firehose delivery streams"""
import os
import sys
import boto3


def _validate_request():
    errors = []
    # Check command line agruments
    if len(sys.argv) != 3 or sys.argv[1] not in ("-p", "-i"):
        errors.append(
            "Usage: python main.py {-p <product file> | -i <infringment file>}"
        )
    envs = [
        "FIREHOSE_PRODUCT_DELIVERY_STREAM_NAME",
        "FIREHOSE_INFRINGEMENT_DELIVERY_STREAM_NAME",
    ]
    # Check environment variables
    for env in envs:
        if not os.getenv(env):
            errors.append(f"Mandatory {env} environment variable is not provided")
    return errors


def _prepare_request():
    request = {}
    # Kinesis Firehose delivery stream names configuration
    delivery_streams = {
        "-p": os.getenv("FIREHOSE_PRODUCT_DELIVERY_STREAM_NAME"),
        "-i": os.getenv("FIREHOSE_INFRINGEMENT_DELIVERY_STREAM_NAME"),
    }
    # Get Kinesis Firehose delivery stream name corresponding to the type of the data
    # file to send to the Kinesis Firehose delivery stream
    request["stream_name"] = delivery_streams[sys.argv[1]]
    # Get the name of the data file to send to the Kinesis Firehose delivery stream
    request["data_file"] = sys.argv[2]
    return request


def send_file_to_delivery_stream(data_file, stream_name):
    """
    Send data_file to AWS Kinesis Firehose delivery stream identified by stream_name
    """
    with open(data_file) as opened_file:
        # Parse records in the data file. Each record in the data file is a one-line
        # valid JSON with all record attributes. Each record in the data file is
        # delimited by a new line (\n) character
        raw_records = opened_file.read().strip().split("\n")
        # Format each record in a required by Kinesis Firehose data structure
        # Separate each record with a new line (\n) character
        records = [{"Data": f"{raw_record}\n"} for raw_record in raw_records]
        # Create a Kinesis Firehose client
        firehose = boto3.client("firehose")
        # Send the formatted records to the appropriate Kinesis Firehose delivery stream
        response = firehose.put_record_batch(
            DeliveryStreamName=stream_name, Records=records
        )
        print(f"Failed records count: {response['FailedPutCount']}")


def main():
    """Send product and infringement files to Kinesis Firehose delivery streams"""
    # Validate command line arguments and environment variables
    errors = _validate_request()
    if errors:
        print(f"ERROR: request validation: {errors}")
        exit(1)
    # Prepare data file and Kinesis Firehose delivery stream name
    request = _prepare_request()
    # Send data file to Kinesis Firehose delivery stream
    send_file_to_delivery_stream(request["data_file"], request["stream_name"])


if __name__ == "__main__":
    main()

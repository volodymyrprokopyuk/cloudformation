"""Send product and infringement files to Kinesis Firehose delivery streams"""
import os
import sys
import time
import boto3


RECORD_SET_SIZE = 500


def _validate_request():
    errors = []
    # Check command line agruments
    if len(sys.argv) != 3 or sys.argv[1] not in ("--product", "--infringement"):
        errors.append(
            "Usage: python main.py {--product <product file>"
            + " | --infringement <infringment file>}"
        )
    envs = ["PRODUCT_DELIVERY_STREAM_NAME", "INFRINGEMENT_DELIVERY_STREAM_NAME"]
    # Check environment variables
    for env in envs:
        if not os.getenv(env):
            errors.append(f"Mandatory {env} environment variable is not provided")
    return errors


def _parse_request():
    request = {}
    # Kinesis Firehose delivery stream names configuration
    delivery_streams = {
        "--product": os.getenv("PRODUCT_DELIVERY_STREAM_NAME"),
        "--infringement": os.getenv("INFRINGEMENT_DELIVERY_STREAM_NAME"),
    }
    # Get Kinesis Firehose delivery stream name corresponding to the type of the data
    # file to send to the Kinesis Firehose delivery stream
    request["stream_name"] = delivery_streams[sys.argv[1]]
    # Get the name of the data file to send to the Kinesis Firehose delivery stream
    request["data_file"] = sys.argv[2]
    return request


def _read_data_file(data_file):
    with open(data_file) as opened_file:
        # Parse records in the data file. Each record in the data file is a one-line
        # valid JSON with all record attributes. Each record in the data file is
        # delimited by a new line (\n) character
        raw_records = opened_file.read().strip().split("\n")
        return raw_records


def _split_records_into_record_sets(raw_records, record_set_size):
    # Format each record in a required by Kinesis Firehose data structure
    # Separate each record with a new line (\n) character
    records = [{"Data": f"{raw_record}\n"} for raw_record in raw_records]
    # Split raw racords into record sets of specified size to satisfy
    # Kinesis Firehose maximum number of records per request constraint
    record_sets = [
        records[start_index : start_index + record_set_size]  # noqa: E203
        for start_index in range(0, len(records), record_set_size)
    ]
    return record_sets


def _put_record_set_to_firehose(firehose, stream_name, record_set):
    try:
        # Send the formatted records split into record sets
        # to the appropriate Kinesis Firehose delivery stream
        response = firehose.put_record_batch(
            DeliveryStreamName=stream_name, Records=record_set
        )
        failed_records_count = response["FailedPutCount"]
        print(f"Failed records count: {failed_records_count}")
        if failed_records_count:
            unique_error_messages = {
                error["ErrorMessage"] for error in response["RequestResponses"]
            }
            print(f"Failed records reasons: {unique_error_messages}")
    except Exception as error:
        print(f"ERROR: send data to firehose: {error}")


def put_file_to_firehose(data_file, stream_name):
    """
    Send data_file to AWS Kinesis Firehose delivery stream identified by stream_name
    """
    raw_records = _read_data_file(data_file)
    record_sets = _split_records_into_record_sets(raw_records, RECORD_SET_SIZE)
    # Create a Kinesis Firehose client
    firehose = boto3.client("firehose")
    for record_set in record_sets:
        _put_record_set_to_firehose(firehose, stream_name, record_set)
        time.sleep(0.5)


def main():
    """Send product and infringement files to Kinesis Firehose delivery streams"""
    # Validate command line arguments and environment variables
    errors = _validate_request()
    if errors:
        print(f"ERROR: Request validation: {errors}")
        exit(1)
    # Prepare data file and Kinesis Firehose delivery stream name
    request = _parse_request()
    # Send data file to Kinesis Firehose delivery stream
    put_file_to_firehose(request["data_file"], request["stream_name"])


if __name__ == "__main__":
    main()

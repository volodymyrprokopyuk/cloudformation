"""Send product and infringement files to AWS Kinesis Firehose delivery streams"""
import sys
import boto3

USAGE = "Usage: python main.py {-p <product file> | -i <infringment file>}"


# Kinesis Firehose delivery stream names configuration
FIREHOSE_STREAMS = {"-p": "ProductDeliveryStream", "-i": "InfringementDeliveryStream"}


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
    """Send product and infringement files to AWS Kinesis Firehose delivery streams"""
    if len(sys.argv) != 3 or sys.argv[1] not in ("-p", "-i"):
        print(USAGE)
        exit(1)
    # Get Kinesis Firehose delivery stream name corresponding to the type of the data
    # file to send to the Kinesis Firehose delivery stream
    stream_name = FIREHOSE_STREAMS[sys.argv[1]]
    # Get the name of the data file to send to the Kinesis Firehose delivery stream
    data_file = sys.argv[2]
    # Send data file to Kinesis Firehose delivery stream
    send_file_to_delivery_stream(data_file, stream_name)


if __name__ == "__main__":
    main()

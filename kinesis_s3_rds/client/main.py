"""Upload product and infringement files to AWS Kinesis Firehose delivery streams"""
import sys
import boto3

USAGE = "Usage: python main.py {-p <product file> | -i <infringment file>}"


FIREHOSE_STREAMS = {"-p": "ProductDeliveryStream", "-i": "InfringementDeliveryStream"}


def upload_file(input_file, stream_name):
    """Upload input_file to AWS Kinesis Firehose delivery stream with stream_name"""
    with open(input_file) as opened_file:
        raw_records = opened_file.read().strip().split("\n")
        records = [{"Data": f"{raw_record}\n"} for raw_record in raw_records]
        firehose = boto3.client("firehose")
        response = firehose.put_record_batch(
            DeliveryStreamName=stream_name, Records=records
        )
        print(f"Failed records count: {response['FailedPutCount']}")


def main():
    """Upload product and infringement files to AWS Kinesis Firehose delivery streams"""
    if len(sys.argv) != 3 or sys.argv[1] not in ("-p", "-i"):
        print(USAGE)
        exit(1)
    stream_name = FIREHOSE_STREAMS[sys.argv[1]]
    input_file = sys.argv[2]
    upload_file(input_file, stream_name)


if __name__ == "__main__":
    main()

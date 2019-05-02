"""Retrieve EC2 instance identity document and store it in S3"""
import json
import requests
import boto3


EC2_METADATA_URL = "http://169.254.169.254/latest/dynamic/instance-identity/document"
S3_BUCKET_NAME = "vlad-stack-ec2-metadata"
S3_OBJECT_KEY = "ec2/instance_identity_document.json"


def get_instance_identity_document(url):
    """Retrieve EC2 instance identity document from EC2 metadata local link URL"""
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def store_instance_identity_document(bucket, key, body):
    """Store EC2 instance identity document in S3"""
    s3 = boto3.client("s3")
    s3.put_object(Bucket=bucket, Key=key, Body=body)


def main():
    """Retrieve EC2 instance identity document and store it in S3"""
    document = get_instance_identity_document(EC2_METADATA_URL)
    store_instance_identity_document(
        S3_BUCKET_NAME, S3_OBJECT_KEY, json.dumps(document, indent=4)
    )


if __name__ == "__main__":
    main()

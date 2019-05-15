"""Log and publish metrics to CloudWatch"""
# import json
# import requests
# import boto3
from jsonlogging import with_logger


EC2_METADATA_URL = "http://169.254.169.254/latest/dynamic/instance-identity/document"


@with_logger(__name__)
def main(logger):
    """Log and publish metrics to CloudWatch"""
    logger.setLevel("DEBUG")
    logger.info("ok")


if __name__ == "__main__":
    main()

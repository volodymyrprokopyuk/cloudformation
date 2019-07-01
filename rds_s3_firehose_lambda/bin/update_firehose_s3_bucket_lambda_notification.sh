#!/usr/bin/env bash

set -eux

source ./bin/config.sh

readonly FIREHOSE_S3_BUCKET_LAMBDA_NOTIFICATION_FILE=$(pwd)/cloudformation/firehose_s3_bucket_lambda_notification.json
readonly S3_FIREHOSE_DELIVERY_STREAM_BUCKET_NAME=infringement-ingest-firehose-delivery-stream

aws s3api put-bucket-notification-configuration \
    --bucket $S3_FIREHOSE_DELIVERY_STREAM_BUCKET_NAME \
    --notification-configuration file://$FIREHOSE_S3_BUCKET_LAMBDA_NOTIFICATION_FILE

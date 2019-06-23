#!/usr/bin/env bash

set -eux

source ./bin/config.sh

readonly S3_FIREHOSE_BUCKET_NOTIFICATION_CONFIGURATION_FILE=$(pwd)/cloudformation/firehose_s3_bucket_notification_configuration.json

aws s3api put-bucket-notification-configuration \
    --bucket $S3_FIREHOSE_DELIVERY_STREAM_BUCKET_NAME \
    --notification-configuration file://$S3_FIREHOSE_BUCKET_NOTIFICATION_CONFIGURATION_FILE

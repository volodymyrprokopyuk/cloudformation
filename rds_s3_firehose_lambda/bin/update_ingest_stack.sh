#!/usr/bin/env bash

set -eux

source ./bin/config.sh

readonly S3_FIREHOSE_DELIVERY_STREAM_BUCKET_NAME=infringement-ingest-firehose-delivery-stream
# Get data transform Lambda ARNs from CloudFormation Exports
readonly LAMBDA_PUT_PRODUCT_IN_DB_ARN=$(aws cloudformation list-exports \
    | jq -r '.Exports[] | select(.Name | contains("PutProductInDbLambdaArn")).Value')
readonly LAMBDA_PUT_INFRINGEMENT_IN_DB_ARN=$(aws cloudformation list-exports \
    | jq -r '.Exports[] | select(.Name | contains("PutInfringementInDbLambdaArn")).Value')
readonly S3_BUCKET_LAMBDA_NOTIFICATION_FILE=s3_bucket_lambda_notification.json

# Create Kinesis Firehose delivery stream S3 bucket Lambda notification JSON
cat > $S3_BUCKET_LAMBDA_NOTIFICATION_FILE <<EOF
{
    "LambdaFunctionConfigurations": [
        {
            "Events": ["s3:ObjectCreated:*"],
            "Filter": {"Key": {"FilterRules": [{"Name": "prefix", "Value": "product/"}]}},
            "LambdaFunctionArn": "$LAMBDA_PUT_PRODUCT_IN_DB_ARN"
        },
        {
            "Events": ["s3:ObjectCreated:*"],
            "Filter": {"Key": {"FilterRules": [{"Name": "prefix", "Value": "infringement/"}]}},
            "LambdaFunctionArn": "$LAMBDA_PUT_INFRINGEMENT_IN_DB_ARN"
        }
    ]
}
EOF

set +e

# Update Kinesis Firehose delivery stream S3 bucket Lambda notification
aws s3api put-bucket-notification-configuration \
    --bucket $S3_FIREHOSE_DELIVERY_STREAM_BUCKET_NAME \
    --notification-configuration file://$S3_BUCKET_LAMBDA_NOTIFICATION_FILE

# Remove Kinesis Firehose delivery stream S3 bucket Lambda notification JSON
rm -f $S3_BUCKET_LAMBDA_NOTIFICATION_FILE

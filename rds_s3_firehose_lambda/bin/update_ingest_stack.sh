#!/usr/bin/env bash

source ./bin/config.sh
source ./bin/util.sh

set $SETOPTS

# Compose Kinesis Firehose infringement delivery bucket name
readonly STACK_NAME=$APPLICATION-ingest-$ENVIRONMENT
readonly LOWER_STACK_NAME=$(echo $STACK_NAME | tr '[:upper:]' '[:lower:]')
readonly S3_INFRINGEMENT_DELIVERY_BUCKET_NAME=$LOWER_STACK_NAME-$S3_INFRINGEMENT_DELIVERY_BUCKET_SUFFIX

# Get PutProductInDb transform Lambda ARN from the CloudFormation Exports
LAMBDA_PUT_PRODUCT_IN_DB_ARN_EXPORT_NAME=$APPLICATION-transform-$ENVIRONMENT:PutProductInDbLambdaArn
readonly LAMBDA_PUT_PRODUCT_IN_DB_ARN=$(
    get_cf_export_value $LAMBDA_PUT_PRODUCT_IN_DB_ARN_EXPORT_NAME
)

# Get PutInfringementInDb transform Lambda ARN from the CloudFormation Exports
LAMBDA_PUT_INFRINGEMENT_IN_DB_ARN_EXPORT_NAME=$APPLICATION-transform-$ENVIRONMENT:PutInfringementInDbLambdaArn
readonly LAMBDA_PUT_INFRINGEMENT_IN_DB_ARN=$(
    get_cf_export_value $LAMBDA_PUT_INFRINGEMENT_IN_DB_ARN_EXPORT_NAME
)

# Create S3 bucket Lambda notification JSON for the Kinesis Firehose infringement
# delivery streams
readonly S3_BUCKET_LAMBDA_NOTIFICATION_JSON=s3_bucket_lambda_notification.json
cat > $S3_BUCKET_LAMBDA_NOTIFICATION_JSON <<EOF
{
    "LambdaFunctionConfigurations": [
        {
            "Events": ["s3:ObjectCreated:*"],
            "Filter": {"Key": {"FilterRules": [{"Name": "prefix", "Value": "product/"}]}},
            "LambdaFunctionArn": "${LAMBDA_PUT_PRODUCT_IN_DB_ARN}"
        },
        {
            "Events": ["s3:ObjectCreated:*"],
            "Filter": {"Key": {"FilterRules": [{"Name": "prefix", "Value": "infringement/"}]}},
            "LambdaFunctionArn": "${LAMBDA_PUT_INFRINGEMENT_IN_DB_ARN}"
        }
    ]
}
EOF

set +e

# Update the Kinesis Firehose infringement delivery stream S3 bucket Lambda notification
aws s3api put-bucket-notification-configuration \
    --bucket $S3_INFRINGEMENT_DELIVERY_BUCKET_NAME \
    --notification-configuration file://$S3_BUCKET_LAMBDA_NOTIFICATION_JSON

# Remove the Kinesis Firehose delivery stream S3 bucket Lambda notification JSON
rm -f $S3_BUCKET_LAMBDA_NOTIFICATION_JSON

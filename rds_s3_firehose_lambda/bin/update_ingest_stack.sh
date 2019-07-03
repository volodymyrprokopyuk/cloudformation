#!/usr/bin/env bash

set -eux

source ./bin/config.sh
source ./bin/util.sh

# Compose Kinesis Firehose infringement delivery bucket name
readonly STACK_NAME=$APPLICATION-ingest-$ENVIRONMENT
readonly LOWER_STACK_NAME=$(echo $STACK_NAME | tr '[:upper:]' '[:lower:]')
readonly S3_FIREHOSE_INFRINGEMENT_DELIVERY_BUCKET_NAME=$LOWER_STACK_NAME-$S3_FIREHOSE_INFRINGEMENT_DELIVERY_BUCKET_SUFFIX

# Get PutProductInDb transform Lambda ARNs from the CloudFormation Exports
LAMBDA_PUT_PRODUCT_IN_DB_ARN_EXPORT_NAME=$APPLICATION-transform-$ENVIRONMENT:PutProductInDbLambdaArn
readonly LAMBDA_PUT_PRODUCT_IN_DB_ARN=$(
    get_cf_export_value $LAMBDA_PUT_PRODUCT_IN_DB_ARN_EXPORT_NAME
)
LAMBDA_PUT_INFRINGEMENT_IN_DB_ARN_EXPORT_NAME=$APPLICATION-transform-$ENVIRONMENT:PutInfringementInDbLambdaArn

# Get PutInfringementInDb transform Lambda ARNs from the CloudFormation Exports
readonly LAMBDA_PUT_INFRINGEMENT_IN_DB_ARN=$(
    get_cf_export_value $LAMBDA_PUT_INFRINGEMENT_IN_DB_ARN_EXPORT_NAME
)

# Create the Kinesis Firehose delivery stream S3 bucket Lambda notification JSON
readonly S3_BUCKET_LAMBDA_NOTIFICATION_JSON=s3_bucket_lambda_notification.json
cat > $S3_BUCKET_LAMBDA_NOTIFICATION_JSON <<EOF
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

Update the Kinesis Firehose delivery stream S3 bucket Lambda notification
aws s3api put-bucket-notification-configuration \
    --bucket $S3_FIREHOSE_INFRINGEMENT_DELIVERY_BUCKET_NAME \
    --notification-configuration file://$S3_BUCKET_LAMBDA_NOTIFICATION_JSON

# Remove the Kinesis Firehose delivery stream S3 bucket Lambda notification JSON
rm -f $S3_BUCKET_LAMBDA_NOTIFICATION_JSON

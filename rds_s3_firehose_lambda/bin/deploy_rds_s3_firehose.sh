#!/usr/bin/env bash

set -ex

source ./bin/config.sh

CF_STACK_ACTION=update-stack
if [[ $1 == -c ]]; then
    CF_STACK_ACTION=create-stack
fi

# Create [-c] or update CloudFormation stack
aws cloudformation $CF_STACK_ACTION --stack-name $CF_STACK_NAME \
    --template-body file://$CF_RDS_S3_FIREHOSE_TEMPLATE \
    --parameters \
    ParameterKey=DbPort,ParameterValue=$DB_PORT \
    ParameterKey=DbName,ParameterValue=$DB_NAME \
    ParameterKey=DbUser,ParameterValue=$DB_USER \
    ParameterKey=DbPassword,ParameterValue=$DB_PASSWORD \
    ParameterKey=FirehoseDeliveryStreamS3BucketName,ParameterValue=$S3_FIREHOSE_DELIVERY_STREAM_BUCKET_NAME \
    ParameterKey=LambdaPackageS3BucketName,ParameterValue=$S3_LAMBDA_PACKAGE_BUCKET_NAME \
    --capabilities CAPABILITY_NAMED_IAM

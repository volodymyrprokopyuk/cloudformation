#!/usr/bin/env bash

set -ex

source ./bin/config.sh

CF_STACK_ACTION=update-stack
if [[ $1 == -c ]]; then
    CF_STACK_ACTION=create-stack
fi

# Create [-c] or update CloudFormation stack
aws cloudformation $CF_STACK_ACTION --stack-name $CF_STACK_NAME \
    --template-body file://$CF_TEMPLATE \
    --parameters \
    ParameterKey=DbPort,ParameterValue=$DB_PORT \
    ParameterKey=DbName,ParameterValue=$DB_NAME \
    ParameterKey=DbUser,ParameterValue=$DB_USER \
    ParameterKey=DbPassword,ParameterValue=$DB_PASSWORD \
    ParameterKey=FirehoseDeliveryStreamS3BucketName,ParameterValue=$S3_FIREHOSE_DELIVERY_STREAM_BUCKET_NAME \
    ParameterKey=LambdaPackageS3BucketName,ParameterValue=$S3_LAMBDA_PACKAGE_BUCKET_NAME \
    ParameterKey=PutProductInDbLambdaVersion,ParameterValue=$LAMBDA_PUT_PRODUCT_IN_DB_VERSION \
    ParameterKey=PutInfringementInDbLambdaVersion,ParameterValue=$LAMBDA_PUT_INFRINGEMENT_IN_DB_VERSION \
    ParameterKey=LambdaLogLevel,ParameterValue=$LAMBDA_LOG_LEVEL \
    --capabilities CAPABILITY_NAMED_IAM

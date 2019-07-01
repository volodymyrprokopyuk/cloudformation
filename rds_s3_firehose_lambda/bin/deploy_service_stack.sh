#!/usr/bin/env bash

set -x

source ./bin/config.sh

read -d "" USAGE <<EOF
Usage:
    ./bin/deploy_service_stack target [-c]"
Target:
    infringement-ingest - deploy Kinesis Firehose delivery streams and S3 bucket
    infringement-transform - deploy data transformation Lambdas
    infringement-store - deploy PostgreSQL RDS
    infringement-expose - deploy API Gateway with backed by endpoint Lambdas
Options:
    -c create stack, if -c is omitted then update stack
EOF

readonly APPLICATION=infringement
readonly CF_DIR=$(pwd)/cloudformation

function deploy_infringement_ingest_stack {
    local stack_action=${1?ERROR: mandatory CloudFormation stack action is not provided}
    local stack_template=$CF_DIR/infringement_ingest.yaml
    local service=ingest
    local stack_name=$APPLICATION-$service
    local firehose_delivery_stream_s3_bucket_name=${stack_name}-firehose-delivery-stream

    aws cloudformation $stack_action --stack-name $stack_name \
        --template-body file://$stack_template \
        --parameters \
        ParameterKey=FirehoseDeliveryStreamS3BucketName,ParameterValue=$firehose_delivery_stream_s3_bucket_name \
        --capabilities CAPABILITY_NAMED_IAM
}

function deploy_infringement_transform_stack {
    local stack_action=${1?ERROR: mandatory CloudFormation stack action is not provided}
    local stack_template=$CF_DIR/infringement_transform.yaml
    local service=transform
    local stack_name=$APPLICATION-$service

    aws cloudformation $stack_action --stack-name $stack_name \
        --template-body file://$stack_template \
        --parameters \
        ParameterKey=DbName,ParameterValue=$DB_NAME \
        ParameterKey=DbUser,ParameterValue=$DB_USER \
        ParameterKey=DbPassword,ParameterValue=$DB_PASSWORD \
        ParameterKey=LambdaPackageS3BucketName,ParameterValue=$S3_LAMBDA_PACKAGE_BUCKET_NAME \
        ParameterKey=PutProductInDbLambdaVersion,ParameterValue=$LAMBDA_PUT_PRODUCT_IN_DB_VERSION \
        ParameterKey=PutInfringementInDbLambdaVersion,ParameterValue=$LAMBDA_PUT_INFRINGEMENT_IN_DB_VERSION \
        ParameterKey=LambdaLogLevel,ParameterValue=$LAMBDA_LOG_LEVEL \
        --capabilities CAPABILITY_NAMED_IAM
}

function deploy_infringement_store_stack {
    local stack_action=${1?ERROR: mandatory CloudFormation stack action is not provided}
    local stack_template=$CF_DIR/infringement_store.yaml
    local service=store
    local stack_name=$APPLICATION-$service

    aws cloudformation $stack_action --stack-name $stack_name \
        --template-body file://$stack_template \
        --parameters \
        ParameterKey=DbPort,ParameterValue=$DB_PORT \
        ParameterKey=DbName,ParameterValue=$DB_NAME \
        ParameterKey=DbUser,ParameterValue=$DB_USER \
        ParameterKey=DbPassword,ParameterValue=$DB_PASSWORD
}

function deploy_infringement_expose_stack {
    local stack_action=${1?ERROR: mandatory CloudFormation stack action is not provided}
    local stack_template=$CF_DIR/infringement_expose.yaml
    local service=expose
    local stack_name=$APPLICATION-$service
}

function deploy_service_stack {
    # CloudFormation stack action
    CF_STACK_ACTION=update-stack
    if [[ $2 == -c ]]; then
        CF_STACK_ACTION=create-stack
    fi
    # CloudFormation service stack
    case $1 in
        infringement-ingest)
            deploy_infringement_ingest_stack $CF_STACK_ACTION
            ;;
        infringement-transform)
            deploy_infringement_transform_stack $CF_STACK_ACTION
            ;;
        infringement-store)
            deploy_infringement_store_stack $CF_STACK_ACTION
            ;;
        infringement-expose)
            deploy_infringement_expose_stack $CF_STACK_ACTION
            ;;
        *)
            echo "${USAGE}"
            exit 1
    esac
}

deploy_service_stack $@

# Create [-c] or update CloudFormation stack
# aws cloudformation $CF_STACK_ACTION --stack-name $CF_STACK_NAME \
#     --template-body file://$CF_TEMPLATE \
#     --parameters \
#     ParameterKey=DbPort,ParameterValue=$DB_PORT \
#     ParameterKey=DbName,ParameterValue=$DB_NAME \
#     ParameterKey=DbUser,ParameterValue=$DB_USER \
#     ParameterKey=DbPassword,ParameterValue=$DB_PASSWORD \
#     ParameterKey=FirehoseDeliveryStreamS3BucketName,ParameterValue=$S3_FIREHOSE_DELIVERY_STREAM_BUCKET_NAME \
#     ParameterKey=LambdaPackageS3BucketName,ParameterValue=$S3_LAMBDA_PACKAGE_BUCKET_NAME \
#     ParameterKey=PutProductInDbLambdaVersion,ParameterValue=$LAMBDA_PUT_PRODUCT_IN_DB_VERSION \
#     ParameterKey=PutInfringementInDbLambdaVersion,ParameterValue=$LAMBDA_PUT_INFRINGEMENT_IN_DB_VERSION \
#     ParameterKey=LambdaLogLevel,ParameterValue=$LAMBDA_LOG_LEVEL \
#     --capabilities CAPABILITY_NAMED_IAM

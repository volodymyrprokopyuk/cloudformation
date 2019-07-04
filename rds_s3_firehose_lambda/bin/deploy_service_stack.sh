#!/usr/bin/env bash

set -x

source ./bin/config.sh

read -d "" USAGE <<EOF
Usage:
    ./bin/deploy_service_stack target [-c]"
Target:
    infringement-store - deploy PostgreSQL RDS
    infringement-ingest - deploy Kinesis Firehose delivery streams and S3 bucket
    infringement-transform - deploy data transformation Lambdas
    infringement-expose - deploy API Gateway backed by endpoint Lambdas
Options:
    -c create stack, if -c is omitted then update stack
EOF

readonly CF_DIR=$(pwd)/cloudformation

function deploy_infringement_ingest_stack {
    local stack_action=${1?ERROR: mandatory CloudFormation stack action is not provided}
    local stack_template=$CF_DIR/infringement_ingest.yaml
    local service=ingest
    local stack_name=$APPLICATION-$service-$ENVIRONMENT
    # Compose bucket name
    local lower_stack_name=$(echo $stack_name | tr '[:upper:]' '[:lower:]')
    local bucket_name=$lower_stack_name-$S3_FIREHOSE_INFRINGEMENT_DELIVERY_BUCKET_SUFFIX

    aws cloudformation $stack_action --stack-name $stack_name \
        --template-body file://$stack_template \
        --parameters \
        ParameterKey=S3FirehoseInfringementDeliveryBucketName,ParameterValue=$bucket_name \
        --capabilities CAPABILITY_NAMED_IAM
}

function deploy_infringement_transform_stack {
    local stack_action=${1?ERROR: mandatory CloudFormation stack action is not provided}
    local stack_template=$CF_DIR/infringement_transform.yaml
    local service=transform
    local stack_name=$APPLICATION-$service-$ENVIRONMENT

    aws cloudformation $stack_action --stack-name $stack_name \
        --template-body file://$stack_template \
        --parameters \
        ParameterKey=RdsEndpointAddressExportName,ParameterValue=$APPLICATION-store-$ENVIRONMENT:RdsEndpointAddress \
        ParameterKey=RdsEndpointPortExportName,ParameterValue=$APPLICATION-store-$ENVIRONMENT:RdsEndpointPort \
        ParameterKey=DbName,ParameterValue=$DB_NAME \
        ParameterKey=DbUser,ParameterValue=$DB_USER \
        ParameterKey=DbPassword,ParameterValue=$DB_PASSWORD \
        ParameterKey=S3FirehoseInfringementDeliveryBucketArnExportName,ParameterValue=$APPLICATION-ingest-$ENVIRONMENT:S3FirehoseInfringementDeliveryBucketArn \
        ParameterKey=S3LambdaPackageBucketName,ParameterValue=$S3_TRANSFORM_LAMBDA_PACKAGE_BUCKET_NAME \
        ParameterKey=LambdaLogLevel,ParameterValue=$LAMBDA_LOG_LEVEL \
        ParameterKey=LambdaPutProductInDbVersion,ParameterValue=$LAMBDA_PUT_PRODUCT_IN_DB_VERSION \
        ParameterKey=LambdaPutInfringementInDbVersion,ParameterValue=$LAMBDA_PUT_INFRINGEMENT_IN_DB_VERSION \
        --capabilities CAPABILITY_NAMED_IAM
}

function deploy_infringement_store_stack {
    local stack_action=${1?ERROR: mandatory CloudFormation stack action is not provided}
    local stack_template=$CF_DIR/infringement_store.yaml
    local service=store
    local stack_name=$APPLICATION-$service-$ENVIRONMENT

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
    local stack_name=$APPLICATION-$service-$ENVIRONMENT
}

function deploy_service_stack {
    # CloudFormation stack action
    local stack_action=update-stack
    if [[ $2 == -c ]]; then
        stack_action=create-stack
    fi
    # CloudFormation service stack
    case $1 in
        infringement-ingest)
            deploy_infringement_ingest_stack $stack_action
            ;;
        infringement-transform)
            deploy_infringement_transform_stack $stack_action
            ;;
        infringement-store)
            deploy_infringement_store_stack $stack_action
            ;;
        infringement-expose)
            deploy_infringement_expose_stack $stack_action
            ;;
        *)
            echo "${USAGE}"
            exit 1
    esac
}

deploy_service_stack $@

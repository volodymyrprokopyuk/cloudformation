#!/usr/bin/env bash

source ./bin/config.sh
source ./bin/util.sh

set $SETOPTS

set +e
read -d "" USAGE <<EOF
Usage:
    ./bin/deploy_service_stack target"
Target:
    infringement-store - deploy PostgreSQL RDS
    infringement-ingest - deploy Kinesis Firehose delivery streams and S3 bucket
    infringement-transform - deploy data transformation Lambdas
    infringement-expose - deploy API Gateway with Lambda endpoints
    infringement-all - deploy whole application
EOF
set -e

function _decide_stack_action {
    local stack_name=${1?ERROR: mandatory stack name is not provided}

    local stack_status=$(get_cf_stack_status $stack_name)
    local stack_action=""
    if cf_stack_does_not_exist $stack_status; then
        stack_action=create-stack
    elif is_cf_stack_create_update_complete $stack_status; then
        stack_action=update-stack
    else
        stack_action=""
    fi
    echo $stack_action
}

function deploy_infringement_ingest_stack {
    local stack_template=$CF_DIR/infringement_ingest.yaml
    local service=ingest
    local stack_name=$APPLICATION-$service-$ENVIRONMENT

    local stack_action=$(_decide_stack_action $stack_name)
    if [[ -z $stack_action ]]; then
        echo "ERROR: stack is not ready for create or update action" >&2
        return 1
    fi

    local lower_stack_name=$(echo $stack_name | tr '[:upper:]' '[:lower:]')
    local bucket_name=$lower_stack_name-$S3_INFRINGEMENT_DELIVERY_BUCKET_SUFFIX

    aws cloudformation $stack_action --stack-name $stack_name \
        --template-body file://$stack_template \
        --parameters \
        ParameterKey=S3InfringementDeliveryBucketName,ParameterValue=$bucket_name \
        --capabilities CAPABILITY_NAMED_IAM
    wait_for_cf_desired_stack_status $stack_name is_cf_stack_create_update_complete
}

function deploy_infringement_transform_stack {
    local stack_template=$CF_DIR/infringement_transform.yaml
    local service=transform
    local stack_name=$APPLICATION-$service-$ENVIRONMENT

    local stack_action=$(_decide_stack_action $stack_name)
    if [[ -z $stack_action ]]; then
        echo "ERROR: stack is not ready for create or update action" >&2
        return 1
    fi

    aws cloudformation $stack_action --stack-name $stack_name \
        --template-body file://$stack_template \
        --parameters \
        ParameterKey=EnvironmentType,ParameterValue=${ENVIRONMENT:0:4} \
        ParameterKey=RdsEndpointAddressExportName,ParameterValue=$APPLICATION-store-$ENVIRONMENT:RdsEndpointAddress \
        ParameterKey=RdsEndpointPortExportName,ParameterValue=$APPLICATION-store-$ENVIRONMENT:RdsEndpointPort \
        ParameterKey=DbName,ParameterValue=$DB_NAME \
        ParameterKey=DbUser,ParameterValue=$DB_INGEST_USER \
        ParameterKey=DbPassword,ParameterValue=$DB_INGEST_PASSWORD \
        ParameterKey=DbConnectTimeout,ParameterValue=$DB_CONNECT_TIMEOUT \
        ParameterKey=S3InfringementDeliveryBucketArnExportName,ParameterValue=$APPLICATION-ingest-$ENVIRONMENT:S3InfringementDeliveryBucketArn \
        ParameterKey=LambdaSecurityGroupIdExportName,ParameterValue=$APPLICATION-store-$ENVIRONMENT:LambdaSecurityGroupId \
        ParameterKey=PrivateSubnetAIdExportName,ParameterValue=$APPLICATION-store-$ENVIRONMENT:PrivateSubnetAId \
        ParameterKey=PrivateSubnetBIdExportName,ParameterValue=$APPLICATION-store-$ENVIRONMENT:PrivateSubnetBId \
        ParameterKey=S3LambdaPackageBucketName,ParameterValue=$S3_TRANSFORM_LAMBDA_PACKAGE_BUCKET_NAME \
        ParameterKey=LambdaLogLevel,ParameterValue=$LAMBDA_LOG_LEVEL \
        ParameterKey=LambdaPutProductInDbVersion,ParameterValue=$LAMBDA_PUT_PRODUCT_IN_DB_VERSION \
        ParameterKey=LambdaPutInfringementInDbVersion,ParameterValue=$LAMBDA_PUT_INFRINGEMENT_IN_DB_VERSION \
        ParameterKey=SnsInfringementImportAlarmNotificationEmail,ParameterValue=$SNS_INFRINGEMENT_IMPORT_ALARM_NOTIFICATION_EMAIL \
        --capabilities CAPABILITY_NAMED_IAM
    wait_for_cf_desired_stack_status $stack_name is_cf_stack_create_update_complete
}

function deploy_infringement_store_stack {
    local stack_template=$CF_DIR/infringement_store.yaml
    local service=store
    local stack_name=$APPLICATION-$service-$ENVIRONMENT

    local stack_action=$(_decide_stack_action $stack_name)
    if [[ -z $stack_action ]]; then
        echo "ERROR: stack is not ready for create or update action" >&2
        return 1
    fi

    aws cloudformation $stack_action --stack-name $stack_name \
        --template-body file://$stack_template \
        --parameters \
        ParameterKey=DbPort,ParameterValue=$DB_LOCAL_PORT \
        ParameterKey=DbName,ParameterValue=$DB_NAME \
        ParameterKey=DbUser,ParameterValue=$DB_SUPER_USER \
        ParameterKey=DbPassword,ParameterValue=$DB_SUPER_PASSWORD
    wait_for_cf_desired_stack_status $stack_name is_cf_stack_create_update_complete
}

function deploy_infringement_expose_stack {
    local stack_template=$CF_DIR/infringement_expose.yaml
    local service=expose
    local stack_name=$APPLICATION-$service-$ENVIRONMENT

    local stack_action=$(_decide_stack_action $stack_name)
    if [[ -z $stack_action ]]; then
        echo "ERROR: stack is not ready for create or update action" >&2
        return 1
    fi
}

function deploy_infringement_application {
    ./bin/upload_transform_lambda_to_s3.sh
    deploy_infringement_store_stack
    deploy_infringement_ingest_stack
    deploy_infringement_transform_stack
    ./bin/update_ingest_stack.sh
}

function deploy_service_stack {
    set +u
    case $1 in
        infringement-ingest)
            deploy_infringement_ingest_stack
            ;;
        infringement-transform)
            deploy_infringement_transform_stack
            ;;
        infringement-store)
            deploy_infringement_store_stack
            ;;
        infringement-expose)
            deploy_infringement_expose_stack
            ;;
        infringement-all)
            deploy_infringement_application
            ;;
        *)
            echo "${USAGE}"
            exit 1
    esac
    set -u
}

deploy_service_stack $@

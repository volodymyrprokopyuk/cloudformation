#!/usr/bin/env bash

source ./bin/config.sh
source ./bin/util.sh

set $SETOPTS

function delete_lambda_package_s3_bucket {
    local s3_lambda_package_bucket_name=${1?ERROR: mandatory lambda package S3 bucket name is not provided}

    if aws s3 ls $s3_lambda_package_bucket_name; then
        aws s3 rm s3://$s3_lambda_package_bucket_name --recursive
        aws s3 rb s3://$s3_lambda_package_bucket_name
    fi
}

function delete_infringement_delivery_bucket_content {
    local stack_name=$APPLICATION-ingest-$ENVIRONMENT
    local lower_stack_name=$(echo $stack_name | tr '[:upper:]' '[:lower:]')
    local bucket_name=s3://$lower_stack_name-$S3_INFRINGEMENT_DELIVERY_BUCKET_SUFFIX

    if aws s3 ls $bucket_name; then
        aws s3 rm s3://$lower_stack_name-$S3_INFRINGEMENT_DELIVERY_BUCKET_SUFFIX --recursive
    fi
}

function delete_infringement_expose_stack {
    local stack_name=$APPLICATION-expose-$ENVIRONMENT

    delete_lambda_package_s3_bucket $S3_EXPOSE_LAMBDA_PACKAGE_BUCKET_NAME
    delete_cf_stack $stack_name
}

function delete_infringement_transform_stack {
    local stack_name=$APPLICATION-transform-$ENVIRONMENT

    delete_lambda_package_s3_bucket $S3_TRANSFORM_LAMBDA_PACKAGE_BUCKET_NAME
    delete_cf_stack $stack_name
}

function delete_infringement_ingest_stack {
    local stack_name=$APPLICATION-ingest-$ENVIRONMENT

    delete_infringement_delivery_bucket_content
    delete_cf_stack $stack_name
}

function delete_infringement_store_stack {
    local stack_name=$APPLICATION-store-$ENVIRONMENT

    delete_cf_stack $stack_name
}

function prompt_for_delete {
    echo "ALL stacks of $APPLICATION application will be DELETED! [YES/NO]"
    set +u
    if [[ $1 == -y ]]; then
        RESPONSE=YES
    else
        read -r RESPONSE
    fi
    set -u
    if [[ $RESPONSE == YES ]]; then
        delete_infringement_expose_stack
        delete_infringement_transform_stack
        delete_infringement_ingest_stack
        delete_infringement_store_stack
    else
        echo "DELETE aborted: ${RESPONSE:-empty response}"
    fi
}

cd $BIN_DIR
setup_virtual_environment $PYVENV
cd $ROOT_DIR

prompt_for_delete "$@"

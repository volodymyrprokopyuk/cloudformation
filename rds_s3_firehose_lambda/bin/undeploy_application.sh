#!/usr/bin/env bash

set -eux

source ./bin/config.sh
source ./bin/util.sh

function delete_transform_lambda_package_bucket {
    local bucket_name=s3://$S3_TRANSFORM_LAMBDA_PACKAGE_BUCKET_NAME

    if aws s3 ls $bucket_name; then
        aws s3 rm s3://$S3_TRANSFORM_LAMBDA_PACKAGE_BUCKET_NAME --recursive
        aws s3 rb s3://$S3_TRANSFORM_LAMBDA_PACKAGE_BUCKET_NAME
    fi
}

function delete_infringement_delivery_bucket_content {
    local service=ingest
    local stack_name=$APPLICATION-$service-$ENVIRONMENT
    local lower_stack_name=$(echo $stack_name | tr '[:upper:]' '[:lower:]')
    local bucket_name=s3://$lower_stack_name-$S3_INFRINGEMENT_DELIVERY_BUCKET_SUFFIX

    if aws s3 ls $bucket_name; then
        aws s3 rm s3://$lower_stack_name-$S3_INFRINGEMENT_DELIVERY_BUCKET_SUFFIX --recursive
    fi
}

function delete_infringement_transform_stack {
    local service=transform
    local stack_name=$APPLICATION-$service-$ENVIRONMENT

    delete_transform_lambda_package_bucket
    delete_cf_stack $stack_name
}

function delete_infringement_ingest_stack {
    local service=ingest
    local stack_name=$APPLICATION-$service-$ENVIRONMENT

    delete_infringement_delivery_bucket_content
    delete_cf_stack $stack_name
}

function delete_infringement_store_stack {
    local service=store
    local stack_name=$APPLICATION-$service-$ENVIRONMENT

    delete_cf_stack $stack_name
}

function prompt_for_delete {
    echo "ALL stacks of $APPLICATION application will be DELETED! [YES/NO]"
    set +u
    if [[ $1 == -y ]]; then
        RESPONSE=YES
    else
        read RESPONSE
    fi
    set -u
    if [[ $RESPONSE == YES ]]; then
        delete_infringement_transform_stack
        delete_infringement_ingest_stack
        delete_infringement_store_stack
    else
        echo "DELETE aborted: ${RESPONSE:-empty response}"
    fi
}

prompt_for_delete $@

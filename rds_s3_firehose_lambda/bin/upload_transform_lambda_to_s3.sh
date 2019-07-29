#!/usr/bin/env bash

source ./bin/config.sh
source ./bin/util.sh

set $SETOPTS

function create_and_upload_lambda_archive_to_s3 {
    local lambda_dir=${1?ERROR: mandatory lambda source direcotry is not provided}
    local lambda_name=${lambda_dir##*/}
    local lambda_version=$(cat $lambda_dir/version)
    local lambda_archive=$lambda_dir/${lambda_name}-${lambda_version}.zip
    local deps_dir=$lambda_dir/$PYVENV/lib/python3.7/site-packages

    cd $lambda_dir
    # Install lambda dependencies
    # rm -rf $lambda_dir/$PYVENV
    setup_virtual_environment $PYVENV
    # Create lambda archive
    rm -rf $lambda_archive
    # Add Python dependencies and exclude the psycopg2 with dynamically linked libpg
    cd $deps_dir
    zip -9 -q -r $lambda_archive . -x '*psycopg2/*' -x '*__pycache__/*' -x '*~'
    # Add common shared Python code and psycopg2 with statically linked libpg
    # as AWS Lambda environment does not have libpg
    cd $LAMBDA_LIB_DIR
    zip -9 -q -r $lambda_archive . -x '*test/*' -x '*__pycache__/*' -x '*~'
    # Add lambda function source code
    cd $lambda_dir
    # shellcheck disable=SC2035
    zip -9 -q $lambda_archive *.py
    # Upload lambda archive to S3
    aws s3 cp $lambda_archive s3://$S3_TRANSFORM_LAMBDA_PACKAGE_BUCKET_NAME
}

create_s3_bucket_if_not_exists $S3_TRANSFORM_LAMBDA_PACKAGE_BUCKET_NAME

for lambda_dir in $LAMBDA_FUNCTION_DIR/*; do
    create_and_upload_lambda_archive_to_s3 $lambda_dir
done

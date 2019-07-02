#!/usr/bin/env bash

set -x

source ./bin/config.sh

readonly PYVENV=pyvenv
readonly LAMBDA_DIR=$(pwd)/lambda/function
readonly LIB_DIR=$(pwd)/lambda/lib

function create_s3_bucket_if_not_exists {
    local s3_bucket_name=${1?ERROR: mandatory S3 bucket name is not provided}
    if aws s3 ls s3://$s3_bucket_name 2>&1 | grep -q 'NoSuchBucket'; then
        aws s3 mb s3://$s3_bucket_name
    fi
}

function create_and_upload_lambda_archive_to_s3 {
    local lambda_name=${1?ERROR: mandatory lambda name is not provided}
    local lambda_dir=$LAMBDA_DIR/$lambda_name
    local lambda_version=$(cat $lambda_dir/version)
    local lambda_archive=$lambda_dir/${lambda_name}-${lambda_version}.zip
    local deps_dir=$lambda_dir/$PYVENV/lib/python3.7/site-packages
    rm -rf $lambda_archive
    # Install lambda dependencies
    cd $lambda_dir
    deactivate
    python -m venv $PYVENV
    source $PYVENV/bin/activate
    pip install -r requirements.txt
    deactivate
    # Create lambda archive
    # Add Python dependencies and exclude the psycopg2 with dynamically linked libpg
    cd $deps_dir
    zip -9 -q -r $lambda_archive . -x '*psycopg2/*' -x '*__pycache__/*'
    # Add common shared Python code and the psycopg2 with statically linked libpg
    # as AWS Lambda environment does not have libpg
    cd $LIB_DIR
    zip -9 -q -r $lambda_archive .
    # Add lambda Python source code
    cd $lambda_dir
    zip -9 -q $lambda_archive *.py
    # Upload lambda archive to S3
    aws s3 cp $lambda_archive s3://$S3_LAMBDA_PACKAGE_BUCKET_NAME
}

create_s3_bucket_if_not_exists $S3_LAMBDA_PACKAGE_BUCKET_NAME

for lambda in $LAMBDA_DIR/*; do
    lambda_name=${lambda##*/}
    create_and_upload_lambda_archive_to_s3 $lambda_name
done

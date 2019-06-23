#!/usr/bin/env bash

set -x

source ./bin/config.sh

readonly ROOT_DIR=$(pwd)/lambda
readonly PYVENV=pyvenv

function create_and_upload_lambda_archive_to_s3 {
    local lambda_name=${1?ERROR: lambda name is expected}
    local lambda_dir=$ROOT_DIR/$lambda_name
    local lambda_version=$(cat $lambda_dir/version)
    local lambda_archive=$lambda_dir/${lambda_name}-${lambda_version}.zip
    local deps_dir=$lambda_dir/$PYVENV/lib/python3.7/site-packages
    # Install lambda dependencies
    cd $lambda_dir
    deactivate
    python -m venv $PYVENV
    source $PYVENV/bin/activate
    pip install -r requirements.txt
    deactivate
    # Create lambda archive
    cd $deps_dir
    zip -r -9 $lambda_archive .
    cd $lambda_dir
    zip $lambda_archive *.py
    # Upload lambda archive to S3
    aws s3 cp $lambda_archive s3://$S3_LAMBDA_PACKAGE_BUCKET_NAME
}

for lambda in $ROOT_DIR/*; do
    lambda_name=${lambda##*/}
    create_and_upload_lambda_archive_to_s3 $lambda_name
done

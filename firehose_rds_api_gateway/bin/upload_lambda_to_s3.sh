#!/usr/bin/env bash

source ./bin/config.sh
source ./bin/util.sh

set $SETOPTS

cd $BIN_DIR
setup_virtual_environment $PYVENV
cd $ROOT_DIR

function create_and_upload_lambda_archive_to_s3 {
    local lambda_dir=${1?ERROR: mandatory lambda source direcotry is not provided}
    local s3_lambda_package_bucket_name=${2?ERROR: mandatory lambda package S3 bucket anme is not provided}
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
    aws s3 cp $lambda_archive s3://$s3_lambda_package_bucket_name
}

# infringement-transform lambdas
create_s3_bucket_if_not_exists $S3_TRANSFORM_LAMBDA_PACKAGE_BUCKET_NAME

for transform_lambda_dir in $LAMBDA_TRANSFORM_DIR/*; do
    create_and_upload_lambda_archive_to_s3 $transform_lambda_dir \
        $S3_TRANSFORM_LAMBDA_PACKAGE_BUCKET_NAME
done

# infringement-expose lambdas
create_s3_bucket_if_not_exists $S3_EXPOSE_LAMBDA_PACKAGE_BUCKET_NAME

for expose_lambda_dir in $LAMBDA_EXPOSE_DIR/*; do
    create_and_upload_lambda_archive_to_s3 $expose_lambda_dir \
        $S3_EXPOSE_LAMBDA_PACKAGE_BUCKET_NAME
done

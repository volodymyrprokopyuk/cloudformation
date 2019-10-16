#!/usr/bin/env bash

source ./bin/config.sh
source ./bin/util.sh

set $SETOPTS

# Database configuration
export DB_HOST
export DB_PORT=$DB_LOCAL_PORT
export DB_NAME
export DB_USER=$DB_SUPER_USER
export DB_PASSWORD=$DB_SUPER_PASSWORD
export DB_CONNECT_TIMEOUT

function integration_test_transform_lambda {
    local transform_lambda_source=${1?ERROR: mandatory transform lambda source directory is not provided}
    local transform_lambda_test=$transform_lambda_source/test
    local transform_lambda_test_data=$transform_lambda_test/data

    cd $transform_lambda_source
    cp $transform_lambda_test_data/*.txt $LAMBDA_TEST_DATA_DIR
    setup_virtual_environment $PYVENV install_test_deps
    export PYTHONPATH=$LAMBDA_LIB_DIR:$transform_lambda_source
    # Test transform lambda function
    pytest -x -v -s --disable-pytest-warnings \
        --cov $transform_lambda_source --cov-report term --cov-report html --cov-append \
        $transform_lambda_test/integration_test.py
    unset PYTHONPATH
}

function integration_test_expose_lambda {
    local expose_lambda_source=${1?ERROR: mandatory expose lambda source directory is not provided}
    local expose_lambda_test=$expose_lambda_source/test

    cd $expose_lambda_source
    setup_virtual_environment $PYVENV install_test_deps
    export PYTHONPATH=$LAMBDA_LIB_DIR:$expose_lambda_source
    # Test expose lambda function
    pytest -x -v -s --disable-pytest-warnings \
        --cov $expose_lambda_source --cov-report term --cov-report html --cov-append \
        $expose_lambda_test/integration_test.py
    unset PYTHONPATH
}

# Create database schema in local database
cd $ROOT_DIR
./bin/create_db_schema.sh -l

for transform_lambda_source in $LAMBDA_TRANSFORM_DIR/*; do
    integration_test_transform_lambda $transform_lambda_source
done

# Create database schema in local database
cd $ROOT_DIR
./bin/create_db_schema.sh -l

for expose_lambda_source in $LAMBDA_EXPOSE_DIR/*; do
    integration_test_expose_lambda $expose_lambda_source
done

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

readonly LAMBDA_TEST_DATA_DIR=/tmp

function integration_test_lambda_function {
    local lambda_function_source=${1?ERROR: mandatory lambda source directory is not provided}
    local lambda_function_test=$lambda_function_source/test
    local lambda_function_test_data=$lambda_function_test/data

    cd $lambda_function_source
    cp $lambda_function_test_data/*.txt $LAMBDA_TEST_DATA_DIR
    setup_virtual_environment $PYVENV install_test_deps
    export PYTHONPATH=$LAMBDA_LIB_DIR:$lambda_function_source
    # Test transform lambda function
    pytest -x -v -s --disable-pytest-warnings \
        --cov $lambda_function_source --cov-report term --cov-report html --cov-append \
        $lambda_function_test/integration_test.py
    unset PYTHONPATH
}

# Create database schema in local database
./bin/create_db_schema.sh -l

for lambda_function_source in $LAMBDA_FUNCTION_DIR/*; do
    integration_test_lambda_function $lambda_function_source
done

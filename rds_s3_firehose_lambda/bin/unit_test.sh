#!/usr/bin/env bash

source ./bin/config.sh
source ./bin/util.sh

set $SETOPTS

readonly LAMBDA_COMMON_SOURCE=$LAMBDA_LIB_DIR/common
readonly LAMBDA_COMMON_TEST=$LAMBDA_COMMON_SOURCE/test
readonly LAMBDA_COMMON_TEST_DATA=$LAMBDA_COMMON_TEST/data
readonly LAMBDA_TEST_DATA_DIR=/tmp

function unit_test_lambda_function {
    local lambda_function_source=${1?ERROR: mandatory lambda source directory is not provided}
    local lambda_function_test=$lambda_function_source/test
    local lambda_function_test_data=$lambda_function_test/data

    cd $lambda_function_source
    cp $LAMBDA_COMMON_TEST_DATA/*.txt $LAMBDA_TEST_DATA_DIR
    cp $lambda_function_test_data/*.txt $LAMBDA_TEST_DATA_DIR
    setup_virtual_environment
    export PYTHONPATH=$LAMBDA_LIB_DIR:$lambda_function_source
    # transform lambda common test
    pytest -x -v -s --disable-pytest-warnings \
        --cov $LAMBDA_COMMON_SOURCE --cov $lambda_function_source \
        --cov-report term --cov-report html $LAMBDA_COMMON_TEST
    # transform lambda function test
    pytest -x -v -s --disable-pytest-warnings \
        --cov $LAMBDA_COMMON_SOURCE --cov $lambda_function_source \
        --cov-report term --cov-report html --cov-append $lambda_function_test
    unset PYTHONPATH
}

for lambda_function_source in $LAMBDA_FUNCTION_DIR/*Product*; do
    unit_test_lambda_function $lambda_function_source
done

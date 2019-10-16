#!/usr/bin/env bash

source ./bin/config.sh
source ./bin/util.sh

set $SETOPTS

function unit_test_transform_lambda {
    local transform_lambda_source=${1?ERROR: mandatory transform lambda source directory is not provided}
    local transform_lambda_test=$transform_lambda_source/test
    local transform_lambda_test_data=$transform_lambda_test/data
    local transform_lambda_common_source=$LAMBDA_LIB_DIR/common/transform
    local transform_lambda_common_test=$transform_lambda_common_source/test
    local transform_lambda_common_test_data=$transform_lambda_common_test/data

    cd $transform_lambda_source
    cp $transform_lambda_common_test_data/*.txt $LAMBDA_TEST_DATA_DIR
    cp $transform_lambda_test_data/*.txt $LAMBDA_TEST_DATA_DIR
    setup_virtual_environment $PYVENV install_test_deps
    export PYTHONPATH=$LAMBDA_LIB_DIR:$transform_lambda_source
    # Test transform lambda common logic
    pytest -x -v -s --disable-pytest-warnings \
        --cov $transform_lambda_common_source --cov $transform_lambda_source \
        --cov-report term --cov-report html \
        $transform_lambda_common_test/unit_test.py
    # Test transform lambda function
    pytest -x -v -s --disable-pytest-warnings \
        --cov $transform_lambda_common_source --cov $transform_lambda_source \
        --cov-report term --cov-report html --cov-append \
        $transform_lambda_test/unit_test.py
    unset PYTHONPATH
}

function unit_test_expose_lambda {
    local expose_lambda_source=${1?ERROR: mandatory expose lambda source directory is not provided}
    local expose_lambda_test=$expose_lambda_source/test
    local expose_lambda_common_source=$LAMBDA_LIB_DIR/common/expose
    local expose_lambda_common_test=$expose_lambda_common_source/test

    cd $expose_lambda_source
    setup_virtual_environment $PYVENV install_test_deps
    export PYTHONPATH=$LAMBDA_LIB_DIR:$expose_lambda_source
    # Test expose lambda common logic
    pytest -x -v -s --disable-pytest-warnings \
        --cov $expose_lambda_common_source --cov $expose_lambda_source \
        --cov-report term --cov-report html \
        $expose_lambda_common_test/unit_test.py
    # Test expose lambda function
    pytest -x -v -s --disable-pytest-warnings \
        --cov $expose_lambda_common_source --cov $expose_lambda_source \
        --cov-report term --cov-report html --cov-append \
        $expose_lambda_test/unit_test.py
    unset PYTHONPATH
}

for transform_lambda_source in $LAMBDA_TRANSFORM_DIR/*; do
    unit_test_transform_lambda $transform_lambda_source
done

for expose_lambda_source in $LAMBDA_EXPOSE_DIR/*; do
    unit_test_expose_lambda $expose_lambda_source
done

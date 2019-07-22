#!/usr/bin/env bash

source ./bin/config.sh

set $SETOPTS

readonly LAMBDA_COMMON_SOURCE=$LAMBDA_LIB_DIR/common
readonly LAMBDA_SOURCE=$LAMBDA_FUNCTION_DIR/PutProductInDbLambda
readonly LAMBDA_TEST=$LAMBDA_SOURCE/test
readonly LAMBDA_TEST_DATA=$LAMBDA_TEST/data
export PYTHONPATH=$LAMBDA_LIB_DIR:$LAMBDA_SOURCE

cp $LAMBDA_TEST_DATA/*.txt /tmp

cd $LAMBDA_SOURCE

if [[ ! -d $PYVENV ]]; then
    python -m venv $PYVENV
    source $PYVENV/bin/activate
    pip install -r requirements.txt
else
    source $PYVENV/bin/activate
fi

pytest -x -v -s --disable-pytest-warnings \
    --cov $LAMBDA_COMMON_SOURCE --cov $LAMBDA_SOURCE \
    --cov-report term --cov-report html $LAMBDA_TEST

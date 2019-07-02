#!/usr/bin/env bash

set -eux

source ./bin/config.sh

export STACK_NAME=$CF_STACK_NAME
export LOG_LEVEL=$LAMBDA_LOG_LEVEL

export DB_HOST=localhost
export DB_PORT
export DB_NAME
export DB_USER
export DB_PASSWORD

readonly LAMBDA_FUNCTION_DIR=$(pwd)/lambda/function
readonly LAMBDA_LIB_DIR=$(pwd)/lambda/lib

export PYTHONPATH=$LAMBDA_LIB_DIR

readonly LAMBDA_PUT_PRODUCT_IN_DB=$LAMBDA_FUNCTION_DIR/PutProductInDbLambda/lambda_function.py
readonly LAMBDA_PUT_INFRINGEMENT_IN_DB=$LAMBDA_FUNCTION_DIR/PutInfringementInDbLambda/lambda_function.py

export LAMBDA_VERSION=$LAMBDA_PUT_PRODUCT_IN_DB_VERSION
python $LAMBDA_PUT_PRODUCT_IN_DB
export LAMBDA_VERSION=$LAMBDA_PUT_INFRINGEMENT_IN_DB_VERSION
python $LAMBDA_PUT_INFRINGEMENT_IN_DB

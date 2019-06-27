#!/usr/bin/env bash

set -eux

source ./bin/config.sh

export DB_HOST
export DB_PORT
export DB_NAME
export DB_USER
export DB_PASSWORD

readonly LAMBDA_FUNCTION_DIR=$(pwd)/lambda/function
readonly LAMBDA_LIB_DIR=$(pwd)/lambda/lib

export PYTHONPATH=$LAMBDA_LIB_DIR

readonly LAMBDA_PUT_PRODUCT_IN_DB=$LAMBDA_FUNCTION_DIR/PutProductInDbLambda/lambda_function.py
readonly LAMBDA_PUT_INFRINGEMENT_IN_DB=$LAMBDA_FUNCTION_DIR/PutInfringementInDbLambda/lambda_function.py

# python $LAMBDA_PUT_PRODUCT_IN_DB
python $LAMBDA_PUT_INFRINGEMENT_IN_DB

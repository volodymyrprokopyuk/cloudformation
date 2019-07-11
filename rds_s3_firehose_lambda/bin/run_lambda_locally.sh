#!/usr/bin/env bash

source ./bin/config.sh

set $SETOPTS

# Application and envirnment configuration
export STACK_NAME=$APPLICATION-transform-$ENVIRONMENT

# Database configuration
export DB_HOST=localhost
export DB_PORT
export DB_NAME
export DB_USER=$DB_INGEST_USER
export DB_PASSWORD=$DB_INGEST_PASSWORD

# Lambda configuration
export LOG_LEVEL=$LAMBDA_LOG_LEVEL
export PYTHONPATH=$LAMBDA_LIB_DIR

readonly LAMBDA_PUT_PRODUCT_IN_DB=$LAMBDA_FUNCTION_DIR/PutProductInDbLambda/lambda_function.py
readonly LAMBDA_PUT_INFRINGEMENT_IN_DB=$LAMBDA_FUNCTION_DIR/PutInfringementInDbLambda/lambda_function.py

# Execute transform lambdas
export LAMBDA_VERSION=$LAMBDA_PUT_PRODUCT_IN_DB_VERSION
python $LAMBDA_PUT_PRODUCT_IN_DB
export LAMBDA_VERSION=$LAMBDA_PUT_INFRINGEMENT_IN_DB_VERSION
python $LAMBDA_PUT_INFRINGEMENT_IN_DB

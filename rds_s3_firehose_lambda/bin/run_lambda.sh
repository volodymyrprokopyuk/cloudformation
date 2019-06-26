#!/usr/bin/env bash

set -eux

source ./bin/config.sh

export DB_HOST
export DB_PORT
export DB_NAME
export DB_USER
export DB_PASSWORD

LAMBDA_ROOT=$(pwd)/lambda/function
LAMBDA_FUNCTION=$LAMBDA_ROOT/PutProductInDbLambda/lambda_function.py

python $LAMBDA_FUNCTION

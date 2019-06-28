#!/usr/bin/env bash

set -eux

readonly ROOT_DIR=$(pwd)/client
readonly CLIENT_SCRIPT=$ROOT_DIR/main.py

python $CLIENT_SCRIPT -p $ROOT_DIR/product.txt
sleep 5
python $CLIENT_SCRIPT -i $ROOT_DIR/infringement.txt

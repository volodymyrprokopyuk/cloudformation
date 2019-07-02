#!/usr/bin/env bash

set -eux

readonly CLIENT_DIR=$(pwd)/client
readonly CLIENT_SCRIPT=$CLIENT_DIR/main.py
readonly CLIENT_DATA=$CLIENT_DIR/data

python $CLIENT_SCRIPT -p $CLIENT_DATA/product.txt
sleep 5
python $CLIENT_SCRIPT -i $CLIENT_DATA/infringement.txt

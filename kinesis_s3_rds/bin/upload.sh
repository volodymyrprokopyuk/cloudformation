#!/usr/bin/env bash

set -x

ROOT_DIR=client

python $ROOT_DIR/main.py -p $ROOT_DIR/product.txt
python $ROOT_DIR/main.py -i $ROOT_DIR/infringement.txt

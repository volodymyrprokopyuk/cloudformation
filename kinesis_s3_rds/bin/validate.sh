#!/usr/bin/env bash

set -eux

TEMPLATE=kinesis_s3_rds.yaml
SOURCE=client/*.py
TEST_SOURCE=client/test/*.py
LINE_LENGTH=88

# Validate CloudFormation Stack Template
aws cloudformation validate-template --template-body file://$(pwd)/$TEMPLATE

# Validate source code
black --line-length $LINE_LENGTH --check $SOURCE
flake8 --max-line-length=$LINE_LENGTH $SOURCE
pylint --max-line-length=$LINE_LENGTH --exit-zero $SOURCE

# Validate tests
# black --line-length $LINE_LENGTH --check $TEST_SOURCE
# flake8 --max-line-length=$LINE_LENGTH $TEST_SOURCE
# pylint --max-line-length=$LINE_LENGTH --exit-zero $TEST_SOURCE

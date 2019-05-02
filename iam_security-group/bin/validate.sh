#!/usr/bin/env bash

set -eux

SOURCE=*.py
LINE_LENGTH=88

# Validate CloudFormation Stack definition
aws cloudformation validate-template --template-body file://$(pwd)/iam_security-group.yaml

# Validate Python code
black --line-length $LINE_LENGTH --check $SOURCE
flake8 --max-line-length=$LINE_LENGTH $SOURCE
pylint --max-line-length=$LINE_LENGTH --exit-zero $SOURCE

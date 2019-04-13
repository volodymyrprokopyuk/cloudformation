#!/usr/bin/env bash

set -eux

TARGET=*.py

aws cloudformation validate-template --template-body file://$(pwd)/sqs.yaml
flake8 $TARGET
bandit $TARGET
radon cc $TARGET
pylint --max-line-length=120 $TARGET
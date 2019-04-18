#!/usr/bin/env bash

set -eux

SOURCE=sqs/*.py
TEST_SOURCE=sqs/test/*.py

aws cloudformation validate-template --template-body file://$(pwd)/sqs.yaml

flake8 $SOURCE
bandit $SOURCE
radon cc $SOURCE
pylint --max-line-length=120 $SOURCE || true

flake8 $TEST_SOURCE
pylint --max-line-length=120 $TEST_SOURCE || true

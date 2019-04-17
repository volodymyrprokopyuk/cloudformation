#!/usr/bin/env bash

set -eux

SOURCE=sqs/*.py

aws cloudformation validate-template --template-body file://$(pwd)/sqs.yaml
flake8 $SOURCE
bandit $SOURCE
radon cc $SOURCE
pylint --max-line-length=120 $SOURCE

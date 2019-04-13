#!/usr/bin/env bash

set -eux

aws cloudformation validate-template --template-body file://$(pwd)/sqs.yaml
flake8 *.py
bandit *.py
radon cc *.py
pylint --max-line-length=120 *.py

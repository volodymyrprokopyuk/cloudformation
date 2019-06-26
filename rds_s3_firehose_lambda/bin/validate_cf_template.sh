#!/usr/bin/env bash

set -eux

source ./bin/config.sh

# Validate CloudFormation stack template
aws cloudformation validate-template --template-body file://$CF_TEMPLATE

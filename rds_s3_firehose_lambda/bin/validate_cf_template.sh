#!/usr/bin/env bash

set -ex

USAGE="Usage: ./bin/validate_cf_template.sh <cf_template.yaml>"

if [[ ! -f $1 ]]; then
    echo $USAGE
    exit 1
fi

CF_TEMPLATE=$(pwd)/$1

# Validate CloudFormation template
aws cloudformation validate-template --template-body file://$CF_TEMPLATE
cfn-lint $CF_TEMPLATE

#!/usr/bin/env bash

source ./bin/config.sh
source ./bin/util.sh

set $SETOPTS

USAGE="Usage: ./bin/validate_cf_template.sh <cf_template.yaml>"

set +u
if [[ ! -f $1 ]]; then
    echo $USAGE
    exit 1
fi
set -u

readonly CF_TEMPLATE=$(pwd)/$1

cd $BIN_DIR
setup_virtual_environment $PYVENV
cd $ROOT_DIR

# Validate CloudFormation template
aws cloudformation validate-template --template-body file://$CF_TEMPLATE
cfn-lint $CF_TEMPLATE

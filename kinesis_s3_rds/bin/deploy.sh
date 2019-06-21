#!/usr/bin/env bash

set -eu

STACK_NAME=vlad-stack
TEMPLATE=kinesis_s3_rds.yaml

aws cloudformation create-stack --stack-name $STACK_NAME \
    --template-body file://$(pwd)/$TEMPLATE \
    --capabilities CAPABILITY_NAMED_IAM

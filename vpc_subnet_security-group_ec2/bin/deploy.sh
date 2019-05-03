#!/usr/bin/env bash

set -eu

STACK_NAME=vlad-stack
TEMPLATE=vpc_subnet_security-group_ec2.yaml

aws cloudformation create-stack --stack-name $STACK_NAME \
    --template-body file://$(pwd)/$TEMPLATE

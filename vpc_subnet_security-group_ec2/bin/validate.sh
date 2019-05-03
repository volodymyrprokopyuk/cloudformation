#!/usr/bin/env bash

set -eux

TEMPLATE=vpc_subnet_security-group_ec2.yaml

aws cloudformation validate-template --template-body file://$(pwd)/$TEMPLATE

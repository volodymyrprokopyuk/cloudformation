#!/usr/bin/env bash

set -eux

aws cloudformation validate-template --template-body file://$(pwd)/vpc_subnet_security-group_ec2.yaml

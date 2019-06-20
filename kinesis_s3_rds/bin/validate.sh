#!/usr/bin/env bash

set -eux

TEMPLATE=kinesis_s3_rds.yaml

aws cloudformation validate-template --template-body file://$(pwd)/$TEMPLATE

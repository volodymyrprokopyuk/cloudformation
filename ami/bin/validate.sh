#!/usr/bin/env bash

set -eux

TEMPLATE=ami.yaml

aws cloudformation validate-template --template-body file://$(pwd)/$TEMPLATE

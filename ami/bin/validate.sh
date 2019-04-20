#!/usr/bin/env bash

set -eux

aws cloudformation validate-template --template-body file://$(pwd)/ami.yaml

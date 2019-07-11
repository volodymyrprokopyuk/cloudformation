#!/usr/bin/env bash

set -eux

source ./bin/config.sh
source ./bin/util.sh

if wait_for_stack_create_update_complete transform; then
    echo STACK_COMPLETE
else
    echo STACK_ERROR
fi

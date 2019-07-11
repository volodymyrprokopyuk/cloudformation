#!/usr/bin/env bash

source ./bin/config.sh
source ./bin/util.sh

set $SETOPTS

if wait_for_stack_create_update_complete transform; then
    echo STACK_COMPLETE
else
    echo STACK_ERROR
fi

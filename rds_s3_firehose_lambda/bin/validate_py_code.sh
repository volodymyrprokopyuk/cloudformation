#!/usr/bin/env bash

source ./bin/config.sh

set $SETOPTS

readonly LINE_LENGTH=88
readonly PY_SOURCE="client/*.py lambda/lib/common/*.py lambda/function/*/*.py"
readonly PY_TEST_SOURCE="client/test/*.py lambda/function/*/test/*.py"

# Validate Python source code
black --line-length $LINE_LENGTH $PY_SOURCE
flake8 --max-line-length=$LINE_LENGTH $PY_SOURCE
pylint --max-line-length=$LINE_LENGTH \
    --disable=invalid-name \
    --disable=bad-continuation \
    --disable=no-value-for-parameter \
    --disable=broad-except \
    --exit-zero $PY_SOURCE

# Validate Python tests
# black --line-length $LINE_LENGTH --check $PY_TEST_SOURCE
# flake8 --max-line-length=$LINE_LENGTH $PY_TEST_SOURCE
# pylint --max-line-length=$LINE_LENGTH --exit-zero $PY_TEST_SOURCE

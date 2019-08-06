#!/usr/bin/env bash

source ./bin/config.sh
source ./bin/util.sh

set $SETOPTS

readonly LINE_LENGTH=88
readonly PY_SOURCE="client/*.py lambda/lib/common/*.py lambda/function/*/*.py"
# shellcheck disable=SC2010
readonly PY_TEST_SOURCE=$(ls lambda/function/*/test/*.py | grep -v 'conftest.py')

cd $BIN_DIR
setup_virtual_environment $PYVENV
cd $ROOT_DIR

# Validate Python source code
black --line-length $LINE_LENGTH $PY_SOURCE
flake8 --max-line-length=$LINE_LENGTH $PY_SOURCE
pylint --max-line-length=$LINE_LENGTH \
    --disable=invalid-name \
    --disable=bad-continuation \
    --disable=no-value-for-parameter \
    --disable=broad-except \
    $PY_SOURCE

# Validate Python tests
black --line-length $LINE_LENGTH $PY_TEST_SOURCE
flake8 --max-line-length=$LINE_LENGTH $PY_TEST_SOURCE
pylint --max-line-length=$LINE_LENGTH \
    --disable=bad-continuation \
    --disable=missing-docstring \
    --disable=import-error \
    --disable=too-many-arguments \
    --disable=unused-argument \
    --disable=redefined-outer-name \
    --disable=duplicate-code \
    $PY_TEST_SOURCE

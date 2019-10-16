#!/usr/bin/env bash

source ./bin/config.sh
source ./bin/util.sh

set $SETOPTS

readonly LINE_LENGTH=88
readonly PY_SOURCE="
$LAMBDA_LIB_DIR/common/*.py
$LAMBDA_LIB_DIR/common/test/*.py
$LAMBDA_LIB_DIR/common/transform/*.py
$LAMBDA_LIB_DIR/common/expose/*.py
$LAMBDA_TRANSFORM_DIR/*/*.py
$LAMBDA_EXPOSE_DIR/*/*.py
$DIRECT_IMPORT_DIR/*.py
$FIREHOSE_IMPORT_DIR/*.py
"
# shellcheck disable=SC2010
readonly PY_TEST_SOURCE=$(
    ls $LAMBDA_LIB_DIR/common/transform/test/*.py \
    $LAMBDA_LIB_DIR/common/transform/test/fixture/*.py \
    $LAMBDA_LIB_DIR/common/expose/test/*.py \
    $LAMBDA_LIB_DIR/common/expose/test/fixture/*.py \
    $LAMBDA_TRANSFORM_DIR/*/test/*.py \
    $LAMBDA_TRANSFORM_DIR/*/test/fixture/*.py \
    $LAMBDA_EXPOSE_DIR/*/test/*.py \
    $LAMBDA_EXPOSE_DIR/*/test/fixture/*.py \
    $TEST_DIR/*.py \
    $TEST_DIR/fixture/*.py \
    | grep -v 'conftest.py'
)

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
    --disable=duplicate-code \
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
    --disable=len-as-condition \
    $PY_TEST_SOURCE

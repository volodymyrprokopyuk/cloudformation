#!/usr/bin/env bash

set -eu

SOURCE=sqs
TEST=$SOURCE/test
export PYTHONPATH=.

pytest -x -v -s --disable-pytest-warnings --cov $SOURCE --cov-report term --cov-report html $TEST

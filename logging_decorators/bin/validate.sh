#!/usr/bin/env bash

set -eux

TARGET=main.py

flake8 $TARGET
bandit $TARGET
radon cc $TARGET
pylint --max-line-length=120 $TARGET

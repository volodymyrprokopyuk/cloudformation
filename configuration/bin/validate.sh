#!/usr/bin/env bash

set -eux

SOURCE=*.py

flake8 $SOURCE
bandit $SOURCE
radon cc $SOURCE
pylint --max-line-length=120 $SOURCE || true

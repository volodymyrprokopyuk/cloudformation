#!/usr/bin/env bash

# Validate bash scripts
shellcheck -e SC2086 -e SC2155 -e SC2004 -e SC2231 -e SC2164 -e SC2148 bin/*.sh

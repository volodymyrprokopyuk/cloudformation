#!/usr/bin/env bash

set -eu

export ENV_SPECIFIC_CONFIG_OPTION_A="Environment specific configuration option A"
export ENV_SPECIFIC_CONFIG_OPTION_B="Environment specific configuration option B"

python main.py

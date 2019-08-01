#!/usr/bin/env bash

source ./bin/config.sh
source ./bin/util.sh

set $SETOPTS

# Validate Bash scripts
./bin/validate_sh_script.sh

# Validate CloudFormation templates
./bin/validate_cf_template.sh cloudformation/infringement_store.yaml
./bin/validate_cf_template.sh cloudformation/infringement_ingest.yaml
./bin/validate_cf_template.sh cloudformation/infringement_transform.yaml

# Validate Python code and tests
./bin/validate_py_code.sh

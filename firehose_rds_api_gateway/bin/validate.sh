#!/usr/bin/env bash

source ./bin/config.sh
source ./bin/util.sh

set $SETOPTS

cd $BIN_DIR
setup_virtual_environment $PYVENV
cd $ROOT_DIR

# Validate Bash scripts
./bin/validate_sh_script.sh

# Validate CloudFormation templates
./bin/validate_cf_template.sh $CF_DIR/infringement_store.yaml
./bin/validate_cf_template.sh $CF_DIR/infringement_ingest.yaml
./bin/validate_cf_template.sh $CF_DIR/infringement_transform.yaml
./bin/validate_cf_template.sh $CF_DIR/infringement_expose.yaml

# Validate Python code and tests
./bin/validate_py_code.sh

#!/usr/bin/env bash

source ./bin/config.sh
source ./bin/util.sh

set $SETOPTS

# ./bin/deploy_application.sh infringement-all

# ./bin/create_db_schema.sh
# ./bin/send_data_to_firehose.sh -p product*.txt -i infringement*.txt
# sleep 80

cd $TEST_DIR
setup_virtual_environment $PYVENV

readonly STACK_NAME=$APPLICATION-store-$ENVIRONMENT
readonly RDS_ENDPOINT_ADDRESS=$(get_cf_export_value $STACK_NAME:RdsEndpointAddress)
readonly BASTION_IP=$(get_cf_export_value $STACK_NAME:BastionEc2PublicIp)
readonly DB_RDS_PORT=$DB_LOCAL_PORT
# Create SSH tunnel to the RDS database instance
create_ssh_tunnel_if_not_exists $DB_TUNNEL_PORT $RDS_ENDPOINT_ADDRESS $DB_RDS_PORT \
    $BASTION_USER $BASTION_IP
readonly DB_BOUND_PORT=$DB_TUNNEL_PORT
set +e

# Database configuration
export DB_HOST
export DB_PORT=$DB_BOUND_PORT
export DB_NAME
export DB_USER=$DB_INGEST_USER
export DB_PASSWORD=$DB_INGEST_PASSWORD
export DB_CONNECT_TIMEOUT

export PYTHONPATH=$LAMBDA_LIB_DIR
pytest -x -v -s --disable-pytest-warnings $TEST_DIR/e2e_test.py
readonly TEST_RESULT=$?
unset PYTHONPATH

destroy_ssh_tunnel_if_exists $DB_TUNNEL_PORT $RDS_ENDPOINT_ADDRESS $DB_RDS_PORT \
    $BASTION_USER $BASTION_IP

# ./bin/undeploy_application.sh -y

exit $TEST_RESULT

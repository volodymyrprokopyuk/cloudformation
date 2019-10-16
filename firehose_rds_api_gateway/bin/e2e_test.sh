#!/usr/bin/env bash

source ./bin/config.sh
source ./bin/util.sh

set $SETOPTS

# Deploy application
# ./bin/deploy_application.sh infringement-all

# Create the database schema of the infirngement data import application
./bin/create_db_schema.sh

# Migrate the database schema of the infirngement data import application
./bin/migrate_db_schema.sh

# Import partner and pirate source data into the database
./bin/import_data_into_db.sh

# Import test data to Kinesis Firehose delivery streams
./bin/import_data_through_firehose.sh \
    --product $LAMBDA_TRANSFORM_DIR/PutProductInDbLambda/test/data/product_success.txt \
    --infringement $LAMBDA_TRANSFORM_DIR/PutInfringementInDbLambda/test/data/infringement_success.txt

sleep 80

# Create SSH tunnel to the RDS database instance
STACK_NAME=$APPLICATION-store-$ENVIRONMENT
readonly RDS_ENDPOINT_ADDRESS=$(get_cf_export_value $STACK_NAME:RdsEndpointAddress)
readonly BASTION_IP=$(get_cf_export_value $STACK_NAME:BastionEc2PublicIp)
STACK_NAME=$APPLICATION-expose-$ENVIRONMENT
export API=$(get_cf_export_value $STACK_NAME:ExposeInfringementDataRestApiRootUri)
readonly DB_RDS_PORT=$DB_LOCAL_PORT
create_ssh_tunnel_if_not_exists $DB_TUNNEL_PORT $RDS_ENDPOINT_ADDRESS $DB_RDS_PORT \
    $BASTION_USER $BASTION_IP
readonly DB_BOUND_PORT=$DB_TUNNEL_PORT
set +e

# Database configuration
export DB_HOST
export DB_PORT=$DB_BOUND_PORT
export DB_NAME
export DB_USER=$DB_SUPER_USER
export DB_PASSWORD=$DB_SUPER_PASSWORD
export DB_CONNECT_TIMEOUT

# Execute E2E test
cd $TEST_DIR
setup_virtual_environment $PYVENV
export PYTHONPATH=$LAMBDA_LIB_DIR
pytest -x -v -s --disable-pytest-warnings $TEST_DIR/e2e_test.py
readonly TEST_RESULT=$?
unset PYTHONPATH

# Destroy SSH tunnel to RDS database instance
destroy_ssh_tunnel_if_exists $DB_TUNNEL_PORT $RDS_ENDPOINT_ADDRESS $DB_RDS_PORT \
    $BASTION_USER $BASTION_IP

# Undeploy application
# ./bin/undeploy_application.sh -y

exit $TEST_RESULT

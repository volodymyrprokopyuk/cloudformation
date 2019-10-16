#!/usr/bin/env bash

source ./bin/config.sh
source ./bin/util.sh

set $SETOPTS

readonly USAGE="Usage: ./bin/import_data_into_db.sh [-l]"

readonly DIRECT_IMPORT_SCRIPT=$DIRECT_IMPORT_DIR/main.py

export DB_HOST
export DB_NAME
export DB_USER=$DB_INGEST_USER
export DB_PASSWORD=$DB_INGEST_PASSWORD
export DB_CONNECT_TIMEOUT

cd $DIRECT_IMPORT_DIR
setup_virtual_environment $PYVENV

if (( $# == 1 )) && [[ $1 != -l ]]; then
    echo $USAGE >&2
    exit 1
fi

# Target localhost database instance
if (( $# == 1 )) && [[ $1 == -l ]]; then
    readonly DB_BOUND_PORT=$DB_LOCAL_PORT
# Target RDS database instance
else
    # Create SSH tunnel to the RDS database instance
    readonly STACK_NAME=$APPLICATION-store-$ENVIRONMENT
    readonly RDS_ENDPOINT_ADDRESS=$(get_cf_export_value $STACK_NAME:RdsEndpointAddress)
    readonly BASTION_IP=$(get_cf_export_value $STACK_NAME:BastionEc2PublicIp)
    readonly DB_RDS_PORT=$DB_LOCAL_PORT
    create_ssh_tunnel_if_not_exists $DB_TUNNEL_PORT $RDS_ENDPOINT_ADDRESS $DB_RDS_PORT \
        $BASTION_USER $BASTION_IP
    readonly DB_BOUND_PORT=$DB_TUNNEL_PORT
fi
export DB_PORT=$DB_BOUND_PORT
set +e

# Import data into database
python $DIRECT_IMPORT_SCRIPT --partner $DIRECT_IMPORT_DIR/data/dummy_partner.txt
python $DIRECT_IMPORT_SCRIPT --pirate-source $DIRECT_IMPORT_DIR/data/dummy_pirate_source.txt
# python $DIRECT_IMPORT_SCRIPT --partner $DIRECT_IMPORT_DIR/data/production_partner.txt
# python $DIRECT_IMPORT_SCRIPT --pirate-source $DIRECT_IMPORT_DIR/data/smp_pirate_source.txt

# Destroy SSH tunnel to RDS database instance
if (( $# == 0 )); then
    destroy_ssh_tunnel_if_exists $DB_TUNNEL_PORT $RDS_ENDPOINT_ADDRESS $DB_RDS_PORT \
        $BASTION_USER $BASTION_IP
fi

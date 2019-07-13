#!/usr/bin/env bash

source ./bin/config.sh
source ./bin/util.sh

set $SETOPTS

readonly USAGE="./bin/connect_to_db.sh [-l]"

readonly DB_HOST=localhost

if (( $# == 1 )) && [[ $1 != -l ]]; then
    echo $USAGE >&2
    exit 1
fi

# Target localhost database instance
if (( $# == 1 )) && [[ $1 == -l ]]; then
    readonly DB_BOUND_PORT=$DB_PORT
# Target RDS database instance
else
    readonly STACK_NAME=$APPLICATION-store-$ENVIRONMENT
    readonly RDS_ENDPOINT_ADDRESS=$(get_cf_export_value $STACK_NAME:RdsEndpointAddress)
    readonly BASTION_IP=$(get_cf_export_value $STACK_NAME:BastionEc2PublicIp)
    # Create SSH tunnel to the RDS database instance
    if ! is_ssh_tunnel_created \
        $DB_LOCAL_PORT $RDS_ENDPOINT_ADDRESS $DB_PORT $BASTION_USER $BASTION_IP; then
        create_ssh_tunnel $DB_LOCAL_PORT $RDS_ENDPOINT_ADDRESS $DB_PORT $BASTION_USER $BASTION_IP
    fi
    readonly DB_BOUND_PORT=$DB_LOCAL_PORT
fi
set +e

# Open an interactive session to the localhost or the RDS database instance
export PGPASSWORD=$DB_SUPER_PASSWORD
pgcli -h $DB_HOST -p $DB_BOUND_PORT $DB_NAME $DB_SUPER_USER

# Destroy SSH tunnel to RDS database instance
if (( $# == 0 )); then
    if is_ssh_tunnel_created \
        $DB_LOCAL_PORT $RDS_ENDPOINT_ADDRESS $DB_PORT $BASTION_USER $BASTION_IP; then
        destroy_ssh_tunnel $DB_LOCAL_PORT $RDS_ENDPOINT_ADDRESS $DB_PORT $BASTION_USER $BASTION_IP
    fi
fi

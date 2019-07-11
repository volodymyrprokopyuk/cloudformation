#!/usr/bin/env bash

source ./bin/config.sh
source ./bin/util.sh

set $SETOPTS

set +u
# Target localhost database instance
if [[ $1 == -l ]]; then
    readonly DB_HOST=localhost
# Get RDS endpoint address from the CloudFormation Exports
else
    readonly RDS_ENDPOINT_ADDRESS_EXPORT_NAME=$APPLICATION-store-$ENVIRONMENT:RdsEndpointAddress
    readonly DB_HOST=$(
        get_cf_export_value $RDS_ENDPOINT_ADDRESS_EXPORT_NAME
    )
fi
set -u

# Open an interactive session with the database
export PGPASSWORD=$DB_SUPER_PASSWORD
pgcli -h $DB_HOST -p $DB_PORT $DB_NAME $DB_SUPER_USER

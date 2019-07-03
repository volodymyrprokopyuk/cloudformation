#!/usr/bin/env bash

set -ex

source ./bin/config.sh
source ./bin/util.sh

# Target localhost
if [[ $1 == -l ]]; then
    readonly DB_HOST=localhost
# Get RDS endpoint address from CloudFormation Exports
else
    readonly RDS_ENDPOINT_ADDRESS_EXPORT_NAME=$APPLICATION-store-$ENVIRONMENT:RdsEndpointAddress
    readonly DB_HOST=$(
        get_cf_export_value $RDS_ENDPOINT_ADDRESS_EXPORT_NAME
    )
fi

readonly DB_DIR=$(pwd)/database
readonly DB_SCHEMA_FILE=$DB_DIR/database_schema.sql
readonly SQL_DROP_DB="DROP DATABASE IF EXISTS $DB_NAME"
readonly SQL_CREATE_DB="CREATE DATABASE $DB_NAME WITH OWNER $DB_USER;"

export PGPASSWORD=$DB_PASSWORD

# Drop and recreate the database schema. Sotre initial data in the database
psql -h $DB_HOST -p $DB_PORT -c "${SQL_DROP_DB}" postgres $DB_USER
psql -h $DB_HOST -p $DB_PORT -c "${SQL_CREATE_DB}" postgres $DB_USER
psql -h $DB_HOST -p $DB_PORT -f $DB_SCHEMA_FILE -v ON_ERROR_STOP=1 $DB_NAME $DB_USER
# Open an interactive session with the database
pgcli -h $DB_HOST -p $DB_PORT $DB_NAME $DB_USER

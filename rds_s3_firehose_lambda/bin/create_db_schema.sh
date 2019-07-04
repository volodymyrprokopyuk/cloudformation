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
readonly DB_DATA_FILE=$DB_DIR/initial_data.sql
readonly DB_USER_FILE=$DB_DIR/database_user.sql

cat > $DB_USER_FILE <<EOF
-- Create ingest_role with privileges
CREATE ROLE ingest_role;
GRANT USAGE ON SCHEMA ingest TO ingest_role;
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA ingest TO ingest_role;
GRANT ALL ON ALL SEQUENCES IN SCHEMA ingest TO ingest_role;

-- Create ingest user and grant him ingest_role privileges
CREATE ROLE ingest WITH PASSWORD '$DB_INGEST_PASSWORD' LOGIN;
GRANT ingest_role TO ingest;
EOF

readonly SQL_DROP_DB="DROP DATABASE IF EXISTS $DB_NAME;"
readonly SQL_DROP_ROLE="DROP ROLE IF EXISTS ingest, ingest_role;"
readonly SQL_CREATE_DB="CREATE DATABASE $DB_NAME WITH OWNER $DB_SUPER_USER;"

# Drop and recreate the database schema. Sotre initial data in the database
export PGPASSWORD=$DB_SUPER_PASSWORD
psql -h $DB_HOST -p $DB_PORT -c "${SQL_DROP_DB}" postgres $DB_SUPER_USER
psql -h $DB_HOST -p $DB_PORT -c "${SQL_DROP_ROLE}" postgres $DB_SUPER_USER
psql -h $DB_HOST -p $DB_PORT -c "${SQL_CREATE_DB}" postgres $DB_SUPER_USER
psql -h $DB_HOST -p $DB_PORT -f $DB_SCHEMA_FILE -v ON_ERROR_STOP=1 $DB_NAME $DB_SUPER_USER
psql -h $DB_HOST -p $DB_PORT -f $DB_DATA_FILE -v ON_ERROR_STOP=1 $DB_NAME $DB_SUPER_USER
psql -h $DB_HOST -p $DB_PORT -f $DB_USER_FILE -v ON_ERROR_STOP=1 $DB_NAME $DB_SUPER_USER
rm -f $DB_USER_FILE
# Open an interactive session with the database
pgcli -h $DB_HOST -p $DB_PORT $DB_NAME $DB_SUPER_USER

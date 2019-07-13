#!/usr/bin/env bash

source ./bin/config.sh
source ./bin/util.sh

set $SETOPTS

readonly USAGE="./bin/create_db_schema.sh [-l]"

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

# Drop and recreate the database schema and roles. Sotre initial data in the database
export PGPASSWORD=$DB_SUPER_PASSWORD
psql -h $DB_HOST -p $DB_BOUND_PORT -c "${SQL_DROP_DB}" postgres $DB_SUPER_USER
psql -h $DB_HOST -p $DB_BOUND_PORT -c "${SQL_DROP_ROLE}" postgres $DB_SUPER_USER
psql -h $DB_HOST -p $DB_BOUND_PORT -c "${SQL_CREATE_DB}" postgres $DB_SUPER_USER
psql -h $DB_HOST -p $DB_BOUND_PORT -f $DB_SCHEMA_FILE -v ON_ERROR_STOP=1 $DB_NAME $DB_SUPER_USER
psql -h $DB_HOST -p $DB_BOUND_PORT -f $DB_DATA_FILE -v ON_ERROR_STOP=1 $DB_NAME $DB_SUPER_USER
psql -h $DB_HOST -p $DB_BOUND_PORT -f $DB_USER_FILE -v ON_ERROR_STOP=1 $DB_NAME $DB_SUPER_USER
rm -f $DB_USER_FILE

# Destroy SSH tunnel to RDS database instance
if (( $# == 0 )); then
    if is_ssh_tunnel_created \
        $DB_LOCAL_PORT $RDS_ENDPOINT_ADDRESS $DB_PORT $BASTION_USER $BASTION_IP; then
        destroy_ssh_tunnel $DB_LOCAL_PORT $RDS_ENDPOINT_ADDRESS $DB_PORT $BASTION_USER $BASTION_IP
    fi
fi

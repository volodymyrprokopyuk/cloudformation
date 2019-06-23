#!/usr/bin/env bash

set -ex

source ./bin/config.sh

# localhost [-l] otherwise RDS Endpoint.Address from ./bin/config.sh
if [[ $1 == -l ]]; then
    DB_HOST=localhost
fi

readonly SQL_DROP_DB="DROP DATABASE IF EXISTS $DB_NAME"
readonly SQL_CREATE_DB="CREATE DATABASE $DB_NAME WITH OWNER $DB_USER;"
readonly DB_SCHEMA_FILE=$(pwd)/database/database_schema.sql

export PGPASSWORD=$DB_PASSWORD

psql -h $DB_HOST -p $DB_PORT -c "${SQL_DROP_DB}" postgres $DB_USER
psql -h $DB_HOST -p $DB_PORT -c "${SQL_CREATE_DB}" postgres $DB_USER
psql -h $DB_HOST -p $DB_PORT -f $DB_SCHEMA_FILE -v ON_ERROR_STOP=1 $DB_NAME $DB_USER
pgcli -h $DB_HOST -p $DB_PORT $DB_NAME $DB_USER

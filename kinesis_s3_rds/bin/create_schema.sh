#!/usr/bin/env bash

set -ex

case $1 in
    -l)
        # localhost
        DB_HOST=localhost
        DB_PORT=5432
        DB_NAME=infringement
        DB_USER=vld
        DB_PASSWORD='vld'
        ;;
    *)
        # RDS
        DB_HOST=vp1smu6gpm7hfky.c07z8n4r5v4a.eu-central-1.rds.amazonaws.com
        DB_PORT=5432
        DB_NAME=infringement
        DB_USER=vld
        DB_PASSWORD='Password1!'
        ;;
esac

SQL_DROP_DB="DROP DATABASE IF EXISTS $DB_NAME"
SQL_CREATE_DB="CREATE DATABASE $DB_NAME WITH OWNER $DB_USER;"
DB_SCHEMA_FILE=database_schema.sql

export PGPASSWORD=$DB_PASSWORD

psql -h $DB_HOST -p $DB_PORT -c "${SQL_DROP_DB}" postgres $DB_USER
psql -h $DB_HOST -p $DB_PORT -c "${SQL_CREATE_DB}" postgres $DB_USER
psql -h $DB_HOST -p $DB_PORT -f $DB_SCHEMA_FILE -v ON_ERROR_STOP=1 $DB_NAME $DB_USER
pgcli -h $DB_HOST -p $DB_PORT $DB_NAME $DB_USER

#!/usr/bin/env bash

set -eux

DB_NAME=infringement
DB_USER=vld
SQL_DROP_DB="DROP DATABASE IF EXISTS $DB_NAME"
SQL_CREATE_DB="CREATE DATABASE $DB_NAME WITH OWNER $DB_USER;"
DB_SCHEMA_FILE=database_schema.sql

psql -c "${SQL_DROP_DB}" postgres $DB_USER
psql -c "${SQL_CREATE_DB}" postgres $DB_USER
psql -f $DB_SCHEMA_FILE -v ON_ERROR_STOP=1 $DB_NAME $DB_USER
pgcli $DB_NAME $DB_USER

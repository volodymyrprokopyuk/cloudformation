#!/usr/bin/env bash

source ./bin/config.sh
source ./bin/util.sh

set $SETOPTS

readonly USAGE="./bin/migrate_db_schema.sh [-l]"

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

function get_last_migration_from_db {
    psql -qtAX -h $DB_HOST -p $DB_BOUND_PORT \
        -c "SELECT * FROM migration.get_last_migration();" \
        -v ON_ERROR_STOP=1 $DB_NAME $DB_SUPER_USER
}

function apply_migrations_to_db {
    local last_migration=${1?ERROR: mandatory last_migration is not provided}

    set +e
    for migration in $DB_MIGRATION_DIR/????-*.sql; do
        if [[ ${migration##*/} > $last_migration ]]; then
            # Apply a migration to a database
            if ! psql -h $DB_HOST -p $DB_BOUND_PORT -f $migration \
                -v ON_ERROR_STOP=1 $DB_NAME $DB_SUPER_USER; then
                break
            fi
            # Track successful migratio application in migration table
            psql -h $DB_HOST -p $DB_BOUND_PORT \
                -c "SELECT migration.put_last_migration('${migration##*/}');" \
                -v ON_ERROR_STOP=1 $DB_NAME $DB_SUPER_USER
        fi
    done
    set -e
}

# Apply pending migrations to the database
export PGPASSWORD=$DB_SUPER_PASSWORD
readonly LAST_MIGRATION=$(get_last_migration_from_db)
apply_migrations_to_db $LAST_MIGRATION

# Destroy SSH tunnel to RDS database instance
if (( $# == 0 )); then
    destroy_ssh_tunnel_if_exists $DB_TUNNEL_PORT $RDS_ENDPOINT_ADDRESS $DB_RDS_PORT \
        $BASTION_USER $BASTION_IP
fi

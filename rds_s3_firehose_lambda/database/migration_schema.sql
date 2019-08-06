-- migration schema
CREATE SCHEMA migration;

-- Relations
CREATE TABLE migration.migration (
    migration_name varchar(100) NOT NULL,
    migration_ts timestamptz NOT NULL
        DEFAULT date_trunc('milliseconds', current_timestamp),
    CONSTRAINT uq_migration
        UNIQUE (migration_name)
);

-- Functions
CREATE OR REPLACE FUNCTION migration.put_last_migration(
    a_migration_name varchar(100)
)
RETURNS varchar(100)
LANGUAGE sql AS $$
    INSERT INTO migration.migration (migration_name)
    VALUES (a_migration_name)
    RETURNING migration_name;
$$;

CREATE OR REPLACE FUNCTION migration.get_last_migration()
RETURNS varchar(100)
LANGUAGE sql AS $$
    SELECT m.migration_name
    FROM migration.migration m
    ORDER BY m.migration_name DESC
    LIMIT 1;
$$;

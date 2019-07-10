-- ingest schema
CREATE SCHEMA ingest;

-- Relations and types
CREATE TABLE ingest.product (
    product_id serial NOT NULL,
    product_external_id varchar(20) NOT NULL,
    product_title varchar(100) NOT NULL,
    first_protection_ts timestamptz NOT NULL,
    product_image_url varchar(500),
    CONSTRAINT pk_product
        PRIMARY KEY (product_id),
    CONSTRAINT uq_product_product_external_id
        UNIQUE (product_external_id),
    CONSTRAINT ck_product_product_title
        CHECK (length(product_title) >= 3),
    CONSTRAINT ck_product_product_image_url
        CHECK (product_image_url IS NULL OR length(product_image_url) >= 3)
);

CREATE TYPE ingest.protection_status_t AS
    ENUM ('ACTIVE', 'INACTIVE');

CREATE TABLE ingest.protection_result (
    product_id integer NOT NULL,
    registration_ts timestamptz NOT NULL,
    protection_status ingest.protection_status_t NOT NULL,
    CONSTRAINT uq_protection_result_product_id_registration_ts
        UNIQUE (product_id, registration_ts),
    CONSTRAINT fk_protection_result_product_id
        FOREIGN KEY (product_id) REFERENCES ingest.product (product_id)
        ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TYPE ingest.pirate_source_name_t AS
    ENUM ('GOOGLE', 'FACEBOOK', 'TWITTER');

CREATE TYPE ingest.pirate_source_t AS
    ENUM ('SEARCH_ENGINE', 'SOCIAL_MEDIA');

CREATE TABLE ingest.pirate_source (
    pirate_source_id serial NOT NULL,
    pirate_source_external_id varchar(20) NOT NULL,
    pirate_source_name ingest.pirate_source_name_t NOT NULL,
    pirate_source_type ingest.pirate_source_t NOT NULL,
    registration_ts timestamptz NOT NULL,
    CONSTRAINT pk_pirate_source
        PRIMARY KEY (pirate_source_id),
    CONSTRAINT uq_pirate_source_pirate_source_external_id
        UNIQUE (pirate_source_external_id),
    CONSTRAINT uq_pirate_source_pirate_source_name_pirate_source_type
        UNIQUE (pirate_source_name, pirate_source_type)
);

CREATE TABLE ingest.search_engine_pirate_source (
    pirate_source_id integer NOT NULL,
    pirate_source_domain varchar(50) NOT NULL,
    CONSTRAINT uq_search_engine_pirate_source_pirate_source_id
        UNIQUE (pirate_source_id),
    CONSTRAINT uq_search_engine_pirate_source_pirate_source_domain
        UNIQUE (pirate_source_domain),
    CONSTRAINT fk_search_engine_pirate_source_pirate_source_id
        FOREIGN KEY (pirate_source_id) REFERENCES ingest.pirate_source (pirate_source_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT ck_search_engine_pirate_source_pirate_source_domain
        CHECK (length(pirate_source_domain) >= 3)
);

CREATE TABLE ingest.social_media_pirate_source (
    pirate_source_id integer NOT NULL,
    pirate_source_domain varchar(50) NOT NULL,
    CONSTRAINT uq_social_media_pirate_source_pirate_source_id
        UNIQUE (pirate_source_id),
    CONSTRAINT uq_social_media_pirate_source_pirate_source_domain
        UNIQUE (pirate_source_domain),
    CONSTRAINT fk_social_media_pirate_source_pirate_source_id
        FOREIGN KEY (pirate_source_id) REFERENCES ingest.pirate_source (pirate_source_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT ck_social_media_pirate_source_pirate_source_domain
        CHECK (length(pirate_source_domain) >= 3)
);

CREATE TYPE ingest.infringement_status_t AS
    ENUM ('ACTIVE', 'TAKEN_DOWN');

CREATE TABLE ingest.infringement (
    infringement_id serial NOT NULL,
    product_id integer NOT NULL,
    pirate_source_id integer NOT NULL,
    detection_ts timestamptz NOT NULL,
    infringement_url varchar(500) NOT NULL,
    infringement_status ingest.infringement_status_t NOT NULL,
    CONSTRAINT pk_infringement
        PRIMARY KEY (infringement_id),
    CONSTRAINT uq_infringement_product_id_pirate_source_id_detection_ts_url
        UNIQUE (product_id, pirate_source_id, detection_ts, infringement_url),
    CONSTRAINT fk_infringement_product_id
        FOREIGN KEY (product_id) REFERENCES ingest.product (product_id)
        ON DELETE RESTRICT ON UPDATE RESTRICT,
    CONSTRAINT fk_infringement_pirate_source_id
        FOREIGN KEY (pirate_source_id) REFERENCES ingest.pirate_source (pirate_source_id)
        ON DELETE RESTRICT ON UPDATE RESTRICT,
    CONSTRAINT ck_infringement_infringement_url
        CHECK (length(infringement_url) >= 3)
);

CREATE TYPE ingest.document_status_t AS
    ENUM ('SUCCESS', 'FAILURE');

CREATE TABLE ingest.document_statistics (
    document_statistics_id serial NOT NULL,
    document_name varchar(300) NOT NULL,
    registration_ts timestamptz NOT NULL
        DEFAULT date_trunc('milliseconds', current_timestamp),
    document_status ingest.document_status_t NOT NULL,
    status_reason jsonb,
    total_records integer NOT NULL DEFAULT 0,
    success_records integer NOT NULL DEFAULT 0,
    failure_records integer NOT NULL DEFAULT 0,
    CONSTRAINT pk_document_statistics
        PRIMARY KEY (document_statistics_id),
    CONSTRAINT ck_document_statistics_status_reason
        CHECK (
            (document_status = 'SUCCESS' AND status_reason IS NULL)
            OR
            (document_status = 'FAILURE' AND status_reason IS NOT NULL)
        ),
    CONSTRAINT ck_document_statistics_total_records
        CHECK (total_records = success_records + failure_records)
);

-- Functions
CREATE OR REPLACE FUNCTION ingest.put_pirate_source(
    a_pirate_source_external_id varchar(20),
    a_pirate_source_name ingest.pirate_source_name_t,
    a_pirate_source_type ingest.pirate_source_t,
    a_registration_ts timestamptz
)
RETURNS integer
LANGUAGE sql AS $$
    INSERT INTO ingest.pirate_source (
        pirate_source_external_id,
        pirate_source_name,
        pirate_source_type,
        registration_ts
    ) VALUES (
        a_pirate_source_external_id,
        a_pirate_source_name,
        a_pirate_source_type,
        a_registration_ts
    )
    ON CONFLICT ON CONSTRAINT uq_pirate_source_pirate_source_external_id
    DO UPDATE SET
        pirate_source_name = excluded.pirate_source_name,
        pirate_source_type = excluded.pirate_source_type,
        registration_ts = excluded.registration_ts
    RETURNING pirate_source_id;
$$;

CREATE OR REPLACE FUNCTION ingest.put_product(
    a_product_external_id varchar(20),
    a_product_title varchar(100),
    a_first_protection_ts timestamptz,
    a_registration_ts timestamptz,
    a_protection_status ingest.protection_status_t,
    a_product_image_url varchar(500) DEFAULT NULL
)
RETURNS integer
LANGUAGE sql AS $$
    WITH inserted_product AS (
        INSERT INTO ingest.product (
            product_external_id,
            product_title,
            first_protection_ts,
            product_image_url
        ) VALUES (
            a_product_external_id,
            a_product_title,
            a_first_protection_ts,
            a_product_image_url
        )
        ON CONFLICT ON CONSTRAINT uq_product_product_external_id
        DO UPDATE SET
            product_title = excluded.product_title,
            first_protection_ts = excluded.first_protection_ts,
            product_image_url = excluded.product_image_url
        RETURNING product_id
    )
    INSERT INTO ingest.protection_result (product_id, registration_ts, protection_status)
    SELECT product_id, a_registration_ts, a_protection_status
    FROM inserted_product
    ON CONFLICT ON CONSTRAINT uq_protection_result_product_id_registration_ts
    DO UPDATE SET
        protection_status = excluded.protection_status
    RETURNING product_id;
$$;

CREATE OR REPLACE FUNCTION ingest.put_infringement(
    a_product_external_id varchar(20),
    a_pirate_source_external_id varchar(20),
    a_detection_ts timestamptz,
    a_infringement_url varchar(500),
    a_infringement_status ingest.infringement_status_t
)
RETURNS integer
LANGUAGE sql AS $$
    WITH infringement_product AS (
        SELECT product_id
        FROM ingest.product
        WHERE product_external_id = a_product_external_id
    ),
    infringement_pirate_source AS (
        SELECT pirate_source_id
        FROM ingest.pirate_source
        WHERE pirate_source_external_id = a_pirate_source_external_id
    )
    INSERT INTO ingest.infringement (
        product_id,
        pirate_source_id,
        detection_ts,
        infringement_url,
        infringement_status
    )
    SELECT
        infringement_product.product_id,
        infringement_pirate_source.pirate_source_id,
        a_detection_ts,
        a_infringement_url,
        a_infringement_status
    FROM infringement_product, infringement_pirate_source
    ON CONFLICT ON CONSTRAINT uq_infringement_product_id_pirate_source_id_detection_ts_url
    DO UPDATE SET
        infringement_status = excluded.infringement_status
    RETURNING infringement_id;
$$;

CREATE OR REPLACE FUNCTION ingest.put_document_statistics(
    a_document_name varchar(300),
    a_document_status ingest.document_status_t,
    a_total_records integer,
    a_success_records integer,
    a_failure_records integer,
    a_status_reason jsonb DEFAULT NULL
)
RETURNS integer
LANGUAGE sql AS $$
    INSERT INTO ingest.document_statistics(
        document_name,
        document_status,
        total_records,
        success_records,
        failure_records,
        status_reason
    ) VALUES (
        a_document_name,
        a_document_status,
        a_total_records,
        a_success_records,
        a_failure_records,
        a_status_reason
    )
    RETURNING document_statistics_id;
$$

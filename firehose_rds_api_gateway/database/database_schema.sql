-- ingest schema
CREATE SCHEMA ingest;

-- Relations and types
CREATE TYPE ingest.partner_status_t AS
    ENUM ('ACTIVE', 'INACTIVE');

CREATE TABLE ingest.partner (
    partner_id serial NOT NULL,
    partner_uuid uuid NOT NULL,
    partner_name varchar(100) NOT NULL,
    partner_status ingest.partner_status_t NOT NULL,
    registration_ts timestamptz NOT NULL,
    creation_ts timestamptz NOT NULL
        DEFAULT date_trunc('milliseconds', current_timestamp),
    update_ts timestamptz NOT NULL
        DEFAULT date_trunc('milliseconds', current_timestamp),
    CONSTRAINT pk_partner
        PRIMARY KEY (partner_id),
    CONSTRAINT uq_partner_partner_uuid
        UNIQUE (partner_uuid),
    CONSTRAINT ck_partner_partner_name
        CHECK (length(partner_name) > 1)
);

CREATE TABLE ingest.product (
    product_id serial NOT NULL,
    partner_id integer NOT NULL,
    product_external_id varchar(50) NOT NULL,
    product_title varchar(100) NOT NULL,
    first_protection_ts timestamptz NOT NULL,
    product_image_url varchar(500),
    creation_ts timestamptz NOT NULL
        DEFAULT date_trunc('milliseconds', current_timestamp),
    update_ts timestamptz NOT NULL
        DEFAULT date_trunc('milliseconds', current_timestamp),
    CONSTRAINT pk_product
        PRIMARY KEY (product_id),
    CONSTRAINT uq_product_partner_id_product_external_id
        UNIQUE (partner_id, product_external_id),
    CONSTRAINT ck_product_product_title
        CHECK (length(product_title) > 1),
    CONSTRAINT ck_product_product_image_url
        CHECK (product_image_url IS NULL OR length(product_image_url) > 7),
    CONSTRAINT fk_product_partner_id
        FOREIGN KEY (partner_id) REFERENCES ingest.partner (partner_id)
        ON DELETE CASCADE ON UPDATE CASCADE
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

CREATE TABLE ingest.pirate_source (
    pirate_source_id serial NOT NULL,
    partner_id integer NOT NULL,
    pirate_source_external_id varchar(50) NOT NULL,
    pirate_source_name varchar(50) NOT NULL,
    pirate_source_type varchar(50) NOT NULL,
    registration_ts timestamptz NOT NULL,
    creation_ts timestamptz NOT NULL
        DEFAULT date_trunc('milliseconds', current_timestamp),
    update_ts timestamptz NOT NULL
        DEFAULT date_trunc('milliseconds', current_timestamp),
    CONSTRAINT pk_pirate_source
        PRIMARY KEY (pirate_source_id),
    CONSTRAINT uq_pirate_source_partner_id_pirate_source_external_id
        UNIQUE (partner_id, pirate_source_external_id),
    CONSTRAINT uq_pirate_source_pirate_source_name_pirate_source_type
        UNIQUE (partner_id, pirate_source_name, pirate_source_type),
    CONSTRAINT fk_pirate_source_partner_id
        FOREIGN KEY (partner_id) REFERENCES ingest.partner (partner_id)
        ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TYPE ingest.infringement_status_t AS
    ENUM ('ACTIVE', 'TAKEN_DOWN');

CREATE TABLE ingest.infringement (
    infringement_id serial NOT NULL,
    product_id integer NOT NULL,
    pirate_source_id integer NOT NULL,
    detection_ts timestamptz NOT NULL,
    infringement_url varchar(500) NOT NULL,
    infringement_screenshot jsonb,
    infringement_status ingest.infringement_status_t NOT NULL,
    creation_ts timestamptz NOT NULL
        DEFAULT date_trunc('milliseconds', current_timestamp),
    update_ts timestamptz NOT NULL
        DEFAULT date_trunc('milliseconds', current_timestamp),
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
        CHECK (length(infringement_url) > 7),
    CONSTRAINT ck_infringement_infringement_screenshot
        CHECK (infringement_screenshot IS NULL
            OR (infringement_screenshot ? 'screenshotUrl'
                AND jsonb_typeof(infringement_screenshot->'screenshotUrl') = 'array'
                AND jsonb_array_length(infringement_screenshot->'screenshotUrl') > 0
            )
        )
);

CREATE TYPE ingest.document_status_t AS
    ENUM ('SUCCESS', 'FAILURE');

CREATE TABLE ingest.document_statistics (
    document_statistics_id serial NOT NULL,
    document_name varchar(300) NOT NULL,
    creation_ts timestamptz NOT NULL
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

-- Put functions
CREATE OR REPLACE FUNCTION ingest.put_partner(
    a_partner_uuid uuid,
    a_partner_name varchar(100),
    a_partner_status ingest.partner_status_t,
    a_registration_ts timestamptz
)
RETURNS integer
LANGUAGE sql AS $$
    INSERT INTO ingest.partner (
        partner_uuid,
        partner_name,
        partner_status,
        registration_ts
    ) VALUES (
        a_partner_uuid,
        a_partner_name,
        a_partner_status,
        a_registration_ts
    )
    ON CONFLICT ON CONSTRAINT uq_partner_partner_uuid
    DO UPDATE SET
        partner_name = excluded.partner_name,
        partner_status = excluded.partner_status,
        registration_ts = excluded.registration_ts,
        update_ts = date_trunc('milliseconds', current_timestamp)
    RETURNING partner_id;
$$;

CREATE OR REPLACE FUNCTION ingest.put_product(
    a_partner_uuid uuid,
    a_product_external_id varchar(50),
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
            partner_id,
            product_external_id,
            product_title,
            first_protection_ts,
            product_image_url
        ) VALUES (
            (SELECT partner_id FROM ingest.partner WHERE partner_uuid = a_partner_uuid),
            a_product_external_id,
            a_product_title,
            a_first_protection_ts,
            a_product_image_url
        )
        ON CONFLICT ON CONSTRAINT uq_product_partner_id_product_external_id
        DO UPDATE SET
            product_title = excluded.product_title,
            first_protection_ts = excluded.first_protection_ts,
            product_image_url = excluded.product_image_url,
            update_ts = date_trunc('milliseconds', current_timestamp)
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

CREATE OR REPLACE FUNCTION ingest.put_pirate_source(
    a_partner_uuid uuid,
    a_pirate_source_external_id varchar(50),
    a_pirate_source_name varchar(50),
    a_pirate_source_type varchar(50),
    a_registration_ts timestamptz
)
RETURNS integer
LANGUAGE sql AS $$
    INSERT INTO ingest.pirate_source (
        partner_id,
        pirate_source_external_id,
        pirate_source_name,
        pirate_source_type,
        registration_ts
    ) VALUES (
        (SELECT partner_id FROM ingest.partner WHERE partner_uuid = a_partner_uuid),
        a_pirate_source_external_id,
        a_pirate_source_name,
        a_pirate_source_type,
        a_registration_ts
    )
    ON CONFLICT ON CONSTRAINT uq_pirate_source_partner_id_pirate_source_external_id
    DO UPDATE SET
        pirate_source_name = excluded.pirate_source_name,
        pirate_source_type = excluded.pirate_source_type,
        registration_ts = excluded.registration_ts,
        update_ts = date_trunc('milliseconds', current_timestamp)
    RETURNING pirate_source_id;
$$;

CREATE OR REPLACE FUNCTION ingest.put_infringement(
    a_partner_uuid uuid,
    a_product_external_id varchar(50),
    a_pirate_source_external_id varchar(50),
    a_detection_ts timestamptz,
    a_infringement_url varchar(500),
    a_infringement_status ingest.infringement_status_t,
    a_infringement_screenshot jsonb DEFAULT NULL
)
RETURNS integer
LANGUAGE sql AS $$
    INSERT INTO ingest.infringement (
        product_id,
        pirate_source_id,
        detection_ts,
        infringement_url,
        infringement_screenshot,
        infringement_status
    ) VALUES (
        (SELECT p.product_id FROM ingest.product p
             JOIN ingest.partner pt ON pt.partner_id = p.partner_id
         WHERE pt.partner_uuid = a_partner_uuid
             and p.product_external_id = a_product_external_id),
        (SELECT ps.pirate_source_id FROM ingest.pirate_source ps
             JOIN ingest.partner pt ON pt.partner_id = ps.partner_id
         WHERE pt.partner_uuid = a_partner_uuid
             AND ps.pirate_source_external_id = a_pirate_source_external_id),
        a_detection_ts,
        a_infringement_url,
        a_infringement_screenshot,
        a_infringement_status
    )
    ON CONFLICT ON CONSTRAINT uq_infringement_product_id_pirate_source_id_detection_ts_url
    DO UPDATE SET
        infringement_screenshot = excluded.infringement_screenshot,
        infringement_status = excluded.infringement_status,
        update_ts = date_trunc('milliseconds', current_timestamp)
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
$$;

-- Get functions
CREATE OR REPLACE FUNCTION ingest.get_partner(
    a_partner_id integer DEFAULT NULL,
    a_partner_uuid uuid DEFAULT NULL,
    a_partner_name varchar(100) DEFAULT NULL,
    a_partner_status ingest.partner_status_t DEFAULT NULL
)
RETURNS TABLE (
    partner_id integer,
    partner_uuid uuid,
    partner_name varchar(100),
    partner_status ingest.partner_status_t,
    registration_ts timestamptz
)
LANGUAGE sql AS $$
    SELECT p.partner_id,
        p.partner_uuid,
        p.partner_name,
        p.partner_status,
        p.registration_ts
    FROM ingest.partner p
    WHERE (a_partner_id IS NULL OR p.partner_id = a_partner_id)
        AND (a_partner_uuid IS NULL OR p.partner_uuid = a_partner_uuid)
        AND (a_partner_name IS NULL
            OR p.partner_name ~* ('.*' || a_partner_name || '.*')
        )
        AND (a_partner_status IS NULL OR p.partner_status = a_partner_status);
$$;

CREATE OR REPLACE FUNCTION ingest.get_product(
    a_partner_id integer DEFAULT NULL,
    a_product_id integer DEFAULT NULL,
    a_product_title varchar(100) DEFAULT NULL,
    a_protection_status ingest.protection_status_t DEFAULT NULL
)
RETURNS TABLE (
    product_id integer,
    product_title varchar(100),
    product_image_url varchar(500),
    protection_status ingest.protection_status_t,
    first_protection_ts timestamptz,
    registration_ts timestamptz,
    partner_id integer,
    partner_uuid uuid,
    partner_name varchar(100)
)
LANGUAGE sql AS $$
    SELECT p.product_id,
        p.product_title,
        p.product_image_url,
        pr.protection_status,
        p.first_protection_ts,
        pr.registration_ts,
        pt.partner_id,
        pt.partner_uuid,
        pt.partner_name
    FROM ingest.product p
        JOIN ingest.partner pt ON pt.partner_id = p.partner_id
        JOIN ingest.protection_result pr ON pr.product_id = p.product_id
    WHERE pr.registration_ts IN (
            SELECT max(lpr.registration_ts) last_protection_ts
            FROM ingest.protection_result lpr
            WHERE lpr.product_id = p.product_id
        )
        AND (a_partner_id IS NULL OR pt.partner_id = a_partner_id)
        AND (a_product_id IS NULL OR p.product_id = a_product_id)
        AND (a_product_title IS NULL
            OR p.product_title ~* ('.*' || a_product_title || '.*')
        )
        AND (a_protection_status IS NULL OR pr.protection_status = a_protection_status);
$$;

CREATE OR REPLACE FUNCTION ingest.get_pirate_source(
    a_partner_id integer DEFAULT NULL,
    a_pirate_source_id integer DEFAULT NULL,
    a_pirate_source_name varchar(50) DEFAULT NULL,
    a_pirate_source_type varchar(50) DEFAULT NULL
)
RETURNS TABLE (
    pirate_source_id integer,
    pirate_source_name varchar(50),
    pirate_source_type varchar(50),
    registration_ts timestamptz,
    partner_id integer,
    partner_uuid uuid,
    partner_name varchar(100)
)
LANGUAGE sql AS $$
    SELECT ps.pirate_source_id,
        ps.pirate_source_name,
        ps.pirate_source_type,
        ps.registration_ts,
        pt.partner_id,
        pt.partner_uuid,
        pt.partner_name
    FROM ingest.pirate_source ps
        JOIN ingest.partner pt ON pt.partner_id = ps.partner_id
    WHERE (a_partner_id IS NULL OR pt.partner_id = a_partner_id)
        AND (a_pirate_source_id IS NULL OR ps.pirate_source_id = a_pirate_source_id)
        AND (a_pirate_source_name IS NULL
            OR ps.pirate_source_name ~* ('.*' || a_pirate_source_name || '.*')
        )
        AND (a_pirate_source_type IS NULL OR ps.pirate_source_type = a_pirate_source_type);
$$;

CREATE OR REPLACE FUNCTION ingest.get_infringement(
    a_partner_id integer DEFAULT NULL,
    a_partner_uuid uuid DEFAULT NULL,
    a_product_id integer DEFAULT NULL,
    a_pirate_source_id integer DEFAULT NULL,
    a_infringement_status ingest.infringement_status_t DEFAULT NULL,
    a_since_ts timestamptz DEFAULT NULL,
    a_till_ts timestamptz DEFAULT NULL,
    a_limit integer DEFAULT 100,
    a_offset integer DEFAULT 0
)
RETURNS TABLE (
    detection_ts timestamptz,
    infringement_url varchar(500),
    infringement_screenshot jsonb,
    infringement_status ingest.infringement_status_t,
    product_id integer,
    product_title varchar(100),
    product_image_url varchar(500),
    pirate_source_id integer,
    pirate_source_name varchar(50),
    pirate_source_type varchar(50),
    partner_id integer,
    partner_uuid uuid,
    partner_name varchar(100)
)
LANGUAGE sql AS $$
    SELECT i.detection_ts,
        i.infringement_url,
        i.infringement_screenshot,
        i.infringement_status,
        i.product_id,
        p.product_title,
        p.product_image_url,
        i.pirate_source_id,
        ps.pirate_source_name,
        ps.pirate_source_type,
        pt.partner_id,
        pt.partner_uuid,
        pt.partner_name
    FROM ingest.infringement i
        JOIN ingest.product p ON p.product_id = i.product_id
        JOIN ingest.pirate_source ps ON ps.pirate_source_id = i.pirate_source_id
        JOIN ingest.partner pt ON pt.partner_id = p.partner_id
    WHERE (a_partner_id IS NULL OR pt.partner_id = a_partner_id)
        AND (a_partner_uuid IS NULL OR pt.partner_uuid = a_partner_uuid)
        AND (a_product_id IS NULL OR i.product_id = a_product_id)
        AND (a_pirate_source_id IS NULL OR i.pirate_source_id = a_pirate_source_id)
        AND (a_infringement_status IS NULL OR i.infringement_status = a_infringement_status)
        AND (a_since_ts IS NULL OR i.detection_ts >= a_since_ts)
        AND (a_till_ts IS NULL OR i.detection_ts < a_till_ts)
    ORDER BY i.infringement_id DESC
    LIMIT a_limit OFFSET a_offset;
$$;

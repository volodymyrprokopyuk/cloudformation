-- Relations and types
CREATE TABLE product (
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

CREATE TYPE protection_status_t AS
    ENUM ('ACTIVE', 'INACTIVE');

CREATE TABLE protection_result (
    product_id integer NOT NULL,
    registration_ts timestamptz NOT NULL,
    protection_status protection_status_t NOT NULL,
    CONSTRAINT uq_protection_result_product_id_registration_ts
        UNIQUE (product_id, registration_ts),
    CONSTRAINT fk_protection_result_product_id
        FOREIGN KEY (product_id) REFERENCES product (product_id)
        ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TYPE pirate_source_name_t AS
    ENUM ('GOOGLE', 'FACEBOOK', 'TWITTER');

CREATE TYPE pirate_source_t AS
    ENUM ('SEARCH_ENGINE', 'SOCIAL_MEDIA');

CREATE TABLE pirate_source (
    pirate_source_id serial NOT NULL,
    pirate_source_external_id varchar(20) NOT NULL,
    pirate_source_name pirate_source_name_t NOT NULL,
    pirate_source_type pirate_source_t NOT NULL,
    registration_ts timestamptz NOT NULL,
    CONSTRAINT pk_pirate_source
        PRIMARY KEY (pirate_source_id),
    CONSTRAINT uq_pirate_source_pirate_source_external_id
        UNIQUE (pirate_source_external_id),
    CONSTRAINT uq_pirate_source_pirate_source_name_pirate_source_type
        UNIQUE (pirate_source_name, pirate_source_type)
);

CREATE TABLE search_engine_pirate_source (
    pirate_source_id integer NOT NULL,
    pirate_source_domain varchar(50) NOT NULL,
    CONSTRAINT uq_search_engine_pirate_source_pirate_source_id
        UNIQUE (pirate_source_id),
    CONSTRAINT uq_search_engine_pirate_source_pirate_source_domain
        UNIQUE (pirate_source_domain),
    CONSTRAINT fk_search_engine_pirate_source_pirate_source_id
        FOREIGN KEY (pirate_source_id) REFERENCES pirate_source (pirate_source_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT ck_search_engine_pirate_source_pirate_source_domain
        CHECK (length(pirate_source_domain) >= 3)
);

CREATE TABLE social_media_pirate_source (
    pirate_source_id integer NOT NULL,
    pirate_source_domain varchar(50) NOT NULL,
    CONSTRAINT uq_social_media_pirate_source_pirate_source_id
        UNIQUE (pirate_source_id),
    CONSTRAINT uq_social_media_pirate_source_pirate_source_domain
        UNIQUE (pirate_source_domain),
    CONSTRAINT fk_social_media_pirate_source_pirate_source_id
        FOREIGN KEY (pirate_source_id) REFERENCES pirate_source (pirate_source_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT ck_social_media_pirate_source_pirate_source_domain
        CHECK (length(pirate_source_domain) >= 3)
);

CREATE TYPE infringement_status_t AS
    ENUM ('ACTIVE', 'TAKEN_DOWN');

CREATE TABLE infringement (
    infringement_id serial NOT NULL,
    product_id integer NOT NULL,
    pirate_source_id integer NOT NULL,
    detection_ts timestamptz NOT NULL,
    infringement_url varchar(500) NOT NULL,
    infringement_status infringement_status_t NOT NULL,
    CONSTRAINT pk_infringement
        PRIMARY KEY (infringement_id),
    CONSTRAINT uq_infringement_product_id_pirate_source_id_detection_ts_url
        UNIQUE (product_id, pirate_source_id, detection_ts, infringement_url),
    CONSTRAINT fk_infringement_product_id
        FOREIGN KEY (product_id) REFERENCES product (product_id)
        ON DELETE RESTRICT ON UPDATE RESTRICT,
    CONSTRAINT fk_infringement_pirate_source_id
        FOREIGN KEY (pirate_source_id) REFERENCES pirate_source (pirate_source_id)
        ON DELETE RESTRICT ON UPDATE RESTRICT,
    CONSTRAINT ck_infringement_infringement_url
        CHECK (length(infringement_url) >= 3)
);

-- Functions
CREATE OR REPLACE FUNCTION put_pirate_source(
    a_pirate_source_external_id varchar(20),
    a_pirate_source_name pirate_source_name_t,
    a_pirate_source_type pirate_source_t,
    a_registration_ts timestamptz
)
RETURNS integer
LANGUAGE sql AS $$
    INSERT INTO pirate_source (
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

CREATE OR REPLACE FUNCTION put_product(
    a_product_external_id varchar(20),
    a_product_title varchar(100),
    a_first_protection_ts timestamptz,
    a_registration_ts timestamptz,
    a_protection_status protection_status_t,
    a_product_image_url varchar(500) DEFAULT NULL
)
RETURNS integer
LANGUAGE sql AS $$
    WITH inserted_product AS (
        INSERT INTO product (
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
    INSERT INTO protection_result (product_id, registration_ts, protection_status)
    SELECT product_id, a_registration_ts, a_protection_status
    FROM inserted_product
    ON CONFLICT ON CONSTRAINT uq_protection_result_product_id_registration_ts
    DO UPDATE SET
        protection_status = excluded.protection_status
    RETURNING product_id;
$$;

CREATE OR REPLACE FUNCTION put_infringement(
    a_product_external_id varchar(20),
    a_pirate_source_external_id varchar(20),
    a_detection_ts timestamptz,
    a_infringement_url varchar(500),
    a_infringement_status infringement_status_t
)
RETURNS integer
LANGUAGE sql AS $$
    WITH infringement_product AS (
        SELECT product_id
        FROM product
        WHERE product_external_id = a_product_external_id
    ),
    infringement_pirate_source AS (
        SELECT pirate_source_id
        FROM pirate_source
        WHERE pirate_source_external_id = a_pirate_source_external_id
    )
    INSERT INTO infringement (
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

-- -- pirate_source
-- SELECT put_pirate_source(
--     'PSRC001', 'GOOGLE', 'SEARCH_ENGINE', '2018-01-20 18:54:35+0200'
-- ) pirate_source_id;
-- SELECT put_pirate_source(
--     'PSRC002', 'FACEBOOK', 'SOCIAL_MEDIA', '2018-02-22 14:13:59+0200'
-- ) pirate_source_id;
-- SELECT put_pirate_source(
--     'PSRC003', 'TWITTER', 'SOCIAL_MEDIA', '2018-03-25 08:50:55+0200'
-- ) pirate_source_id;
-- SELECT put_pirate_source(
--     'PSRC003', 'TWITTER', 'SOCIAL_MEDIA', '2018-03-25 08:50:55+0200'
-- ) pirate_source_id;

-- -- product
-- SELECT put_product(
--     'PROD001', 'Product title 1', '2019-01-06 21:34:54+0200',
--     '2019-02-06 21:34:54+0200', 'ACTIVE', 'https://api.movies.com/movies/1'
-- ) product_id;
-- SELECT put_product(
--     'PROD002', 'Product title 2', '2019-02-06 21:34:54+0200',
--     '2019-03-06 21:34:54+0200', 'INACTIVE'
-- ) product_id;
-- SELECT put_product(
--     'PROD001', 'Product title 1 (updated)', '2019-01-06 21:34:54+0200',
--     '2019-02-06 21:34:54+0200', 'ACTIVE', 'https://api.movies.com/movies/1'
-- ) product_id;

-- -- infringement
-- SELECT put_infringement(
--     'PROD001', 'PSRC001', '2019-04-06 21:34:54+0200',
--     'https://www.pirate1.com/movies/1', 'ACTIVE'
-- ) infringement_id;
-- SELECT put_infringement(
--     'PROD002', 'PSRC002', '2019-05-06 21:34:54+0200',
--     'https://www.pirate1.com/movies/2', 'TAKEN_DOWN'
-- ) infringement_id;
-- SELECT put_infringement(
--     'PROD001', 'PSRC001', '2019-04-06 21:34:54+0200',
--     'https://www.pirate1.com/movies/1', 'TAKEN_DOWN'
-- ) infringement_id;

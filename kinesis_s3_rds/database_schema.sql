CREATE TABLE product (
    product_id serial NOT NULL,
    product_external_id varchar(20) NOT NULL,
    product_title varchar(100) NOT NULL,
    first_protection_ts timestamptz NOT NULL,
    product_image_url varchar(500),
    CONSTRAINT pk_product
        PRIMARY KEY (product_id),
    CONSTRAINT uq_product_proeuct_external_id
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
    CONSTRAINT uq_pirate_source_pirate_source_name_type
        UNIQUE (pirate_source_name, pirate_source_type)
);

CREATE TABLE search_engine_pirate_source (
    pirate_source_id integer NOT NULL,
    CONSTRAINT fk_search_engine_pirate_source_pirate_source_id
        FOREIGN KEY (pirate_source_id) REFERENCES pirate_source (pirate_source_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT uq_search_engine_pirate_source_pirate_source_id
        UNIQUE (pirate_source_id)
);

CREATE TABLE social_media_pirate_source (
    pirate_source_id integer NOT NULL,
    CONSTRAINT fk_social_media_pirate_source_pirate_source_id
        FOREIGN KEY (pirate_source_id) REFERENCES pirate_source (pirate_source_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT uq_social_media_pirate_source_pirate_source_id
        UNIQUE (pirate_source_id)
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
    CONSTRAINT fk_infringement_product_id
        FOREIGN KEY (product_id) REFERENCES product (product_id)
        ON DELETE RESTRICT ON UPDATE RESTRICT,
    CONSTRAINT fk_infringement_pirate_source_id
        FOREIGN KEY (pirate_source_id) REFERENCES pirate_source (pirate_source_id)
        ON DELETE RESTRICT ON UPDATE RESTRICT,
    CONSTRAINT ck_infringement_infringement_url
        CHECK (length(infringement_url) >= 3)
);

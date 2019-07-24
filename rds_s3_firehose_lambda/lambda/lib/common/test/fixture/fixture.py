import os
import psycopg2
from psycopg2.extras import RealDictCursor
from pytest import fixture
from common.test.util import create_transform_event


# Configuration fixture
@fixture
def invalid_db_config(monkeypatch):
    config = {
        "DB_HOST": "host",
        "DB_PORT": "port",
        "DB_NAME": "name",
        "DB_USER": "user",
    }
    for key, value in config.items():
        monkeypatch.setenv(key, value)
    return config


@fixture
def db_config(monkeypatch):
    config = {
        "DB_HOST": "host",
        "DB_PORT": "port",
        "DB_NAME": "name",
        "DB_USER": "user",
        "DB_PASSWORD": "password",
        "DB_CONNECT_TIMEOUT": "connect_timeout",
    }
    for key, value in config.items():
        monkeypatch.setenv(key, value)
    return config


# Transform event fixture
@fixture
def invalid_event():
    event = create_transform_event("", "")
    return event

@fixture
def non_existing_document_event():
    event = create_transform_event("bucket_name", "object_key")
    return event


@fixture
def empty_document_event():
    event = create_transform_event("bucket_name", "document_empty.txt")
    return event


@fixture
def invalid_document_event():
    event = create_transform_event("bucket_name", "document_invalid.txt")
    return event


@fixture
def event():
    event = create_transform_event("bucket_name", "object_key")
    return event

# RDS fixture
@fixture(scope="session")
def rds():
    rds_config = {
        "host": os.getenv("DB_HOST"),
        "port": os.getenv("DB_PORT"),
        "dbname": os.getenv("DB_NAME"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "connect_timeout": os.getenv("DB_CONNECT_TIMEOUT"),
        "cursor_factory": RealDictCursor,
    }
    rds = psycopg2.connect(**rds_config)
    yield rds
    rds.close()

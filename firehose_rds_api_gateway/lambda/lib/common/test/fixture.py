"""Common test fixtures"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor

# pylint: disable=import-error
from pytest import fixture


# Configuration fixture
@fixture
def invalid_db_config(monkeypatch):
    """Invalid database configuration"""
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
    """Database configuration"""
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


# RDS fixture
# pylint: disable=redefined-outer-name
@fixture(scope="session")
def rds():
    """Connect to RDS before a test and close the connection after the test"""
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

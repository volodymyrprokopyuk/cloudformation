"""Import data from JSON file into database"""
import os
import sys
import json
from functools import partial
import psycopg2
from psycopg2.extras import RealDictCursor


def _get_env_specific_config():
    config = {}
    # Get RDS endpoint and credentials from the environment variables
    config["db_host"] = os.getenv("DB_HOST")
    config["db_port"] = os.getenv("DB_PORT")
    config["db_name"] = os.getenv("DB_NAME")
    config["db_user"] = os.getenv("DB_USER")
    config["db_password"] = os.getenv("DB_PASSWORD")
    config["db_connect_timeout"] = os.getenv("DB_CONNECT_TIMEOUT")
    return config


def get_config():
    """Gets configuration from multiple configuration sources"""
    local_config = {}
    env_specific_config = _get_env_specific_config()
    local_config.update(env_specific_config)
    return local_config


def _validate_request():
    errors = []
    if len(sys.argv) != 3 or sys.argv[1] not in ("--partner", "--pirate-source"):
        errors.append(
            "Usage: python main.py {--partner <partner file>"
            + " | --pirate-source <pireate source file>}"
        )
    envs = [
        "DB_HOST",
        "DB_PORT",
        "DB_NAME",
        "DB_USER",
        "DB_PASSWORD",
        "DB_CONNECT_TIMEOUT",
    ]
    for env in envs:
        if not os.getenv(env):
            errors.append(f"Mandatory {env} environment variable is not provided")
    return errors


def _parse_request():
    request = {}
    request["request_type"] = sys.argv[1].replace("--", "")
    request["data_file"] = sys.argv[2]
    return request


def _parse_file(data_file):
    with open(data_file, "r") as opened_file:
        raw_data = opened_file.read()
        raw_records = raw_data.strip().split("\n")
        raw_records = list(filter(len, raw_records))
        return raw_records


def _parse_record(raw_record):
    record = json.loads(raw_record)
    return record


def _put_parter_record_in_db(record, rds):
    with rds.cursor() as cursor:
        sql = """
        SELECT ingest.put_partner(
            %(partner_uuid)s,
            %(partner_name)s,
            %(partner_status)s,
            %(registration_ts)s
        ) partner_id;
        """
        cursor.execute(sql, record)
        result = cursor.fetchone()
        rds.commit()
        partner_id = result["partner_id"]
        return partner_id


def _put_pirate_source_record_in_db(record, rds):
    with rds.cursor() as cursor:
        sql = """
        SELECT ingest.put_pirate_source(
            %(partner_uuid)s,
            %(pirate_source_external_id)s,
            %(pirate_source_name)s,
            %(pirate_source_type)s,
            %(registration_ts)s
        ) pirate_source_id;
        """
        cursor.execute(sql, record)
        result = cursor.fetchone()
        rds.commit()
        pirate_source_id = result["pirate_source_id"]
        return pirate_source_id


def _process_record(put_record_in_db, raw_record, rds):
    try:
        record = _parse_record(raw_record)
        record_id = put_record_in_db(record, rds)
        print(f"SUCCESS: {record}: {record_id}")
    except Exception as error:
        print(f"ERROR: Process record: {error}")


def _process_request(process_record, request):
    local_config = get_config()
    rds_config = {
        "host": local_config["db_host"],
        "port": local_config["db_port"],
        "dbname": local_config["db_name"],
        "user": local_config["db_user"],
        "password": local_config["db_password"],
        "connect_timeout": local_config["db_connect_timeout"],
        "cursor_factory": RealDictCursor,
    }
    rds = psycopg2.connect(**rds_config)
    raw_records = _parse_file(request["data_file"])
    for raw_record in raw_records:
        process_record(raw_record, rds)


def _build_request_handlers():
    request_handlers = {}
    process_partner_record = partial(_process_record, _put_parter_record_in_db)
    process_partner_request = partial(_process_request, process_partner_record)
    request_handlers["partner"] = process_partner_request
    process_pirate_source_record = partial(
        _process_record, _put_pirate_source_record_in_db
    )
    process_pirate_source_request = partial(
        _process_request, process_pirate_source_record
    )
    request_handlers["pirate-source"] = process_pirate_source_request
    return request_handlers


def main():
    """Import data from JSON file into database"""
    errors = _validate_request()
    if errors:
        print(f"ERROR: Request validation: {errors}")
        exit(1)
    request = _parse_request()
    request_handlers = _build_request_handlers()
    process_request = request_handlers[request["request_type"]]
    process_request(request)


if __name__ == "__main__":
    main()

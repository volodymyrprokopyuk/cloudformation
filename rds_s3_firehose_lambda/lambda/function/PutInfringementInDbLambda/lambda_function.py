"""Put infringement into database lambda"""
import os


def lambda_handler(event, context):
    """Put infringement into database lambda handler"""
    print(f"Event: {event}")
    print(f"Context: {context}")
    db_host = os.getenv("DB_HOST", "unknown")
    db_port = os.getenv("DB_PORT", "unknown")
    db_name = os.getenv("DB_NAME", "unknown")
    db_user = os.getenv("DB_USER", "unknown")
    db_password = os.getenv("DB_PASSWORD", "unknown")
    print(f"db_host: {db_host}")
    print(f"db_port: {db_port}")
    print(f"db_name: {db_name}")
    print(f"db_user: {db_user}")
    print(f"db_password: {db_password}")

"""Lambda configuration module"""
import os


_GLOBAL_CONFIG = None


def _get_env_specific_config():
    config = {}
    # Get RDS endpoint and credentials from the environment variables
    config["db_host"] = os.getenv("DB_HOST")
    config["db_port"] = os.getenv("DB_PORT")
    config["db_name"] = os.getenv("DB_NAME")
    config["db_user"] = os.getenv("DB_USER")
    config["db_password"] = os.getenv("DB_PASSWORD")
    return config


def get_config():
    """ Gets configuration from multiple configuration sources"""
    global _GLOBAL_CONFIG
    if _GLOBAL_CONFIG is not None:
        return _GLOBAL_CONFIG
    _GLOBAL_CONFIG = {}
    env_specific_config = _get_env_specific_config()
    _GLOBAL_CONFIG.update(env_specific_config)
    return _GLOBAL_CONFIG

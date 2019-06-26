"""Configuration module"""
import os


# Uninitialized Singleton configuration for the whole process
_GLOBAL_CONFIG = None


def _get_env_specific_config():
    config = {}
    # Geg RDS endpoint and credentials from environment variables
    config["db_host"] = os.getenv("DB_HOST")
    config["db_port"] = os.getenv("DB_PORT")
    config["db_name"] = os.getenv("DB_NAME")
    config["db_user"] = os.getenv("DB_USER")
    config["db_password"] = os.getenv("DB_PASSWORD")
    return config


def get_config():
    """
    Retrieves the configuration from multiple configuration sources. Merges all
    configuration options into a single Python dictionary. Implementes the Singleton
    design pattern
    """
    # Simple Singleton implementation using only module variables and functions
    global _GLOBAL_CONFIG
    if _GLOBAL_CONFIG is not None:
        return _GLOBAL_CONFIG
    # Initialize the Singleton configuraiton
    _GLOBAL_CONFIG = {}
    # Retrieve the environment specific configuration (in this case environment
    # variables)
    env_specific_config = _get_env_specific_config()
    _GLOBAL_CONFIG.update(env_specific_config)
    # Return a single Python dictionary with the configuration options from all
    # configuration sources
    #     - Command line options and parameters
    #     - Environment variables
    #     - Configuration files
    #     - Configuration server REST calls
    #     = Credentials and secrets from a secure vaults
    return _GLOBAL_CONFIG

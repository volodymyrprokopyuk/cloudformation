"""Configuration module"""
import os
import json

# Uninitialized Singleton configuration for the whole process
_GLOBAL_CONFIG = None


def _get_env_idependent_config():
    config = {}
    with open("env_independent_config.json") as config_file:
        config = json.loads(config_file.read())
    return config


def _get_env_specific_config():
    config = {}
    config["ENV_SPECIFIC_CONFIG_OPTION_A"] = os.getenv("ENV_SPECIFIC_CONFIG_OPTION_A",
                                                       "Configuration option A default")
    config["ENV_SPECIFIC_CONFIG_OPTION_B"] = os.getenv("ENV_SPECIFIC_CONFIG_OPTION_B",
                                                       "Configuration option A default")
    return config


def get_config():
    """
        Retrieves the configuration from multiple configuration sources. Merges all configuration options into a single
        Python dictionary. Implementes the Singleton design pattern
    """
    # Simple Singleton implementation using only module variables and functions
    global _GLOBAL_CONFIG
    if _GLOBAL_CONFIG is not None:
        return _GLOBAL_CONFIG
    # Initialize the Singleton configuraiton
    _GLOBAL_CONFIG = {}
    # Retrieve the environment independent configuration (in this case a configuration JSON file)
    env_indpendent_config = _get_env_idependent_config()
    _GLOBAL_CONFIG.update(env_indpendent_config)
    # Retrieve the environment specific configuration (in this case environment variables)
    env_specific_config = _get_env_specific_config()
    _GLOBAL_CONFIG.update(env_specific_config)
    # Return a single Python dictionary with the configuration options from all configuration sources
    #     - Command line options and parameters
    #     - Configuration files
    #     - Environment variables
    #     - Configuration server REST calls
    #     = Secure vaults
    return _GLOBAL_CONFIG

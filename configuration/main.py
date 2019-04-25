"""Use `config` module and `get_config` function"""
from functools import wraps
# The `get_config()` function is the only configuration interface for all modules
from config import get_config


# The global configuration is required to configure decorators
GLOBAL_CONFIG = get_config()


def decorator_needs_config(config):
    """Decorator with a parameter `config` that is used for configuration purposes"""
    def decorator(original):
        @wraps(original)
        def decorated(*args, **kwargs):
            print(f"Decorator configuration: {config}")
            return original(*args, **kwargs)
        return decorated
    return decorator


# Use the `global_config` to configure a decorator
@decorator_needs_config(GLOBAL_CONFIG["env_independent_config_option_a"])
def function_needs_config(config):
    """Function configuration is passed explicitly as a parameter"""
    print(f"Function configuration: {config}")


class ClassNeedsConfig:
    """Class is configured via the constructor call"""

    def __init__(self, config):
        """Store the class configuration provided in a constructor call in an instance varaible"""
        self.config = config

    def show_config(self):
        """Show class configuration"""
        print(f"Class configuration: {self.config}")


def main():
    """Showcase `local_config` usage"""
    # Retrive all configuration at program entry point
    local_config = get_config()
    # Explicitly pass to a function ONLY required configuration
    function_needs_config(local_config["env_independent_config_option_b"])
    # Explicitly pass to a class ONLY required configuration
    class_needs_config = ClassNeedsConfig(local_config["ENV_SPECIFIC_CONFIG_OPTION_A"])
    class_needs_config.show_config()


if __name__ == "__main__":
    main()

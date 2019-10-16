"Common util functions"
from datetime import datetime


TS_FORMAT = "%Y-%m-%d %H:%M:%S%z"


def is_valid_timestamp(ts, ts_format):
    """Returns true when a timestampt is valid and conforms to the timestampt format"""
    try:
        datetime.strptime(ts, ts_format)
        return True
    except ValueError:
        return False


def get_or_default(dictionary, keys, default=None):
    """Returns nested dot-separated value from a dictionary or default"""
    value = dictionary
    for key in keys.split("."):
        try:
            value = value[key]
        except (KeyError, TypeError):
            return default
    return default if value is None else value

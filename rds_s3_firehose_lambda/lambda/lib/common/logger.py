"""Logger with a JSON formatter and environment and context log decorators"""
import os
import logging
import time
import json
from functools import wraps


class JsonFormatter:
    """Convert a LogRecord to JSON"""

    OPTIONAL_JSON_ATTRIBUTES = ["stack", "version"]

    def format(self, log_record):
        """Convert a LogRecord to JSON"""
        json_log_record = {}
        # Timestamp in UTC
        created = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(log_record.created))
        msecs = int(log_record.msecs)
        json_log_record["timestamp"] = f"{created}.{msecs:03}"
        # Log level
        json_log_record["level"] = log_record.levelname
        # Logger name
        json_log_record["name"] = log_record.name
        # Log message: single dict argument
        if isinstance(log_record.msg, dict) and not log_record.args:
            json_log_record["message"] = log_record.msg
        # Log message: format string with arguments
        else:
            json_log_record["message"] = log_record.getMessage()
        # Optional JSON attributes from environment and context log decorators
        for attribute in JsonFormatter.OPTIONAL_JSON_ATTRIBUTES:
            if hasattr(log_record, attribute):
                json_log_record[attribute] = getattr(log_record, attribute)
        # Format the LogRecord in JSON
        return json.dumps(json_log_record)


def with_logger(name, log_file=None):
    """Configure a logger with a JSON formatter and a stream or a file handler"""

    def _create_log_handler():
        # Create a FileHandler if the log_file is provided
        if log_file:
            # Recursively create log subdirectories if needed
            log_dir = os.path.dirname(log_file)
            if log_dir:
                os.makedirs(log_dir, exist_ok=True)
            handler = logging.FileHandler(log_file)
        # Create a console StreamHandler if the log_file is not provided
        else:
            handler = logging.StreamHandler()
        # Set a JSON formatter
        formatter = JsonFormatter()
        handler.setFormatter(formatter)
        return handler

    def decorator(original):
        @wraps(original)
        def decorated(*args, **kwargs):
            logger = logging.getLogger(name)
            # Add the configured log handler if it is not already added
            if not logger.handlers:
                handler = _create_log_handler()
                logger.addHandler(handler)
            # Set a log level from the LOG_LEVEL environment variable
            log_level = os.getenv("LOG_LEVEL", "INFO")
            logger.setLevel(log_level)
            # Provide the configured logger to the original function
            return original(logger, *args, **kwargs)

        return decorated

    return decorator


def log_environment(original):
    """Add environment-specific parameters to a LogRecord"""

    @wraps(original)
    def decorated(logger, *args, **kwargs):
        stack_name = os.getenv("STACK_NAME", "default")
        lambda_version = os.getenv("LAMBDA_VERSION", "0.0.0")

        def execution_environment_filter(log_record):
            log_record.stack = stack_name
            log_record.version = lambda_version
            return True

        logger.addFilter(execution_environment_filter)
        result = original(logger, *args, **kwargs)
        logger.removeFilter(execution_environment_filter)
        return result

    return decorated


def log_context(original):
    """Add context-specific parameters to a LogRecord"""

    @wraps(original)
    def decorated(logger, request, *args, **kwargs):
        candidate_id = request["candidate_id"]

        def execution_context_filter(log_record):
            log_record.candidateId = candidate_id
            return True

        logger.addFilter(execution_context_filter)
        result = original(logger, request, *args, **kwargs)
        logger.removeFilter(execution_context_filter)
        return result

    return decorated


@with_logger("main")
# @log_context
def process_request(logger, request):
    """Process request"""
    logger.info("Processing request %s", request)
    logger.info({"request": request})


@with_logger("main")
# @with_logger("main", "main.log")
# @with_logger("main", "log/sublog/main.log")
@log_environment
def main(logger):
    """Process requests"""
    logger.debug("Starting...")
    requests = [{"candidate_id": 1}, {"candidate_id": 2}]
    logger.warning("Processing %s requests...", len(requests))
    for request in requests:
        process_request(request)
    logger.error("Test error message")
    logger.critical("Test critical message")
    logger.debug("Stopping...")


if __name__ == "__main__":
    main()

# LOG_LEVEL=DEBUG STACK_NAME=vlad-dev LAMBDA_VERSION=0.1.0 python lambda/lib/common/logger.py

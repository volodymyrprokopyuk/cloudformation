"""Logger, execution environment, and execution context decorators"""
import logging
import time
import json
from functools import wraps


class JsonFormatter:
    """
        JsonFormatter converts LogRecord to JSON

        Mandatory LogRecord parameters that will be included into final JSON from the origianl LogRecord
        - Timestamp
        - Log level
        - Logger name
        - Log message

        Optional LogRecord parameters that will be included into the fina JSON from the execution environment
        - Environment name

        Optional LogRecord parameters that will be included into the fina JSON from the execution context
        - CandidateId
    """

    # Convert the native Python log levels to the desired and documented log levels
    LOG_LEVEL_MAP = {
        "DEBUG": "DEBUG",
        "INFO": "INFO",
        "WARNING": "WARN",
        "ERROR": "ERROR",
        "CRITICAL": "FATAL"
    }

    # Optional JSON attributes from the execution environment and the execution context
    OPTIONAL_JSON_ATTRIBUTES = ["environment", "candidateId"]

    def format(self, log_record):
        """Convert LogRecord to JSON"""
        json_log_record = {}
        # Timestamp in UTC
        created = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(log_record.created))
        msecs = int(log_record.msecs)
        json_log_record["timestamp"] = f"{created}.{msecs:03}"
        # Log level
        json_log_record["level"] = JsonFormatter.LOG_LEVEL_MAP.get(log_record.levelname)
        # Logger name
        json_log_record["name"] = log_record.name
        # Log message
        json_log_record["message"] = log_record.getMessage()
        # Add optional JSON attributes from the execution environment and the execution context
        for attribute in JsonFormatter.OPTIONAL_JSON_ATTRIBUTES:
            if hasattr(log_record, attribute):
                json_log_record[attribute] = getattr(log_record, attribute)
        # Format the LogRecord in JSON
        return json.dumps(json_log_record)


def with_logger(name):
    """Provide a configured Logger with name `name` to the original function"""
    def decorator(original):
        @wraps(original)
        def decorated(*args, **kwargs):
            formatter = JsonFormatter()
            handler = logging.StreamHandler()
            # Use the JSON formatter
            handler.setFormatter(formatter)
            logger = logging.getLogger(name)
            # Use STDOUT for log output
            logger.addHandler(handler)
            # Provide the configured Logger to the original function
            return original(logger, *args, **kwargs)
        return decorated
    return decorator


def with_execution_environment(original):
    """Attach the execution environment parameters to the Logger of the original function"""
    def decorated(logger, *args, **kwargs):
        # Retrieve the environment name form the environment
        environment = "DEV"

        # Define the execution environment filter to add the execution environment parameters to the LogRecord
        def execution_environment_filter(log_record):
            log_record.environment = environment
            return True

        # Add the execution environment filter to the Logger
        logger.addFilter(execution_environment_filter)
        # Forward the Logger with the added execution environment filter to the original function
        result = original(logger, *args, **kwargs)
        # Remove the execution environment filter from the Logger to prevent the execution environment parameters
        # to appear in logs outside the scope of the function on which the @with_execution_environment decorator
        # has been applied
        logger.removeFilter(execution_environment_filter)
        return result
    return decorated


def with_execution_context(original):
    """Attach the execution context parameters to the Logger of the original function"""
    def decorated(logger, request, *args, **kwargs):
        # Retrieve the CandidateId from the request
        candidate_id = request["candidate_id"]

        # Define the execution context filter to add the execution context parameters to the LogRecord
        def execution_context_filter(log_record):
            log_record.candidateId = candidate_id
            return True

        # Add the execution context filter to the Logger
        logger.addFilter(execution_context_filter)
        # Forward the Logger with the added execution context filter to the original function
        result = original(logger, request, *args, **kwargs)
        # Remove the execution context filter from the Logger to prevent the execution context parameters # to appear in
        # logs outside the scope of the function on which the @with_execution_context decorator has been applied
        logger.removeFilter(execution_context_filter)
        return result
    return decorated


@with_execution_context
def process_request(logger, request):
    """Process request"""
    logger.info("Processing request %s", request)


@with_logger(__name__)
@with_execution_environment
def main(logger):
    """Process requests"""
    logger.setLevel("DEBUG")

    logger.debug("Starting...")
    requests = [{"candidate_id": 1}, {"candidate_id": 2}]
    logger.warning("Processing %s requests...", len(requests))
    for request in requests:
        process_request(logger, request)
    logger.error("Test error message")
    logger.critical("Test fatal message")
    logger.debug("Stopping...")


main()

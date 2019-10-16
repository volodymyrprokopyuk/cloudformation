"""Get data from database lambda"""
import json
from functools import partial
import psycopg2
from psycopg2.extras import RealDictCursor
from common.util import get_or_default
from common.logger import with_logger, log_environment, log_request_context
from common.transform.transform_config import get_config


LOGGER_NAME = "main"


class HttpError(Exception):
    """HttpError with message, HTTP status code and error details"""

    def __init__(self, message, statusCode, details):
        super().__init__(message)
        self.statusCode = statusCode
        self.details = details

    def description(self):
        """Provides error message, status code and error details"""
        return (
            # pylint: disable=unsubscriptable-object
            f"{self.args[0]}. Status code: {self.statusCode}"
            + f". Details: {'; '.join(self.details)}"
        )


def _validate_config(local_config):
    errors = []
    # Validate RDS endpoint and credentials
    attributes = [
        "db_host",
        "db_port",
        "db_name",
        "db_user",
        "db_password",
        "db_connect_timeout",
    ]
    for attribute in attributes:
        if not get_or_default(local_config, attribute):
            errors.append(f"mandatory {attribute} is not provided")
    return errors


def _log_request(logger, event):
    method = get_or_default(event, "httpMethod", "unknown")
    path = get_or_default(event, "path", "unknown")
    path_params = get_or_default(event, "pathParameters", {})
    querystring = get_or_default(event, "queryStringParameters", {})
    logger.info(f"START: {method} {path}/{path_params}?{querystring}")
    logger.info(event)


def _format_success_response(data):
    response = {}
    response["statusCode"] = 200
    headers = {}
    headers["Content-Type"] = "application/json"
    response["headers"] = headers
    body = {}
    body["data"] = data
    response["body"] = json.dumps(body)
    response["isBase64Encoded"] = False
    return response


def _format_error_response(error):
    response = {}
    response["statusCode"] = error.statusCode
    headers = {}
    headers["Content-Type"] = "application/json"
    response["headers"] = headers
    response_error = {}
    response_error["message"] = str(error)
    response_error["details"] = "; ".join(error.details)
    body = {}
    body["error"] = response_error
    response["body"] = json.dumps(body)
    response["isBase64Encoded"] = False
    return response


@with_logger(LOGGER_NAME)
# pylint: disable=unused-argument
def _process_request(
    logger, parse_request, validate_request, perform_db_operation, event
):
    local_config = get_config()
    errors = _validate_config(local_config)
    if not errors:
        request = parse_request(event)
        errors = validate_request(request)
        if not errors:
            try:
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
                local_config["rds"] = rds
                try:
                    try:
                        data = perform_db_operation(request, rds)
                        return (None, data)
                    except Exception as error:
                        logger.error(f"Perform database operation: {error}")
                        request_error = HttpError("Database error", 500, [str(error)])
                finally:
                    rds.close()
            except Exception as error:
                logger.critical(f"Connect to RDS: {error}")
                request_error = HttpError("Connect to RDS error", 500, [str(error)])
        else:
            logger.error(f"Validate request: {errors}")
            request_error = HttpError("Validate request error", 400, errors)
    else:
        logger.critical(f"Validate configuration: {errors}")
        request_error = HttpError("Validate configuration error", 500, errors)
    return (request_error, None)


@with_logger(LOGGER_NAME)
@log_environment
@log_request_context
# pylint: disable=unused-argument
def _lambda_handler(logger, process_request, event, context):
    _log_request(logger, event)
    (error, data) = process_request(event)
    if error:
        error_response = _format_error_response(error)
        logger.error(f"FAILURE: {error.description()}")
        return error_response
    success_response = _format_success_response(data)
    logger.info(f"SUCCESS: Status code: 200. Records: {len(data)}")
    return success_response


def create_lambda_handler(parse_request, validate_request, perform_db_operation):
    """Create labmda handler for provided specific functions and configuration"""
    process_request = partial(
        _process_request, parse_request, validate_request, perform_db_operation
    )
    lambda_handler = partial(_lambda_handler, process_request)
    return lambda_handler

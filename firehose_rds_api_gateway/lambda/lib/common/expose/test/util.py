import uuid
import json


def create_expose_event(
    method, path, path_parameters=None, querystring_parameters=None, body=None
):
    event = {
        "httpMethod": method,
        "path": path,
        "pathParameters": path_parameters,
        "queryStringParameters": querystring_parameters,
        "requestContext": {"requestId": str(uuid.uuid4())},
        "body": json.dumps(body),
    }
    return event

"""Post infirngement into database lambda"""
import re
import json
from common.util import get_or_default, TS_FORMAT, is_valid_timestamp
from common.expose.expose_lambda_handler import create_lambda_handler


def _parse_request(event):
    request = {}
    body = get_or_default(event, "body")
    if body == "null":
        return request
    try:
        request = json.loads(body)
    except Exception:
        return request
    return request


def _validate_request(request):
    errors = []
    if not request:
        errors.append("request body is empty or invalid JSON")
        return errors
    attributes = [
        "partnerUuid",
        "productExternalId",
        "pirateSourceExternalId",
        "detectionTs",
        "infringementUrl",
        "infringementStatus",
    ]
    for attribute in attributes:
        if get_or_default(request, attribute) is None:
            errors.append(f"mandatory {attribute} is not provided")
    if errors:
        return errors
    partner_uuid = request["partnerUuid"]
    if partner_uuid is not None and not re.match(
        r"^\w{8}-\w{4}-\w{4}-\w{4}-\w{12}$", partner_uuid
    ):
        errors.append("mandatory partnerUuid must be a UUID")
    product_external_id = request["productExternalId"]
    # pylint: disable=len-as-condition
    if product_external_id is not None and not 0 < len(product_external_id) < 51:
        errors.append("mandatory productExternalId is too short or too long")
    pirate_source_external_id = request["pirateSourceExternalId"]
    if (
        pirate_source_external_id is not None
        and not 0 < len(pirate_source_external_id) < 51
    ):
        errors.append("mandatory pirateSourceExternalId is too short or too long")
    detection_ts = request["detectionTs"]
    if detection_ts is not None and not is_valid_timestamp(detection_ts, TS_FORMAT):
        errors.append(f"mandatory detectionTs must be valid: {TS_FORMAT}")
    infringement_url = request["infringementUrl"]
    if infringement_url is not None and not 7 < len(infringement_url) < 501:
        errors.append("mandatory infringementUrl is too short or too long")
    infringement_status = request["infringementStatus"]
    if infringement_status is not None and not 1 < len(infringement_status) < 31:
        errors.append("mandatory infringementStatus is too short or too long")
    if "infringementScreenshot" not in request:
        request["infringementScreenshot"] = None
    infringement_screenshot = request["infringementScreenshot"]
    if infringement_screenshot is not None and not get_or_default(
        request, "infringementScreenshot.screenshotUrl"
    ):
        errors.append("optional infringementScreenshot is missing screenshotUrl array")
    return errors


def _build_sql_query(request):
    infringement_screenshot = request["infringementScreenshot"]
    if infringement_screenshot is not None:
        request["infringementScreenshot"] = json.dumps(
            request["infringementScreenshot"]
        )
    parameterMapping = {
        "partnerUuid": "a_partner_uuid",
        "productExternalId": "a_product_external_id",
        "pirateSourceExternalId": "a_pirate_source_external_id",
        "detectionTs": "a_detection_ts",
        "infringementUrl": "a_infringement_url",
        "infringementScreenshot": "a_infringement_screenshot",
        "infringementStatus": "a_infringement_status",
    }
    sqlArguments = [
        f"{sqlParam} := %({httpParam})s"
        for (httpParam, sqlParam) in parameterMapping.items()
        if request[httpParam] is not None
    ]
    sql = f"""
    SELECT ingest.put_infringement({', '.join(sqlArguments)}) infringement_id;
    """
    return sql


def _put_record_into_db(request, rds):
    with rds.cursor() as cursor:
        sql = _build_sql_query(request)
        cursor.execute(sql, request)
        result = cursor.fetchone()
        rds.commit()
        record_id = result["infringement_id"]
        response = {}
        response["infringementId"] = record_id
        return response


lambda_handler = create_lambda_handler(
    _parse_request, _validate_request, _put_record_into_db
)

"""Get partner from database lambda"""
import re
from common.util import TS_FORMAT, get_or_default
from common.expose.expose_lambda_handler import create_lambda_handler


def _parse_request(event):
    request = {}
    request["partnerId"] = get_or_default(event, "pathParameters.partnerId")
    partner_id = request["partnerId"]
    if partner_id is not None and str(partner_id).isdigit():
        request["partnerId"] = int(partner_id)
    request["partnerUuid"] = get_or_default(event, "queryStringParameters.partnerUuid")
    request["partnerName"] = get_or_default(event, "queryStringParameters.partnerName")
    request["partnerStatus"] = get_or_default(
        event, "queryStringParameters.partnerStatus"
    )
    return request


def _validate_request(request):
    errors = []
    partner_id = request["partnerId"]
    if partner_id is not None and not isinstance(partner_id, int):
        errors.append("partnerId must be an integer")
    partner_uuid = request["partnerUuid"]
    if partner_uuid is not None and not re.match(
        r"^\w{8}-\w{4}-\w{4}-\w{4}-\w{12}$", partner_uuid
    ):
        errors.append("partnerUuid must be a UUID")
    partner_name = request["partnerName"]
    if partner_name is not None and not 1 < len(partner_name) < 101:
        errors.append("partnerName is too short or too long")
    partner_status = request["partnerStatus"]
    if partner_status is not None and not 1 < len(partner_status) < 31:
        errors.append("partnerStatus is too short or too long")
    if partner_id is not None and partner_uuid is not None:
        errors.append("partnerUuid is not compatible with partnerId")
    if (partner_id is not None or partner_uuid is not None) and (
        partner_name is not None or partner_status is not None
    ):
        errors.append(
            "partnerName and partnerStatus are not compatible with"
            + " partnerId and partnerUuid"
        )
    return errors


def _build_sql_query(request):
    parameterMapping = {
        "partnerId": "a_partner_id",
        "partnerUuid": "a_partner_uuid",
        "partnerName": "a_partner_name",
        "partnerStatus": "a_partner_status",
    }
    sqlArguments = [
        f"{sqlParam} := %({httpParam})s"
        for (httpParam, sqlParam) in parameterMapping.items()
        if request[httpParam] is not None
    ]
    sql = f"""
        SELECT
            pt.partner_id "partnerId",
            pt.partner_uuid "partnerUuid",
            pt.partner_name "partnerName",
            pt.partner_status "partnerStatus",
            pt.registration_ts "registrationTs"
        FROM ingest.get_partner({', '.join(sqlArguments)}) pt;
    """
    return sql


def _format_data(data):
    for record in data:
        registration_ts = record["registrationTs"]
        record["registrationTs"] = registration_ts.strftime(TS_FORMAT)
    return data


def _get_data_from_db(request, rds):
    with rds.cursor() as cursor:
        sql = _build_sql_query(request)
        cursor.execute(sql, request)
        data = cursor.fetchall()
        formatted_data = _format_data(data)
        return formatted_data


lambda_handler = create_lambda_handler(
    _parse_request, _validate_request, _get_data_from_db
)

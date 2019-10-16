"""Get pirate srouce from database lambda"""
from common.util import TS_FORMAT, get_or_default
from common.expose.expose_lambda_handler import create_lambda_handler


def _parse_request(event):
    request = {}
    request["partnerId"] = get_or_default(event, "queryStringParameters.partnerId")
    partner_id = request["partnerId"]
    if partner_id is not None and str(partner_id).isdigit():
        request["partnerId"] = int(partner_id)
    request["pirateSourceId"] = get_or_default(event, "pathParameters.pirateSourceId")
    pirate_source_id = request["pirateSourceId"]
    if pirate_source_id is not None and str(pirate_source_id).isdigit():
        request["pirateSourceId"] = int(pirate_source_id)
    request["pirateSourceName"] = get_or_default(
        event, "queryStringParameters.pirateSourceName"
    )
    request["pirateSourceType"] = get_or_default(
        event, "queryStringParameters.pirateSourceType"
    )
    return request


def _validate_request(request):
    errors = []
    partner_id = request["partnerId"]
    if partner_id is not None and not isinstance(partner_id, int):
        errors.append("partnerId must be an integer")
    pirate_source_id = request["pirateSourceId"]
    if pirate_source_id is not None and not isinstance(pirate_source_id, int):
        errors.append("pirateSourceId must be an integer")
    pirate_source_name = request["pirateSourceName"]
    if pirate_source_name is not None and not 1 < len(pirate_source_name) < 51:
        errors.append("pirateSourceName is too short or too long")
    pirate_source_type = request["pirateSourceType"]
    if pirate_source_type is not None and not 1 < len(pirate_source_type) < 51:
        errors.append("pirateSourceType is too short or too long")
    if (
        pirate_source_id is None
        and partner_id is None
        and not (pirate_source_name or pirate_source_type)
    ):
        errors.append("mandatory partnerId is not provided")
    if pirate_source_id and (pirate_source_name or pirate_source_type):
        errors.append(
            "pirateSourceName and pirateSourceType are not compatible with"
            + " pirateSourceId"
        )
    return errors


def _build_sql_query(request):
    parameterMapping = {
        "partnerId": "a_partner_id",
        "pirateSourceId": "a_pirate_source_id",
        "pirateSourceName": "a_pirate_source_name",
        "pirateSourceType": "a_pirate_source_type",
    }
    sqlArguments = [
        f"{sqlParam} := %({httpParam})s"
        for (httpParam, sqlParam) in parameterMapping.items()
        if request[httpParam] is not None
    ]
    sql = f"""
        SELECT ps.pirate_source_id "pirateSourceId",
            ps.pirate_source_name "pirateSourceName",
            ps.pirate_source_type "pirateSourceType",
            ps.registration_ts "registrationTs",
            ps.partner_id "partnerId",
            ps.partner_uuid "partnerUuid",
            ps.partner_name "partnerName"
        FROM ingest.get_pirate_source({', '.join(sqlArguments)}) ps;
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

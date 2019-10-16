"""Get product from database lambda"""
from common.util import TS_FORMAT, get_or_default
from common.expose.expose_lambda_handler import create_lambda_handler


def _parse_request(event):
    request = {}
    request["partnerId"] = get_or_default(event, "queryStringParameters.partnerId")
    partner_id = request["partnerId"]
    if partner_id is not None and str(partner_id).isdigit():
        request["partnerId"] = int(partner_id)
    request["productId"] = get_or_default(event, "pathParameters.productId")
    product_id = request["productId"]
    if product_id is not None and str(product_id).isdigit():
        request["productId"] = int(product_id)
    request["productTitle"] = get_or_default(
        event, "queryStringParameters.productTitle"
    )
    request["protectionStatus"] = get_or_default(
        event, "queryStringParameters.protectionStatus"
    )
    return request


def _validate_request(request):
    errors = []
    partner_id = request["partnerId"]
    if partner_id is not None and not isinstance(partner_id, int):
        errors.append("partnerId must be an integer")
    product_id = request["productId"]
    if product_id is not None and not isinstance(product_id, int):
        errors.append("productId must be an integer")
    product_title = request["productTitle"]
    if product_title is not None and not 1 < len(product_title) < 101:
        errors.append("productTitle is too short or too long")
    protection_status = request["protectionStatus"]
    if protection_status is not None and not 1 < len(protection_status) < 31:
        errors.append("protectionStatus is too short or too long")
    if (
        product_id is None
        and partner_id is None
        and not (product_title or protection_status)
    ):
        errors.append("mandatory partnerId is not provided")
    if product_id and (product_title or protection_status):
        errors.append(
            "productTitle and protectionStatus are not compatible with productId"
        )
    return errors


def _build_sql_query(request):
    parameterMapping = {
        "partnerId": "a_partner_id",
        "productId": "a_product_id",
        "productTitle": "a_product_title",
        "protectionStatus": "a_protection_status",
    }
    sqlArguments = [
        f"{sqlParam} := %({httpParam})s"
        for (httpParam, sqlParam) in parameterMapping.items()
        if request[httpParam] is not None
    ]
    sql = f"""
        SELECT p.product_id "productId",
            p.product_title "productTitle",
            p.product_image_url "productImageUrl",
            p.protection_status "protectionStatus",
            p.first_protection_ts "firstProtectionTs",
            p.registration_ts "registrationTs",
            p.partner_id "partnerId",
            p.partner_uuid "partnerUuid",
            p.partner_name "partnerName"
        FROM ingest.get_product({', '.join(sqlArguments)}) p;
    """
    return sql


def _format_data(data):
    for record in data:
        first_protection_ts = record["firstProtectionTs"]
        record["firstProtectionTs"] = first_protection_ts.strftime(TS_FORMAT)
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

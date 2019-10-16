"""Get infringement from database lambda"""
import re
from common.util import get_or_default, TS_FORMAT, is_valid_timestamp
from common.expose.expose_lambda_handler import create_lambda_handler


def _parse_request(event):
    request = {}
    request["partnerId"] = get_or_default(event, "queryStringParameters.partnerId")
    partner_id = request["partnerId"]
    if partner_id is not None and str(partner_id).isdigit():
        request["partnerId"] = int(partner_id)
    request["partnerUuid"] = get_or_default(event, "queryStringParameters.partnerUuid")
    request["productId"] = get_or_default(event, "queryStringParameters.productId")
    product_id = request["productId"]
    if product_id is not None and str(product_id).isdigit():
        request["productId"] = int(product_id)
    request["pirateSourceId"] = get_or_default(
        event, "queryStringParameters.pirateSourceId"
    )
    pirate_source_id = request["pirateSourceId"]
    if pirate_source_id is not None and str(pirate_source_id).isdigit():
        request["pirateSourceId"] = int(pirate_source_id)
    request["infringementStatus"] = get_or_default(
        event, "queryStringParameters.infringementStatus"
    )
    request["sinceTs"] = get_or_default(event, "queryStringParameters.sinceTs")
    since_ts = request["sinceTs"]
    if since_ts is not None:
        request["sinceTs"] = re.sub(r" (\d+)$", r"+\1", since_ts)
    request["tillTs"] = get_or_default(event, "queryStringParameters.tillTs")
    till_ts = request["tillTs"]
    if till_ts is not None:
        request["tillTs"] = re.sub(r" (\d+)$", r"+\1", till_ts)
    request["limit"] = get_or_default(event, "queryStringParameters.limit")
    limit = request["limit"]
    if limit is not None and str(limit).isdigit():
        request["limit"] = int(limit)
    request["offset"] = get_or_default(event, "queryStringParameters.offset")
    offset = request["offset"]
    if offset is not None and str(offset).isdigit():
        request["offset"] = int(offset)
    return request


# pylint: disable=too-many-branches
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
    product_id = request["productId"]
    if product_id is not None and not isinstance(product_id, int):
        errors.append("productId must be an integer")
    pirate_source_id = request["pirateSourceId"]
    if pirate_source_id is not None and not isinstance(pirate_source_id, int):
        errors.append("pirateSourceId must be an integer")
    infringement_status = request["infringementStatus"]
    if infringement_status is not None and not 1 < len(infringement_status) < 31:
        errors.append("infringementStatus is too short or too long")
    since_ts = request["sinceTs"]
    if since_ts is not None and not is_valid_timestamp(since_ts, TS_FORMAT):
        errors.append(f"sinceTs must be valid: {TS_FORMAT}")
    till_ts = request["tillTs"]
    if till_ts is not None and not is_valid_timestamp(till_ts, TS_FORMAT):
        errors.append(f"tillTs must be valid: {TS_FORMAT}")
    limit = request["limit"]
    if limit is not None and not isinstance(limit, int):
        errors.append("optional limit must be an integer")
    if limit is not None and isinstance(limit, int) and limit > 1000:
        errors.append("optional limit must be lower or equal to 1000")
    offset = request["offset"]
    if offset is not None and not isinstance(offset, int):
        errors.append("optional offset must be an integer")
    if offset is not None and isinstance(offset, int) and offset > 100:
        errors.append("optional offset must lower or equal to 100")
    if all([parameter is None for parameter in [partner_id, partner_uuid, product_id]]):
        errors.append("one of partnerId, partnerUuid, or productId is mandatory")
    if all([parameter is not None for parameter in [partner_id, partner_uuid]]):
        errors.append("one of partnerId, partnerUuid is allowed")
    return errors


def _build_sql_query(request):
    parameterMapping = {
        "partnerId": "a_partner_id",
        "partnerUuid": "a_partner_uuid",
        "productId": "a_product_id",
        "pirateSourceId": "a_pirate_source_id",
        "infringementStatus": "a_infringement_status",
        "sinceTs": "a_since_ts",
        "tillTs": "a_till_ts",
        "limit": "a_limit",
        "offset": "a_offset",
    }
    sqlArguments = [
        f"{sqlParam} := %({httpParam})s"
        for (httpParam, sqlParam) in parameterMapping.items()
        if request[httpParam] is not None
    ]
    sql = f"""
    SELECT i.detection_ts "detectionTs",
        i.infringement_url "infringementUrl",
        i.infringement_screenshot "infringementScreenshot",
        i.infringement_status "infringementStatus",
        i.product_id "productId",
        i.product_title "productTitle",
        i.product_image_url "productImageUrl",
        i.pirate_source_id "pirateSourceId",
        i.pirate_source_name "pirateSourceName",
        i.pirate_source_type "pirateSourceType",
        i.partner_id "partnerId",
        i.partner_uuid "partnerUuid",
        i.partner_name "partnerName"
    FROM ingest.get_infringement({', '.join(sqlArguments)}) i;
    """
    return sql


def _format_data(data):
    for record in data:
        detection_ts = record["detectionTs"]
        record["detectionTs"] = detection_ts.strftime(TS_FORMAT)
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

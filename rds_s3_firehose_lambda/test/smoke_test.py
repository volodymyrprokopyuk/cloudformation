from common.test.util import get_product_count, get_infringement_count


def _get_dummy_count(rds):
    with rds.cursor() as cursor:
        sql = """
            SELECT count(*) dummy_count FROM ingest.infringement i
                JOIN ingest.product p ON p.product_id = i.product_id
            WHERE p.product_external_id = 'PROD000';
        """
        cursor.execute(sql)
        result = cursor.fetchone()
        product_count = result["dummy_count"]
        return product_count


def test_process_request_success(rds):
    dummy_count = _get_dummy_count(rds)
    assert dummy_count == 1

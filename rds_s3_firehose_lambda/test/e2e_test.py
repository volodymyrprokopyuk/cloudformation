from common.test.util import get_product_count, get_infringement_count

def test_process_request_success(rds):
    product_count = get_product_count(rds)
    assert product_count > 0
    infringement_count = get_infringement_count(rds)
    assert infringement_count > 0

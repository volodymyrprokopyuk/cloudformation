"""Common utils"""
from unittest.mock import MagicMock


def all_in(messages, log):
    """Returns true if all messages are found in log capture"""
    return all([message in log for message in messages])


def all_not_in(messages, log):
    """Returns true if none of messages are found in log capture"""
    return all([message not in log for message in messages])


def mock_pg_fetchall(pg_connect_mock, fetchall_value):
    """Mock PostgreSQL fetchall method to return the fetchall_value"""
    rds_mock = MagicMock()
    pg_connect_mock.return_value = rds_mock
    cursor_mock = MagicMock()
    rds_mock.cursor.return_value = cursor_mock
    cursor_mock.__enter__.return_value = MagicMock()
    cursor_mock.__enter__.return_value.fetchall.return_value = fetchall_value


def mock_pg_fetchone(pg_connect_mock, fetchone_value):
    """Mock PostgreSQL fetchone method to return the fetchone_value"""
    rds_mock = MagicMock()
    pg_connect_mock.return_value = rds_mock
    cursor_mock = MagicMock()
    rds_mock.cursor.return_value = cursor_mock
    cursor_mock.__enter__.return_value = MagicMock()
    cursor_mock.__enter__.return_value.fetchone.return_value = fetchone_value


PARTNERS = [
    {
        "partner_uuid": "aa61382a-a98d-4ddf-a4a7-6d3543328af5",
        "partner_name": "Dummy partner 1",
        "partner_status": "ACTIVE",
        "registration_ts": "2000-01-01 00:00:00+0000",
    }
]


def put_partner_in_db_ids(rds, partners, cleanup=True):
    """Insert partners into database before a test and clean up after the test"""
    partner_ids = []
    with rds.cursor() as cursor:
        for partner in partners:
            sql = """
            SELECT ingest.put_partner(
                %(partner_uuid)s,
                %(partner_name)s,
                %(partner_status)s,
                %(registration_ts)s
            ) partner_id;
            """
            cursor.execute(sql, partner)
            result = cursor.fetchone()
            rds.commit()
            partner_id = result["partner_id"]
            partner_ids.append(partner_id)
    yield partner_ids
    if cleanup:
        with rds.cursor() as cursor:
            partner_ids = [str(partner_id) for partner_id in partner_ids]
            sql = f"""
            DELETE FROM ingest.partner WHERE partner_id IN ({', '.join(partner_ids)});
            """
            cursor.execute(sql)
            rds.commit()


PRODUCTS = [
    {
        "partner_uuid": "aa61382a-a98d-4ddf-a4a7-6d3543328af5",
        "product_external_id": "PROD001",
        "product_title": "Dummy product title 1",
        "first_protection_ts": "2000-01-01 00:00:00+0000",
        "registration_ts": "2000-01-01 00:00:00+0000",
        "protection_status": "ACTIVE",
        "product_image_url": "https://api.movies.com/movies/1",
    },
    {
        "partner_uuid": "aa61382a-a98d-4ddf-a4a7-6d3543328af5",
        "product_external_id": "PROD002",
        "product_title": "Dummy product title 2",
        "first_protection_ts": "2000-01-01 00:00:01+0000",
        "registration_ts": "2000-01-01 00:00:01+0000",
        "protection_status": "INACTIVE",
        "product_image_url": "https://api.movies.com/movies/2",
    },
]


def put_product_in_db_ids(rds, products, cleanup=True):
    """Insert products into database before a test and clean up after the test"""
    product_ids = []
    with rds.cursor() as cursor:
        for product in products:
            sql = """
            SELECT ingest.put_product(
                %(partner_uuid)s,
                %(product_external_id)s,
                %(product_title)s,
                %(first_protection_ts)s,
                %(registration_ts)s,
                %(protection_status)s,
                %(product_image_url)s
            ) product_id;
            """
            cursor.execute(sql, product)
            result = cursor.fetchone()
            rds.commit()
            product_id = result["product_id"]
            product_ids.append(product_id)
    yield product_ids
    if cleanup:
        with rds.cursor() as cursor:
            product_ids = [str(product_id) for product_id in product_ids]
            sql = f"""
            DELETE FROM ingest.product WHERE product_id IN ({', '.join(product_ids)});
            """
            cursor.execute(sql)
            rds.commit()


PIRATE_SOURCES = [
    {
        "partner_uuid": "aa61382a-a98d-4ddf-a4a7-6d3543328af5",
        "pirate_source_external_id": "PSRC001",
        "pirate_source_name": "Dummy pirate source name 1",
        "pirate_source_type": "DUMMY_SEARCH_ENGINE",
        "registration_ts": "2000-01-01 00:00:00+0000",
    },
    {
        "partner_uuid": "aa61382a-a98d-4ddf-a4a7-6d3543328af5",
        "pirate_source_external_id": "PSRC002",
        "pirate_source_name": "Dummy pirate source name 2",
        "pirate_source_type": "DUMMY_SOCIAL_MEDIA",
        "registration_ts": "2000-01-01 00:00:00+0000",
    },
]


def put_pirate_source_in_db_ids(rds, pirate_sources, cleanup=True):
    """Insert pirate sources into database before a test and clean up after the test"""
    pirate_source_ids = []
    with rds.cursor() as cursor:
        for pirate_source in pirate_sources:
            sql = """
            SELECT ingest.put_pirate_source(
                %(partner_uuid)s,
                %(pirate_source_external_id)s,
                %(pirate_source_name)s,
                %(pirate_source_type)s,
                %(registration_ts)s
            ) pirate_source_id;
            """
            cursor.execute(sql, pirate_source)
            result = cursor.fetchone()
            rds.commit()
            pirate_source_id = result["pirate_source_id"]
            pirate_source_ids.append(pirate_source_id)
    yield pirate_source_ids
    if cleanup:
        with rds.cursor() as cursor:
            pirate_source_ids = [
                str(pirate_source_id) for pirate_source_id in pirate_source_ids
            ]
            sql = f"""
            DELETE FROM ingest.pirate_source
            WHERE pirate_source_id IN ({', '.join(pirate_source_ids)});
            """
            cursor.execute(sql)
            rds.commit()


INFRINGEMENTS = [
    {
        "partner_uuid": "aa61382a-a98d-4ddf-a4a7-6d3543328af5",
        "product_external_id": "PROD001",
        "pirate_source_external_id": "PSRC001",
        "detection_ts": "2000-01-01 00:00:00+0000",
        "infringement_url": "https://www.pirate1.com/movies/1",
        # pylint: disable=line-too-long
        "infringement_screenshot": '{"screenshotUrl": ["https://s3.aws.com/screenshot-01.jpg"]}',  # noqa: E501
        "infringement_status": "ACTIVE",
    },
    {
        "partner_uuid": "aa61382a-a98d-4ddf-a4a7-6d3543328af5",
        "product_external_id": "PROD001",
        "pirate_source_external_id": "PSRC002",
        "detection_ts": "2000-01-01 00:00:01+0000",
        "infringement_url": "https://www.pirate2.com/movies/1",
        # pylint: disable=line-too-long
        "infringement_screenshot": '{"screenshotUrl": ["https://s3.aws.com/screenshot-02.jpg"]}',  # noqa: E501
        "infringement_status": "TAKEN_DOWN",
    },
    {
        "partner_uuid": "aa61382a-a98d-4ddf-a4a7-6d3543328af5",
        "product_external_id": "PROD002",
        "pirate_source_external_id": "PSRC001",
        "detection_ts": "2000-01-01 00:00:02+0000",
        "infringement_url": "https://www.pirate1.com/movies/2",
        "infringement_screenshot": None,
        "infringement_status": "ACTIVE",
    },
]


def put_infringement_in_db_ids(rds, infringements, cleanup=True):
    """Insert infringements into database before a test and clean up after the test"""
    infringement_ids = []
    with rds.cursor() as cursor:
        for infringement in infringements:
            sql = """
            SELECT ingest.put_infringement(
                %(partner_uuid)s,
                %(product_external_id)s,
                %(pirate_source_external_id)s,
                %(detection_ts)s,
                %(infringement_url)s,
                %(infringement_status)s,
                %(infringement_screenshot)s
            ) infringement_id;
            """
            cursor.execute(sql, infringement)
            result = cursor.fetchone()
            rds.commit()
            infringement_id = result["infringement_id"]
            infringement_ids.append(infringement_id)
    yield infringement_ids
    if cleanup:
        with rds.cursor() as cursor:
            infringement_ids = [
                str(infringement_id) for infringement_id in infringement_ids
            ]
            sql = f"""
            DELETE FROM ingest.infringement
            WHERE infringement_id IN ({', '.join(infringement_ids)});
            """
            cursor.execute(sql)
            rds.commit()


def post_delete_dummy_infringement(rds):
    """post delete all infringements from database"""
    yield
    with rds.cursor() as cursor:
        sql = """
        DELETE FROM ingest.infringement
        WHERE product_id IN (
            SELECT p.product_id
            FROM ingest.product p
            WHERE p.product_external_id IN ('PROD001', 'PROD002')
        );
        """
        cursor.execute(sql)
        rds.commit()


def get_dummy_product_count(rds):
    """Get dummy product count from database"""
    with rds.cursor() as cursor:
        sql = """
        SELECT count(*) product_count
        FROM ingest.product p
        WHERE p.product_external_id IN ('PROD001', 'PROD002');
        """
        cursor.execute(sql)
        result = cursor.fetchone()
        product_count = result["product_count"]
        return product_count


def get_dummy_infringement_count(rds):
    """Get dummy infringement count from database"""
    with rds.cursor() as cursor:
        sql = """
        SELECT count(*) infringement_count
        FROM ingest.infringement i
            JOIN ingest.product p ON p.product_id = i.product_id
        WHERE p.product_external_id IN ('PROD001', 'PROD002');
        """
        cursor.execute(sql)
        result = cursor.fetchone()
        infringement_count = result["infringement_count"]
        return infringement_count


def get_infringement_by_id(rds, infringement_id):
    """Get infringement by id from database"""
    infringement = {}
    infringement["infringement_id"] = infringement_id
    with rds.cursor() as cursor:
        sql = """
        SELECT i.* FROM ingest.infringement i
        WHERE i.infringement_id = %(infringement_id)s;
        """
        cursor.execute(sql, infringement)
        result = cursor.fetchone()
        return result

def all_in(messages, log):
    return all([message in log for message in messages])


def all_not_in(messages, log):
    return all([message not in log for message in messages])


def create_transform_event(bucket_name, object_key):
    event = {
        "Records": [
            {
                "s3": {
                    "bucket": {
                        "name": bucket_name
                    },
                    "object": {
                        "key": object_key
                    },
                }
            }
        ]
    }
    return event


def get_product_count(rds):
    with rds.cursor() as cursor:
        sql = """SELECT COUNT(*) product_count FROM ingest.product;"""
        cursor.execute(sql)
        result = cursor.fetchone()
        product_count = result["product_count"]
        return product_count


def get_infringement_count(rds):
    with rds.cursor() as cursor:
        sql = """SELECT COUNT(*) infringement_count FROM ingest.infringement;"""
        cursor.execute(sql)
        result = cursor.fetchone()
        infringement_count = result["infringement_count"]
        return infringement_count

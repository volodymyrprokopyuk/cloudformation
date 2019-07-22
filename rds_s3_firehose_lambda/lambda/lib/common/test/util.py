def all_in(messages, log):
    return all([message in log for message in messages])


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

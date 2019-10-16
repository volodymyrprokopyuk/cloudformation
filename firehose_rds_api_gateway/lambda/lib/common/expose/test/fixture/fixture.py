from pytest import fixture
from common.expose.test.util import create_expose_event


# Expose event fixture
@fixture
def event():
    event = create_expose_event("GET", "/resource")
    return event

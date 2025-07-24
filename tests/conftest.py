import pytest


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
def vcr_config():
    return {
        "filter_headers": [("authorization", None)],
    }

import os
from collections.abc import AsyncGenerator

import pytest
from mcp.client.session import ClientSession
from mcp.server.fastmcp import FastMCP
from mcp.shared.memory import create_connected_server_and_client_session

from logfire_mcp.__main__ import app_factory


@pytest.fixture
def anyio_backend():
    return 'asyncio'


@pytest.fixture
def vcr_config():
    return {'filter_headers': [('authorization', None)]}


@pytest.fixture
async def logfire_read_token() -> str:
    # To get a read token, go to https://logfire-us.pydantic.dev/kludex/logfire-mcp/settings/read-tokens/.
    return os.getenv('LOGFIRE_READ_TOKEN', 'fake-token')


@pytest.fixture
def app(logfire_read_token: str) -> FastMCP:
    return app_factory(logfire_read_token)


@pytest.fixture
async def session(app: FastMCP) -> AsyncGenerator[ClientSession]:
    mcp_server = app._mcp_server  # type: ignore
    async with create_connected_server_and_client_session(mcp_server, raise_exceptions=True) as _session:
        yield _session

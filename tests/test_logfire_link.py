import os
from collections.abc import AsyncGenerator

import pytest
from mcp.client.session import ClientSession
from mcp.server.fastmcp import FastMCP
from mcp.shared.memory import create_connected_server_and_client_session
from mcp.types import TextContent

from logfire_mcp.__main__ import app_factory

pytestmark = [pytest.mark.vcr, pytest.mark.anyio]


@pytest.fixture
async def logfire_read_token() -> str:
    # To get a read token, go to https://logfire-us.pydantic.dev/kludex/logfire-mcp/settings/read-tokens/.
    return os.getenv("LOGFIRE_READ_TOKEN", "fake-token")


@pytest.fixture
def app(logfire_read_token: str) -> FastMCP:
    return app_factory(logfire_read_token, "https://api-us.pydantic.dev")


@pytest.fixture
async def session(app: FastMCP) -> AsyncGenerator[ClientSession]:
    mcp_server = app._mcp_server  # type: ignore
    async with create_connected_server_and_client_session(mcp_server, raise_exceptions=True) as _session:
        yield _session


async def test_logfire_link(session: ClientSession) -> None:
    result = await session.call_tool("logfire_link", {"trace_id": "019837e6ba8ab0ede383b398b6706f28"})

    assert result.content == [
        TextContent(
            type="text",
            text="https://logfire-us.pydantic.dev/kludex/logfire-mcp?q=trace_id%3D%27019837e6ba8ab0ede383b398b6706f28%27",
        )
    ]

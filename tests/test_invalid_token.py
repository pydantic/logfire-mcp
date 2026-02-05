import pytest
from mcp.server.fastmcp import FastMCP
from mcp.shared.memory import create_connected_server_and_client_session

from logfire_mcp.main import InvalidReadTokenError, app_factory

pytestmark = [pytest.mark.vcr, pytest.mark.anyio]


@pytest.fixture
def app_with_invalid_token() -> FastMCP:
    return app_factory('invalid-token')


async def test_invalid_token(app_with_invalid_token: FastMCP) -> None:
    mcp_server = app_with_invalid_token._mcp_server  # type: ignore
    with pytest.raises(ExceptionGroup) as exc_info:
        async with create_connected_server_and_client_session(mcp_server, raise_exceptions=True):
            pass

    # The exception is wrapped in an ExceptionGroup
    exception_group = exc_info.value
    assert len(exception_group.exceptions) == 1
    inner_exception = exception_group.exceptions[0]
    assert isinstance(inner_exception, InvalidReadTokenError)
    assert 'Invalid Logfire read token' in str(inner_exception)

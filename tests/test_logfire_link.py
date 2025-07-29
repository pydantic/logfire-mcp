import pytest
from mcp.client.session import ClientSession
from mcp.types import TextContent

pytestmark = [pytest.mark.vcr, pytest.mark.anyio]


async def test_logfire_link(session: ClientSession) -> None:
    result = await session.call_tool('logfire_link', {'trace_id': '019837e6ba8ab0ede383b398b6706f28'})

    assert result.content == [
        TextContent(
            type='text',
            text='https://logfire-us.pydantic.dev/kludex/logfire-mcp?q=trace_id%3D%27019837e6ba8ab0ede383b398b6706f28%27',
        )
    ]

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from importlib.metadata import version
from typing import Annotated, Any, TypedDict, cast

from logfire.experimental.query_client import AsyncLogfireQueryClient
from mcp.server.fastmcp import Context, FastMCP
from mcp.server.session import ServerSession
from pydantic import Field, WithJsonSchema


@dataclass
class MCPState:
    logfire_client: AsyncLogfireQueryClient


HOUR = 60  # minutes
DAY = 24 * HOUR

__version__ = version('logfire-mcp')

Age = Annotated[
    int,
    Field(
        ge=0,
        le=7 * 30 * DAY,
        description='Number of minutes to look back, e.g. 30 for last 30 minutes. Maximum allowed value is 30 days.',
    ),
    WithJsonSchema({'type': 'integer'}),
]


async def find_exceptions_in_file(
    ctx: Context[ServerSession, MCPState],
    filepath: Annotated[str, Field(description='The path to the file to find exceptions in.')],
    age: Age,
) -> list[Any]:
    """Get the details about the 10 most recent exceptions on the file."""
    logfire_client = ctx.request_context.lifespan_context.logfire_client
    min_timestamp = datetime.now(UTC) - timedelta(minutes=age)
    result = await logfire_client.query_json_rows(
        f"""\
        SELECT
            created_at,
            message,
            exception_type,
            exception_message,
            exception_stacktrace
        FROM records
        WHERE is_exception = true
            AND exception_stacktrace like '%{filepath}%'
        ORDER BY created_at DESC
        LIMIT 10
    """,
        min_timestamp=min_timestamp,
    )
    return result['rows']


async def arbitrary_query(
    ctx: Context[ServerSession, MCPState],
    query: Annotated[str, Field(description='The query to run, as a SQL string.')],
    age: Age,
) -> list[Any]:
    """Run an arbitrary query on the Pydantic Logfire database.

    The SQL reference is available via the `sql_reference` tool.
    """
    logfire_client = ctx.request_context.lifespan_context.logfire_client
    min_timestamp = datetime.now(UTC) - timedelta(minutes=age)
    result = await logfire_client.query_json_rows(query, min_timestamp=min_timestamp)
    return result['rows']


async def schema_reference(ctx: Context[ServerSession, MCPState]) -> str:
    """The database schema for the Logfire DataFusion database.

    This includes all tables, columns, and their types as well as descriptions.
    For example:

    ```sql
    -- The records table contains spans and logs.
    CREATE TABLE records (
        message TEXT, -- The message of the record
        span_name TEXT, -- The name of the span, message is usually templated from this
        trace_id TEXT, -- The trace ID, identifies a group of spans in a trace
        exception_type TEXT, -- The type of the exception
        exception_message TEXT, -- The message of the exception
        -- other columns...
    );
    ```
    The SQL syntax is similar to Postgres, although the query engine is actually Apache DataFusion.

    To access nested JSON fields e.g. in the `attributes` column use the `->` and `->>` operators.
    You may need to cast the result of these operators e.g. `(attributes->'cost')::float + 10`.

    You should apply as much filtering as reasonable to reduce the amount of data queried.
    Filters on `start_timestamp`, `service_name`, `span_name`, `metric_name`, `trace_id` are efficient.
    """
    logfire_client = ctx.request_context.lifespan_context.logfire_client
    response = await logfire_client.client.get('/v1/schemas')
    schema_data = response.json()

    def schema_to_sql(schema_json: dict[str, Any]) -> str:
        sql_commands: list[str] = []
        for table in schema_json.get('tables', []):
            table_name = table['name']
            columns: list[str] = []

            for col_name, col_info in table['schema'].items():
                data_type = col_info['data_type']
                nullable = col_info.get('nullable', True)
                description = col_info.get('description', '').strip()

                column_def = f'{col_name} {data_type}'
                if not nullable:
                    column_def += ' NOT NULL'
                if description:
                    column_def += f' -- {description}'

                columns.append(column_def)

            create_table = f'CREATE TABLE {table_name} (\n    ' + ',\n    '.join(columns) + '\n);'
            sql_commands.append(create_table)

        return '\n\n'.join(sql_commands)

    return schema_to_sql(schema_data)


async def logfire_link(
    ctx: Context[ServerSession, MCPState],
    trace_id: Annotated[str, Field(description='The trace ID to link to.')],
) -> str:
    """Creates a link to help the user to view the trace in the Logfire UI."""
    logfire_client = ctx.request_context.lifespan_context.logfire_client
    response = await logfire_client.client.get('/v1/read-token-info')
    read_token_info = cast(ReadTokenInfo, response.json())
    organization_name = read_token_info['organization_name']
    project_name = read_token_info['project_name']

    url = logfire_client.client.base_url
    url = url.join(f'{organization_name}/{project_name}')
    url = url.copy_add_param('q', f"trace_id='{trace_id}'")
    return str(url)


def app_factory(logfire_read_token: str, logfire_base_url: str | None = None) -> FastMCP:
    @asynccontextmanager
    async def lifespan(server: FastMCP) -> AsyncIterator[MCPState]:
        # print to stderr so we this message doesn't get read by the MCP client
        headers = {'User-Agent': f'logfire-mcp/{__version__}'}
        async with AsyncLogfireQueryClient(logfire_read_token, headers=headers, base_url=logfire_base_url) as client:
            yield MCPState(logfire_client=client)

    mcp = FastMCP('Logfire', lifespan=lifespan)
    mcp.tool()(find_exceptions_in_file)
    mcp.tool()(arbitrary_query)
    mcp.tool()(logfire_link)
    mcp.tool()(schema_reference)

    return mcp


class ReadTokenInfo(TypedDict):
    token_id: str
    organization_id: str
    project_id: str
    organization_name: str
    project_name: str

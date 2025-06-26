import argparse
import os
import re
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from importlib.metadata import version
from textwrap import indent
from typing import Annotated, Any, Literal, TypedDict, cast

from logfire.experimental.query_client import AsyncLogfireQueryClient
from mcp.server.fastmcp import Context, FastMCP
from mcp.server.session import ServerSession
from pydantic import AfterValidator

HOUR = 60  # minutes
DAY = 24 * HOUR

__version__ = version("logfire-mcp")


@dataclass
class MCPState:
    logfire_client: AsyncLogfireQueryClient


def validate_age(age: int) -> int:
    """Validate that the age is within acceptable bounds (positive and <= 7 days)."""
    if age <= 0:
        raise ValueError("Age must be positive")
    if age > 7 * DAY:
        raise ValueError("Age cannot be more than 7 days")
    return age


ValidatedAge = Annotated[int, AfterValidator(validate_age)]
"""We don't want to add exclusiveMaximum on the schema because it fails with some models."""


async def find_exceptions_in_file(ctx: Context[ServerSession, MCPState], filepath: str, age: ValidatedAge) -> list[Any]:
    """Get the details about the 10 most recent exceptions on the file.

    Args:
        filepath: The path to the file to find exceptions in.
        age: Number of minutes to look back, e.g. 30 for last 30 minutes. Maximum allowed value is 7 days.
    """
    logfire_client = ctx.request_context.lifespan_context.logfire_client
    min_timestamp = datetime.now(UTC) - timedelta(minutes=age)
    result = await logfire_client.query_json_rows(
        f"""\
        SELECT
            created_at,
            message,
            exception_type,
            exception_message,
            exception_stacktrace,
        FROM records
        WHERE is_exception = true
            AND exception_stacktrace like '%{filepath}%'
        ORDER BY created_at DESC
        LIMIT 10
    """,
        min_timestamp=min_timestamp,
    )
    return result["rows"]


async def arbitrary_query(ctx: Context[ServerSession, MCPState], query: str, age: ValidatedAge) -> list[Any]:
    """Run an arbitrary query on the Logfire database.

    The schema is available via the `get_logfire_records_schema` tool.

    Args:
        query: The query to run, as a SQL string.
        age: Number of minutes to look back, e.g. 30 for last 30 minutes. Maximum allowed value is 7 days.
    """
    logfire_client = ctx.request_context.lifespan_context.logfire_client
    min_timestamp = datetime.now(UTC) - timedelta(minutes=age)
    result = await logfire_client.query_json_rows(query, min_timestamp=min_timestamp)
    return result["rows"]


async def get_logfire_records_schema(ctx: Context[ServerSession, MCPState]) -> str:
    """Get the records schema from Logfire.

    To perform the `arbitrary_query` tool, you can use the `schema://records` to understand the schema.
    """
    logfire_client = ctx.request_context.lifespan_context.logfire_client
    result = await logfire_client.query_json_rows("SHOW COLUMNS FROM records")
    return build_schema_description(cast(list[SchemaRow], result["rows"]))


class SchemaRow(TypedDict):
    column_name: str
    data_type: str
    is_nullable: Literal["YES", "NO"]

    # These columns are less likely to be useful
    table_name: str  # could be useful if looking at both records _and_ metrics..
    table_catalog: str
    table_schema: str


def _remove_dictionary_encoding(data_type: str) -> str:
    result = re.sub(r"Dictionary\([^,]+, ([^,]+)\)", r"\1", data_type)
    return result


def build_schema_description(rows: list[SchemaRow]) -> str:
    normal_column_lines: list[str] = []
    attribute_lines: list[str] = []
    resource_attribute_lines: list[str] = []

    for row in rows:
        modifier = " IS NOT NULL" if row["is_nullable"] == "NO" else ""
        data_type = _remove_dictionary_encoding(row["data_type"])
        if row["column_name"].startswith("_lf_attributes"):
            name = row["column_name"][len("_lf_attributes/") :]
            attribute_lines.append(f"attributes->>'{name}' (type: {data_type}{modifier})")
        elif row["column_name"].startswith("_lf_otel_resource_attributes"):
            name = row["column_name"][len("_lf_otel_resource_attributes/") :]
            resource_attribute_lines.append(f"otel_resource_attributes->>'{name}' (type: {data_type}{modifier})")
        else:
            name = row["column_name"]
            normal_column_lines.append(f"{name} {data_type}{modifier}")

    normal_columns = ",\n".join(normal_column_lines)
    attributes = "\n".join([f"* {line}" for line in attribute_lines])
    resource_attributes = "\n".join([f"* {line}" for line in resource_attribute_lines])

    schema_description = f"""\
The following data was obtained by running the query "SHOW COLUMNS FROM records" in the Logfire datafusion database.
We present it here as pseudo-postgres-DDL, but this is a datafusion table.
Note that Logfire has support for special JSON querying so that you can use the `->` and `->>` operators like in Postgres, despite being a DataFusion database.

CREATE TABLE records AS (
{indent(normal_columns, "    ")}
)

Note that the `attributes` column can be interacted with like postgres JSONB.
It can have arbitrary user-specified fields, but the following fields are semantic conventions and have the specified types:
{attributes}

And for `otel_resource_attributes`:
{resource_attributes}
"""
    return schema_description


def app_factory(logfire_read_token: str, logfire_base_url: str) -> FastMCP:
    @asynccontextmanager
    async def lifespan(server: FastMCP) -> AsyncIterator[MCPState]:
        headers = {"User-Agent": f"logfire-mcp/{__version__}"}
        async with AsyncLogfireQueryClient(logfire_read_token, logfire_base_url, headers=headers) as client:
            yield MCPState(logfire_client=client)

    mcp = FastMCP("Logfire", lifespan=lifespan)
    mcp.tool()(find_exceptions_in_file)
    mcp.tool()(arbitrary_query)
    mcp.tool()(get_logfire_records_schema)

    return mcp


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--read-token",
        type=str,
        required=False,
        help="Logfire read token. Can also be set via LOGFIRE_READ_TOKEN environment variable.",
    )
    parser.add_argument(
        "--base-url",
        type=str,
        required=False,
        help="Logfire base URL. Can also be set via LOGFIRE_BASE_URL environment variable. "
        "Defaults to https://api-us.pydantic.dev",
    )
    args = parser.parse_args()

    # Get token from args or environment
    logfire_read_token = args.read_token or os.getenv("LOGFIRE_READ_TOKEN")
    if not logfire_read_token:
        parser.error(
            "Logfire read token must be provided either via --read-token argument "
            "or LOGFIRE_READ_TOKEN environment variable"
        )

    # Get base URL from args, environment, or default
    logfire_base_url = args.base_url or os.getenv("LOGFIRE_BASE_URL") or "https://api-us.pydantic.dev"

    app = app_factory(logfire_read_token, logfire_base_url)
    app.run(transport="stdio")


if __name__ == "__main__":
    main()

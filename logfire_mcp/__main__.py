import argparse
import asyncio
import os
import sys

from dotenv import dotenv_values, find_dotenv
from mcp import ClientSession, StdioServerParameters, stdio_client
from mcp.types import TextContent

from .main import __version__, app_factory


def main():
    name_version = f'Logfire MCP v{__version__}'
    parser = argparse.ArgumentParser(
        prog='logfire-mcp',
        description=f'{name_version}\n\nSee github.com/pydantic/logfire-mcp',
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        '--read-token',
        type=str,
        help='Pydantic Logfire read token. Can also be set via LOGFIRE_READ_TOKEN environment variable.',
    )
    parser.add_argument(
        '--base-url',
        type=str,
        required=False,
        help='Pydantic Logfire base URL. Can also be set via LOGFIRE_BASE_URL environment variable.',
    )
    parser.add_argument('--test', action='store_true', help='Test the MCP server and exit')
    parser.add_argument('--version', action='store_true', help='Show version and exit')
    args = parser.parse_args()
    if args.version:
        print(name_version)
        return

    # Get token from args or environment
    logfire_read_token, source = get_read_token(args)
    if not logfire_read_token:
        parser.error(
            'Pydantic Logfire read token must be provided either via --read-token argument '
            'or LOGFIRE_READ_TOKEN environment variable'
        )

    logfire_base_url = args.base_url or os.getenv('LOGFIRE_BASE_URL')
    if args.test:
        asyncio.run(test(logfire_read_token, logfire_base_url, source))
    else:
        app = app_factory(logfire_read_token, logfire_base_url)
        app.run(transport='stdio')


async def test(logfire_read_token: str, logfire_base_url: str | None, source: str):
    print('testing Logfire MCP server:\n')
    print(f'logfire_read_token: `{logfire_read_token[:12]}...{logfire_read_token[-5:]}` from {source}\n')

    args = ['-m', 'logfire_mcp', '--read-token', logfire_read_token]
    if logfire_base_url:
        print(f'logfire_base_url: `{logfire_base_url}`')
        args += ['--base-url', logfire_base_url]

    server_params = StdioServerParameters(command=sys.executable, args=args)
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            print('tools:')
            for tool in tools.tools:
                print(f'  - {tool.name}')

            list_resources = await session.list_resources()
            print('resources:')
            for resource in list_resources.resources:
                print(f'  - {resource.name}')

            for tool in 'sql_reference', 'get_logfire_records_schema':
                print(f'\ncalling `{tool}`:')
                output = await session.call_tool(tool)
                # debug(output)
                content = output.content[0]
                assert isinstance(content, TextContent), f'Expected TextContent, got {type(content)}'
                if len(content.text) < 200:
                    print(f'> {content.text.strip()}')
                else:
                    first_line = content.text.strip().split('\n', 1)[0]
                    print(f'> {first_line}... ({len(content.text) - len(first_line)} more characters)\n')


def get_read_token(args: argparse.Namespace) -> tuple[str | None, str]:
    if args.read_token:
        return args.read_token, 'CLI argument'
    elif token := os.getenv('LOGFIRE_READ_TOKEN'):
        return token, 'environment variable'
    else:
        return dotenv_values(dotenv_path=find_dotenv(usecwd=True)).get('LOGFIRE_READ_TOKEN'), 'dotenv file'


if __name__ == '__main__':
    main()

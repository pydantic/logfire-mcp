import argparse
import sys

from .main import __version__

USE_REMOTE_SERVER_MESSAGE = (
    'The logfire-mcp package (the local stdio MCP server) is deprecated and no longer maintained.\n'
    'Use the remote Logfire MCP server instead: https://logfire.pydantic.dev/docs/how-to-guides/mcp-server/'
)


def main():
    name_version = f'Logfire MCP v{__version__}'
    parser = argparse.ArgumentParser(
        prog='logfire-mcp',
        description=f'{name_version}\n\n{USE_REMOTE_SERVER_MESSAGE}\n\nSee github.com/pydantic/logfire-mcp',
        formatter_class=argparse.RawTextHelpFormatter,
    )
    # The following arguments are kept so that existing invocations still reach the deprecation message
    # below instead of failing with an "unrecognized arguments" error.
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

    sys.exit(USE_REMOTE_SERVER_MESSAGE)


if __name__ == '__main__':
    main()

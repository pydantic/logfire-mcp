import argparse
import os

from dotenv import load_dotenv

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
        required=False,
        help='Pydantic Logfire read token. Can also be set via LOGFIRE_READ_TOKEN environment variable.',
    )
    parser.add_argument('--version', action='store_true', help='Show version and exit')
    args = parser.parse_args()
    if args.version:
        print(name_version)
        return

    load_dotenv()
    # Get token from args or environment
    logfire_read_token = args.read_token or os.getenv('LOGFIRE_READ_TOKEN')
    if not logfire_read_token:
        parser.error(
            'Pydantic Logfire read token must be provided either via --read-token argument '
            'or LOGFIRE_READ_TOKEN environment variable'
        )

    app = app_factory(logfire_read_token)
    app.run(transport='stdio')


if __name__ == '__main__':
    main()

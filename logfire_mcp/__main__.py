import argparse
import os

from .main import app_factory


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--read-token",
        type=str,
        required=False,
        help="Pydantic Logfire read token. Can also be set via LOGFIRE_READ_TOKEN environment variable.",
    )
    parser.add_argument(
        "--base-url",
        type=str,
        required=False,
        help="Pydantic Logfire base URL. Can also be set via LOGFIRE_BASE_URL environment variable. "
        "Defaults to https://api-us.pydantic.dev",
    )
    args = parser.parse_args()

    # Get token from args or environment
    logfire_read_token = args.read_token or os.getenv("LOGFIRE_READ_TOKEN")
    if not logfire_read_token:
        parser.error(
            "Pydantic Logfire read token must be provided either via --read-token argument "
            "or LOGFIRE_READ_TOKEN environment variable"
        )

    # Get base URL from args, environment, or default
    logfire_base_url = args.base_url or os.getenv("LOGFIRE_BASE_URL") or "https://api-us.pydantic.dev"

    app = app_factory(logfire_read_token, logfire_base_url)
    app.run(transport="stdio")


if __name__ == "__main__":
    main()

# Logfire MCP Server

A Model Context Protocol server that provides access to Logfire logs and exceptions. This server enables LLMs to query your application logs, find exceptions, and perform custom queries using Logfire's query API, with automatic token-based authentication.

## Available Tools

* `find_exceptions` - Get exception counts grouped by file
  * Required arguments:
    * `age` (int): Number of minutes to look back (e.g., 30 for last 30 minutes, max 7 days)

* `find_exceptions_in_file` - Get detailed information about exceptions in a specific file
  * Required arguments:
    * `filepath` (string): Path to the file to analyze
    * `age` (int): Number of minutes to look back (max 7 days)

* `arbitrary_query` - Run custom SQL queries on your logs
  * Required arguments:
    * `query` (string): SQL query to execute
    * `age` (int): Number of minutes to look back (max 7 days)

* `get_logfire_records_schema` - Get the database schema to help with custom queries
  * No required arguments

## Installation

### Using pip (recommended)

Install `logfire-mcp` via pip:

```bash
pip install logfire-mcp
```

After installation, you can run it directly using:

```bash
logfire-mcp --read-token YOUR_TOKEN
```

Or using environment variables:

```bash
LOGFIRE_READ_TOKEN=YOUR_TOKEN logfire-mcp
```

## Configuration

### Configure for Cursor

Create a `.cursor/mcp.json` file in your project root:

```json
{
  "mcpServers": {
    "logfire": {
      "command": "logfire-mcp",
      "args": ["--read-token=YOUR-TOKEN"]
    }
  }
}
```

### Configure for Claude Desktop

Add to your Claude settings:

```json
{
  "command": ["logfire-mcp"],
  "type": "stdio",
  "env": {
    "LOGFIRE_READ_TOKEN": "YOUR_TOKEN"
  }
}
```

### Configure for Cline

Add to your Cline settings in `cline_mcp_settings.json`:

```json
{
  "mcpServers": {
    "logfire": {
      "command": "logfire-mcp",
      "env": {
        "LOGFIRE_READ_TOKEN": "YOUR_TOKEN"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

### Customization - Base URL

By default, the server connects to the Logfire API at `https://logfire-api.pydantic.dev`. You can override this by:

1. Using the `--base-url` argument:
```bash
logfire-mcp --base-url=https://your-logfire-instance.com
```

2. Setting the environment variable:
```bash
LOGFIRE_BASE_URL=https://your-logfire-instance.com logfire-mcp
```

## Example Interactions

1. Find all exceptions in the last hour:
```json
{
  "name": "find_exceptions",
  "arguments": {
    "age": 60
  }
}
```

Response:
```json
[
  {
    "filepath": "app/api.py",
    "count": 12
  },
  {
    "filepath": "app/models.py",
    "count": 5
  }
]
```

2. Get details about exceptions in a specific file:
```json
{
  "name": "find_exceptions_in_file",
  "arguments": {
    "filepath": "app/api.py",
    "age": 1440
  }
}
```

Response:
```json
[
  {
    "created_at": "2024-03-20T10:30:00Z",
    "message": "Failed to process request",
    "exception_type": "ValueError",
    "exception_message": "Invalid input format",
    "function_name": "process_request",
    "line_number": "42"
  }
]
```

3. Run a custom query:
```json
{
  "name": "arbitrary_query",
  "arguments": {
    "query": "SELECT message, created_at FROM records WHERE level = 'ERROR' ORDER BY created_at DESC LIMIT 10",
    "age": 1440
  }
}
```

## Examples of Questions for Claude

1. "What exceptions occurred in the last hour?"
2. "Show me the recent errors in the file 'app/api.py'"
3. "How many error logs were there in the last 24 hours?"
4. "What are the most common exception types in my application?"
5. "Get me the schema of the logs database"
6. "Run a query to find all critical errors from yesterday"

## Getting Started

1. First, obtain a Logfire read token from:
   https://logfire.pydantic.dev/-/redirect/latest-project/settings/read-tokens

2. Install the package:
   ```bash
   pip install logfire-mcp
   ```

3. Configure your preferred client (Cursor, Claude Desktop, or Cline) using the configuration examples above

4. Start using the MCP server to analyze your logs and exceptions!

## Contributing

We welcome contributions to help improve the Logfire MCP server. Whether you want to add new log analysis tools, enhance existing functionality, or improve documentation, your input is valuable.

For examples of other MCP servers and implementation patterns, see the [Model Context Protocol servers repository](https://github.com/modelcontextprotocol/servers).

## License

Logfire MCP is licensed under the MIT License. This means you are free to use, modify, and distribute the software, subject to the terms and conditions of the MIT License.

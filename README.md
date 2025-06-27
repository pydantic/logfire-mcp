# Logfire MCP Server

This repository contains a Model Context Protocol (MCP) server with tools that can access the OpenTelemetry traces and
metrics you've sent to Logfire.

<a href="https://glama.ai/mcp/servers/@pydantic/logfire-mcp">
  <img width="380" height="200" src="https://glama.ai/mcp/servers/@pydantic/logfire-mcp/badge" alt="Logfire Server MCP server" />
</a>

This MCP server enables LLMs to retrieve your application's telemetry data, analyze distributed
traces, and make use of the results of arbitrary SQL queries executed using the Logfire APIs.

## Available Tools

* `find_exceptions_in_file` - Get detailed trace information about exceptions in a specific file
  * Required arguments:
    * `filepath` (string): Path to the file to analyze
    * `age` (int): Number of minutes to look back (max 7 days)

* `arbitrary_query` - Run custom SQL queries on your OpenTelemetry traces and metrics
  * Required arguments:
    * `query` (string): SQL query to execute
    * `age` (int): Number of minutes to look back (max 7 days)

* `get_logfire_records_schema` - Get the OpenTelemetry schema to help with custom queries
  * No required arguments

## Setup
### Install `uv`

The first thing to do is make sure `uv` is installed, as `uv` is used to run the MCP server.

For installation instructions, see the [`uv` installation docs](https://docs.astral.sh/uv/getting-started/installation/).

If you already have an older version of `uv` installed, you might need to update it with `uv self update`.

### Obtain a Logfire read token
In order to make requests to the Logfire APIs, the Logfire MCP server requires a "read token".

You can create one under the "Read Tokens" section of your project settings in Logfire:
https://logfire.pydantic.dev/-/redirect/latest-project/settings/read-tokens

> [!IMPORTANT]
> Logfire read tokens are project-specific, so you need to create one for the specific project you want to expose to the Logfire MCP server.

### Manually run the server
Once you have `uv` installed and have a Logfire read token, you can manually run the MCP server using `uvx` (which is provided by `uv`).

You can specify your read token using the `LOGFIRE_READ_TOKEN` environment variable:

```bash
LOGFIRE_READ_TOKEN=YOUR_READ_TOKEN uvx logfire-mcp@latest
```

or using the `--read-token` flag:

```bash
uvx logfire-mcp@latest --read-token=YOUR_READ_TOKEN
```
> [!NOTE]
> If you are using Cursor, Claude Desktop, Cline, or other MCP clients that manage your MCP servers for you, you **_do
    NOT_** need to manually run the server yourself. The next section will show you how to configure these clients to make
    use of the Logfire MCP server.

## Configuration with well-known MCP clients

### Configure for Cursor

Create a `.cursor/mcp.json` file in your project root:

```json
{
  "mcpServers": {
    "logfire": {
      "command": "uvx",
      "args": ["logfire-mcp@latest", "--read-token=YOUR-TOKEN"]
    }
  }
}
```

The Cursor doesn't accept the `env` field, so you need to use the `--read-token` flag instead.

### Configure for Claude Desktop

Add to your Claude settings:

```json
{
  "command": ["uvx"],
  "args": ["logfire-mcp@latest"],
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
      "command": "uvx",
      "args": ["logfire-mcp@latest"],
      "env": {
        "LOGFIRE_READ_TOKEN": "YOUR_TOKEN"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```
### Configure for VS Code

Make sure you [enabled MCP support in VS Code](https://code.visualstudio.com/docs/copilot/chat/mcp-servers#_enable-mcp-support-in-vs-code).

Create a `.vscode/mcp.json` file in your project's root directory:

```json
{
  "servers": {
    "logfire": {
      "type": "stdio",
      "command": "uvx", // or the absolute /path/to/uvx
      "args": ["logfire-mcp@latest"],
      "env": {
        "LOGFIRE_READ_TOKEN": "YOUR_TOKEN",
        "LOGFIRE_BASE_URL": "https://api-eu.pydantic.dev" // choose the correct base url
      }
    }
  }
}
```

### Customization - Base URL

By default, the server connects to the Logfire API at `https://api-us.pydantic.dev`. You can override this by:

1. Using the `--base-url` argument:
```bash
uvx logfire-mcp@latest --base-url=https://your-logfire-instance.com
```

2. Setting the environment variable:
```bash
LOGFIRE_BASE_URL=https://your-logfire-instance.com uvx logfire-mcp@latest
```

## Example Interactions

1. Get details about exceptions from traces in a specific file:
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
    "line_number": "42",
    "attributes": {
      "service.name": "api-service",
      "code.filepath": "app/api.py"
    },
    "trace_id": "1234567890abcdef"
  }
]
```

2. Run a custom query on traces:
```json
{
  "name": "arbitrary_query",
  "arguments": {
    "query": "SELECT trace_id, message, created_at, attributes->>'service.name' as service FROM records WHERE severity_text = 'ERROR' ORDER BY created_at DESC LIMIT 10",
    "age": 1440
  }
}
```

## Examples of Questions for Claude

1. "What exceptions occurred in traces from the last hour across all services?"
2. "Show me the recent errors in the file 'app/api.py' with their trace context"
3. "How many errors were there in the last 24 hours per service?"
4. "What are the most common exception types in my traces, grouped by service name?"
5. "Get me the OpenTelemetry schema for traces and metrics"
6. "Find all errors from yesterday and show their trace contexts"

## Getting Started

1. First, obtain a Logfire read token from:
   https://logfire.pydantic.dev/-/redirect/latest-project/settings/read-tokens

2. Run the MCP server:
   ```bash
   uvx logfire-mcp@latest --read-token=YOUR_TOKEN
   ```

3. Configure your preferred client (Cursor, Claude Desktop, or Cline) using the configuration examples above

4. Start using the MCP server to analyze your OpenTelemetry traces and metrics!

## Contributing

We welcome contributions to help improve the Logfire MCP server. Whether you want to add new trace analysis tools, enhance metrics querying functionality, or improve documentation, your input is valuable.

For examples of other MCP servers and implementation patterns, see the [Model Context Protocol servers repository](https://github.com/modelcontextprotocol/servers).

## License

Logfire MCP is licensed under the MIT License. This means you are free to use, modify, and distribute the software, subject to the terms and conditions of the MIT License.

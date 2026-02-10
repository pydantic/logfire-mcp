# Pydantic Logfire MCP Server

This repository contains a Model Context Protocol (MCP) server with tools that can access the OpenTelemetry traces and
metrics you've sent to Pydantic Logfire.

## Remote MCP Server (Recommended)

Pydantic Logfire provides a hosted remote MCP server that you can use instead of running this package locally.
This is the easiest way to get started with the Logfire MCP server.

To use the remote MCP server, add the following configuration to your MCP client.

**Choose the endpoint that matches your Logfire data region:**

For **US region** (`logfire-us.pydantic.dev`):
```json
{
  "mcpServers": {
    "logfire": {
      "type": "http",
      "url": "https://logfire-us.pydantic.dev/mcp"
    }
  }
}
```

For **EU region** (`logfire-eu.pydantic.dev`):
```json
{
  "mcpServers": {
    "logfire": {
      "type": "http",
      "url": "https://logfire-eu.pydantic.dev/mcp"
    }
  }
}
```

> [!NOTE]
> The remote MCP server handles authentication automatically through your browser. When you first connect,
> you'll be prompted to authenticate with your Pydantic Logfire account.

> [!NOTE]
> If you are running a self-hosted Logfire instance, you should use the [Running Locally](#running-locally) section below
> to configure the MCP server with your custom base URL.

---

## Running Locally (Deprecated)

> [!WARNING]
> Running the MCP server locally is deprecated. Please use the [Remote MCP Server](#remote-mcp-server-recommended) instead.
> The local server will continue to work, but we recommend migrating to the remote server for a better experience.

If you prefer to run the MCP server locally, you can use this package instead.

<a href="https://glama.ai/mcp/servers/@pydantic/logfire-mcp">
  <img width="380" height="200" src="https://glama.ai/mcp/servers/@pydantic/logfire-mcp/badge" alt="Pydantic Logfire Server MCP server" />
</a>

This MCP server enables LLMs to retrieve your application's telemetry data, analyze distributed
traces, and make use of the results of arbitrary SQL queries executed using the Pydantic Logfire APIs.

## Available Tools

* `find_exceptions_in_file` - Get the details about the 10 most recent exceptions on the file.
  * Arguments:
    * `filepath` (string) - The path to the file to find exceptions in.
    * `age` (integer) - Number of minutes to look back, e.g. 30 for last 30 minutes. Maximum allowed value is 30 days.

* `arbitrary_query` - Run an arbitrary query on the Pydantic Logfire database.
  * Arguments:
    * `query` (string) - The query to run, as a SQL string.
    * `age` (integer) - Number of minutes to look back, e.g. 30 for last 30 minutes. Maximum allowed value is 30 days.

* `logfire_link` - Creates a link to help the user to view the trace in the Logfire UI.
  * Arguments:
    * `trace_id` (string) - The trace ID to link to.

* `schema_reference` - The database schema for the Logfire DataFusion database.


## Setup

### Install `uv`

The first thing to do is make sure `uv` is installed, as `uv` is used to run the MCP server.

For installation instructions, see the [`uv` installation docs](https://docs.astral.sh/uv/getting-started/installation/).

If you already have an older version of `uv` installed, you might need to update it with `uv self update`.

### Obtain a Pydantic Logfire read token
In order to make requests to the Pydantic Logfire APIs, the Pydantic Logfire MCP server requires a "read token".

You can create one under the "Read Tokens" section of your project settings in Pydantic Logfire:
https://logfire.pydantic.dev/-/redirect/latest-project/settings/read-tokens

> [!IMPORTANT]
> Pydantic Logfire read tokens are project-specific, so you need to create one for the specific project you want to expose to the Pydantic Logfire MCP server.

### Manually run the server

Once you have `uv` installed and have a Pydantic Logfire read token, you can manually run the MCP server using `uvx` (which is provided by `uv`).

You can specify your read token using the `LOGFIRE_READ_TOKEN` environment variable:

```bash
LOGFIRE_READ_TOKEN=YOUR_READ_TOKEN uvx logfire-mcp@latest
```

You can also set `LOGFIRE_READ_TOKEN` in a `.env` file:

```bash
LOGFIRE_READ_TOKEN=pylf_v1_us_...
```

**NOTE:** for this to work, the MCP server needs to run with the directory containing the `.env` file in its working directory.

or using the `--read-token` flag:

```bash
uvx logfire-mcp@latest --read-token=YOUR_READ_TOKEN
```
> [!NOTE]
> If you are using Cursor, Claude Desktop, Cline, or other MCP clients that manage your MCP servers for you, you **_do
    NOT_** need to manually run the server yourself. The next section will show you how to configure these clients to make
    use of the Pydantic Logfire MCP server.

### Base URL

If you are running Logfire in a self hosted environment, you need to specify the base URL.
This can be done using the `LOGFIRE_BASE_URL` environment variable:

```bash
LOGFIRE_BASE_URL=https://logfire.my-company.com uvx logfire-mcp@latest --read-token=YOUR_READ_TOKEN
```

You can also use the `--base-url` argument:

```bash
uvx logfire-mcp@latest --base-url=https://logfire.my-company.com --read-token=YOUR_READ_TOKEN
```

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

### Configure for Claude code

Run the following command:

```bash
claude mcp add logfire -e LOGFIRE_READ_TOKEN=YOUR_TOKEN -- uvx logfire-mcp@latest
```

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
        "LOGFIRE_READ_TOKEN": "YOUR_TOKEN"
      }
    }
  }
}
```

### Configure for Zed

Create a `.zed/settings.json` file in your project's root directory:

```json
{
  "context_servers": {
    "logfire": {
      "source": "custom",
      "command": "uvx",
      "args": ["logfire-mcp@latest"],
      "env": {
        "LOGFIRE_READ_TOKEN": "YOUR_TOKEN"
      },
      "enabled": true
    }
  }
}
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

1. First, obtain a Pydantic Logfire read token from:
   https://logfire.pydantic.dev/-/redirect/latest-project/settings/read-tokens

2. Run the MCP server:
   ```bash
   uvx logfire-mcp@latest --read-token=YOUR_TOKEN
   ```

3. Configure your preferred client (Cursor, Claude Desktop, or Cline) using the configuration examples above

4. Start using the MCP server to analyze your OpenTelemetry traces and metrics!

## Contributing

We welcome contributions to help improve the Pydantic Logfire MCP server. Whether you want to add new trace analysis tools, enhance metrics querying functionality, or improve documentation, your input is valuable.

For examples of other MCP servers and implementation patterns, see the [Model Context Protocol servers repository](https://github.com/modelcontextprotocol/servers).

## License

Pydantic Logfire MCP is licensed under the MIT License. This means you are free to use, modify, and distribute the software, subject to the terms and conditions of the MIT License.

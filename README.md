# Pydantic Logfire MCP Server

This repository contains a Model Context Protocol (MCP) server with tools that can access the OpenTelemetry traces and
metrics you've sent to Pydantic Logfire.

## Remote MCP Server (Recommended)

Pydantic Logfire provides a hosted remote MCP server that you can use instead of running this package locally.
This is the easiest way to get started with the Logfire MCP server.

To use the remote MCP server, add the following configuration to your MCP client.

**Choose the endpoint that matches your Logfire data region:**

- **US region** — `logfire-us.pydantic.dev`
- **EU region** — `logfire-eu.pydantic.dev`

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
> If you want to run logfire-mcp locally, check the [OLD_README.md](OLD_README.md) file.

## Configuration with well-known MCP clients

The examples below use the **US region** endpoint. Replace the URL with `https://logfire-eu.pydantic.dev/mcp` if you are using the EU region.

### Configure for Cursor

Create a `.cursor/mcp.json` file in your project root:

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

### Configure for Claude Code

Run the following command:

```bash
claude mcp add logfire --transport http https://logfire-us.pydantic.dev/mcp
```

### Configure for Claude Desktop

Add to your Claude settings:

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

### Configure for Cline

Add to your Cline settings in `cline_mcp_settings.json`:

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

### Configure for VS Code

Make sure you [enabled MCP support in VS Code](https://code.visualstudio.com/docs/copilot/chat/mcp-servers#_enable-mcp-support-in-vs-code).

Create a `.vscode/mcp.json` file in your project's root directory:

```json
{
  "servers": {
    "logfire": {
      "type": "http",
      "url": "https://logfire-us.pydantic.dev/mcp"
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
      "type": "http",
      "url": "https://logfire-us.pydantic.dev/mcp"
    }
  }
}
```

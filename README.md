# Logfire MCP

This is the code source for the Logfire MCP server.

## Installation

You can install the Logfire MCP server using pip:

```bash
pip install logfire-mcp
```

## Usage

First, you need a Logfire read token. You can create one at
https://logfire.pydantic.dev/-/redirect/latest-project/settings/read-tokens

After installing the package, you can run the server:

```bash
LOGFIRE_READ_TOKEN=your_token logfire-mcp
```

> [!NOTE]
> You can also set the `LOGFIRE_BASE_URL` environment variable to point to your own Logfire instance.
> This is mainly useful for Logfire developers for the time being, but will also be valuable for when we
> have a self-hosted Logfire instance.

The MCP server uses the `stdio` transport protocol for communication.

## Connect to the MCP server

Here's how to connect different clients to the MCP server:

### Cursor

You can configure Cursor by creating a `.cursor/mcp.json` file in your project root:

```json
{
  "mcpServers": {
    "logfire": {
      "command": "uvx",
      "args": ["logfire-mcp", "--logfire-read-token=YOUR-TOKEN"],
    }
  }
}
```

> [!NOTE]
> Unfortunately, cursor doesn't support the `env` field in the MCP configuration,
> so you need to pass the token via the `--logfire-read-token` flag.

For more detailed information, you can check the
[Cursor documentation](https://docs.cursor.com/context/model-context-protocol).

### Claude Desktop

In Claude Desktop, go to Settings → Advanced and add the following MCP configuration:
```json
{
  "command": ["logfire-mcp"],
  "type": "stdio",
  "env": {
    "LOGFIRE_READ_TOKEN": "your_token"
  }
}
```

Check out the [MCP quickstart](https://modelcontextprotocol.io/quickstart/user)
for more information.

### Cline

When using Cline, you can configure the `cline_mcp_settings.json` file to connect to the
MCP server:

```json
{
  "mcpServers": {
    "logfire": {
      "command": "uvx",
      "args": [
        "logfire-mcp",
      ],
      "env": {
        "LOGFIRE_READ_TOKEN": "your_token"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

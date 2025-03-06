# Logfire MCP

This is the code source for the Logfire MCP server.

For now, we only have a Docker container that you can pull from GitHub repository.

## Usage

First, you need a Logfire read token. You can create one at
https://logfire.pydantic.dev/-/redirect/latest-project/settings/read-tokens

Then, you can run the container:

```bash
docker run -e LOGFIRE_READ_TOKEN=your_token -p 8005:8005 ghcr.io/pydantic/logfire-mcp:latest
```

> [!NOTE]
> You can also set the `LOGFIRE_BASE_URL` environment variable to point to your own Logfire instance.
> This is mainly useful for Logfire developers for the time being, but will also be valuable for when we
> have a self-hosted Logfire instance.

Now the MCP server is running on port 8005. We use the `sse` transport, so you can connect to it using the following URL:

```bash
http://0.0.0.0:8005/sse
```

## Connect to the MCP server

### Cursor

You can check how to connect to the MCP server in the Cursor documentation:
https://docs.cursor.com/context/model-context-protocol

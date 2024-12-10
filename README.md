# mcp-transport-auth

A simple MCP server with basic auth transport.

## Usage

Start the server and client, using SSE transport with basic auth:

```bash
# MCP Server
## Using SSE transport with basic auth
USERNAME=admin PASSWORD=pass uv run mcp-transport-auth --port 8000

## Using SSE transport without basic auth
uv run mcp-transport-auth -w

# MCP Client
USERNAME=admin PASSWORD=pass uv run mcp-transport-auth-client
```

A simple MCP server that exposes

## Usage

Start the server using either stdio (default) or SSE transport:

```bash
# Using SSE transport with basic auth
uv run mcp-transport-auth

# Using SSE transport without basic auth
uv run mcp-transport-auth -w

# Using SSE transport on custom port
uv run mcp-transport-auth --port 8000
```

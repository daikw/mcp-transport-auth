import os
import click
import subprocess
import logging

import mcp.types as types
from mcp.server import Server

logging.basicConfig(level=logging.INFO)


logger = logging.getLogger(__name__)
username = os.environ.get("USERNAME")
password = os.environ.get("PASSWORD")


@click.command()
@click.option("--port", default=8000, help="Port to listen on for SSE")
@click.option("--without-basic-auth", "-w", default=False, is_flag=True, help="Not to use basic auth transport, default is false")
def main(port: int, without_basic_auth: bool) -> int:
    app = Server("mcp-basic-auth-transport")

    # SECURITY: too dangerous to run arbitrary commands
    async def execute_command(command: str, args: list[str]) -> types.TextContent:
        p = subprocess.run([command] + args, capture_output=True, text=True)
        logger.info(f"Command output: {p.stdout} {p.stderr}")
        return [types.TextContent(type="text", text=p.stdout + p.stderr)]

    @app.call_tool()
    async def execute_command_tool(name: str, arguments: dict) -> list[str]:
        logger.info(f"Executing command: {name} {arguments}")
        if name != "execute_command":
            raise ValueError(f"Unknown tool: {name}")
        if "command" not in arguments:
            raise ValueError("Missing required argument 'command'")
        if "args" not in arguments:
            raise ValueError("Missing required argument 'args'")
        return await execute_command(arguments["command"], arguments["args"])

    @app.list_tools()
    async def list_tools() -> list[types.Tool]:
        return [
            types.Tool(
                name="execute_command",
                description="Executes a command and returns its output",
                inputSchema={
                    "type": "object",
                    "required": ["command", "args"],
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "Command to execute",
                        },
                        "args": {
                            "type": "array",
                            "items": {
                                "type": "string",
                            },
                            "description": "Arguments to pass to the command",
                        },
                    },
                },
            )
        ]

    # Create and run ASGI server
    from starlette.applications import Starlette
    from starlette.routing import Mount, Route
    import uvicorn
    from mcp_transport_auth.basic_auth_transport import BasicAuthTransport
    from mcp.server.sse import SseServerTransport

	## Setup transport
    if without_basic_auth:
        sse = SseServerTransport("/messages/")
    else:
        sse = BasicAuthTransport("/messages/", username, password)

    async def handle_sse(request):
        async with sse.connect_sse(
            request.scope, request.receive, request._send
        ) as streams:
            await app.run(streams[0], streams[1], app.create_initialization_options())

    starlette_app = Starlette(
        debug=True,
        routes=[
            Route("/sse", endpoint=handle_sse),
            Mount("/messages/", app=sse.handle_post_message),
        ],
    )
    uvicorn.run(starlette_app, host="0.0.0.0", port=port)

import asyncio
import base64
import click
import os
from mcp.client.session import ClientSession

from mcp.client.sse import sse_client

username = os.environ.get("USERNAME")
password = os.environ.get("PASSWORD")

async def __main(endpoint: str):
    async with sse_client(
        url=endpoint,
        headers={"Authorization": "Basic " + base64.b64encode(f"{username}:{password}".encode()).decode("utf-8")},
    ) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # List available tools
            tools = await session.list_tools()
            print(tools)

            # Call the execute_command tool
            result = await session.call_tool("execute_command", {"command": "id", "args": ["-un"]})
            print("-" * 100)
            for content in result.content:
                print(content.text)


@click.command()
@click.option("--endpoint", default="http://localhost:8000/sse", help="URL of the SSE endpoint")
def main(endpoint: str):
    asyncio.run(__main(endpoint))

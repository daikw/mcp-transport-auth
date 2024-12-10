import base64
from contextlib import asynccontextmanager

from starlette.types import Scope, Receive, Send
from starlette.exceptions import HTTPException

from mcp.server.sse import SseServerTransport

class BasicAuthTransport(SseServerTransport):
    """
    Example basic auth implementation of SSE server transport.
    """
    def __init__(self, endpoint: str, username: str, password: str):
        super().__init__(endpoint)
        self.expected_header = b"Basic " + base64.b64encode(f"{username}:{password}".encode())

    @asynccontextmanager
    async def connect_sse(self, scope: Scope, receive: Receive, send: Send):
        auth_header = dict(scope["headers"]).get(b'authorization', b'')
        if auth_header != self.expected_header:
            raise HTTPException(status_code=401, detail="Unauthorized")
        async with super().connect_sse(scope, receive, send) as streams:
            yield streams

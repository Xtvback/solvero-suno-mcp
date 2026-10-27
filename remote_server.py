"""Optional HTTP transport, protected by a shared bearer token.

This is a single-owner development deployment, NOT OAuth.
Do not expose it to ChatGPT until compatible OAuth is implemented.
"""
import hmac
import os
from contextlib import asynccontextmanager

import uvicorn
from starlette.applications import Starlette
from starlette.routing import Mount, Route
from starlette.responses import JSONResponse

from server import app as mcp

token = os.environ.get("MCP_BEARER_TOKEN", "")
if len(token) < 32:
    raise RuntimeError("Set MCP_BEARER_TOKEN to a random secret of at least 32 characters.")

async def health(request):
    return JSONResponse({"status": "ok"})

class BearerAuth:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http" and scope.get("path") != "/health":
            headers = dict(scope.get("headers", []))
            supplied = headers.get(b"authorization", b"").decode("latin-1")
            expected = "Bearer " + token
            if not hmac.compare_digest(supplied, expected):
                body = b'{"error":"unauthorized"}'
                await send({"type": "http.response.start", "status": 401,
                            "headers": [(b"content-type", b"application/json"),
                                        (b"content-length", str(len(body)).encode())]})
                await send({"type": "http.response.body", "body": body})
                return
        await self.app(scope, receive, send)

@asynccontextmanager
async def lifespan(app):
    async with mcp.session_manager.run():
        yield

web_app = Starlette(routes=[Route("/health", health, methods=["GET"]), Mount("/mcp", app=mcp.streamable_http_app())], lifespan=lifespan)
application = BearerAuth(web_app)

if __name__ == "__main__":
    uvicorn.run(application, host=os.environ.get("HOST", "127.0.0.1"),
                port=int(os.environ.get("PORT", "8000")))

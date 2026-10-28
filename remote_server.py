"""Remote MCP transport protected by Auth0 OAuth access tokens."""
import os
from contextlib import asynccontextmanager

import uvicorn
from starlette.applications import Starlette
from starlette.routing import Mount, Route
from starlette.responses import JSONResponse

from auth import AccessTokenError, Auth0JWTValidator, AuthSettings
from server import app as mcp

settings = AuthSettings.from_env()
validator = Auth0JWTValidator(settings)

async def health(request):
    return JSONResponse({"status": "ok", "release": "chat-production-v1",
                         "tools": ["prepare_music_project", "prepare_release_handoff"]})

async def protected_resource_metadata(request):
    return JSONResponse(
        settings.protected_resource_metadata(),
        headers={"Cache-Control": "public, max-age=300"},
    )

class OAuthBearerAuth:
    def __init__(self, app, token_validator=validator):
        self.app = app
        self.token_validator = token_validator

    async def _reject(self, send, error=None):
        challenge = (
            'Bearer resource_metadata="' + settings.resource_metadata_url
            + '", scope="' + settings.required_scope + '"'
        )
        if error:
            challenge += ', error="' + error + '"'
        body = b'{"error":"unauthorized"}'
        await send({
            "type": "http.response.start", "status": 401,
            "headers": [
                (b"content-type", b"application/json"),
                (b"content-length", str(len(body)).encode()),
                (b"www-authenticate", challenge.encode("ascii")),
                (b"cache-control", b"no-store"),
            ],
        })
        await send({"type": "http.response.body", "body": body})

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http" and scope.get("path", "").startswith("/mcp"):
            headers = dict(scope.get("headers", []))
            supplied = headers.get(b"authorization", b"").decode("latin-1")
            scheme, separator, token = supplied.partition(" ")
            if separator != " " or scheme.lower() != "bearer" or not token:
                await self._reject(send)
                return
            try:
                self.token_validator.validate(token)
            except AccessTokenError as exc:
                error = "insufficient_scope" if "scope" in str(exc).lower() else "invalid_token"
                await self._reject(send, error=error)
                return
        await self.app(scope, receive, send)

@asynccontextmanager
async def lifespan(app):
    async with mcp.session_manager.run():
        yield

web_app = Starlette(routes=[
    Route("/health", health, methods=["GET"]),
    Route("/.well-known/oauth-protected-resource", protected_resource_metadata, methods=["GET"]),
    Route("/.well-known/oauth-protected-resource/mcp", protected_resource_metadata, methods=["GET"]),
    Mount("/", app=mcp.streamable_http_app()),
], lifespan=lifespan)
application = OAuthBearerAuth(web_app)

if __name__ == "__main__":
    uvicorn.run(application, host=os.environ.get("HOST", "127.0.0.1"),
                port=int(os.environ.get("PORT", "8000")))

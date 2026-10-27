"""Auth0 access-token validation and MCP OAuth resource metadata."""

from __future__ import annotations

import os
from dataclasses import dataclass
from urllib.parse import urlsplit

import jwt
from jwt import PyJWKClient, PyJWKClientError
from jwt.exceptions import PyJWTError


class AuthConfigurationError(RuntimeError):
    """Raised when required OAuth settings are absent or unsafe."""


class AccessTokenError(ValueError):
    """Raised when a bearer token cannot authorize an MCP request."""


@dataclass(frozen=True)
class AuthSettings:
    issuer: str
    audience: str
    required_scope: str
    jwks_url: str
    resource_metadata_url: str

    @classmethod
    def from_env(cls) -> "AuthSettings":
        issuer = os.environ.get("AUTH0_ISSUER", "https://solvero-mcp.eu.auth0.com/").strip()
        audience = os.environ.get(
            "AUTH0_AUDIENCE", "https://solvero-suno-mcp.onrender.com/mcp"
        ).strip()
        required_scope = os.environ.get("AUTH0_REQUIRED_SCOPE", "mcp:tools").strip()

        if not issuer.startswith("https://") or not issuer.endswith("/"):
            raise AuthConfigurationError("AUTH0_ISSUER must be an HTTPS URL ending in '/'.")
        if not audience.startswith("https://"):
            raise AuthConfigurationError("AUTH0_AUDIENCE must be an HTTPS resource identifier.")
        if not required_scope or any(char.isspace() for char in required_scope):
            raise AuthConfigurationError("AUTH0_REQUIRED_SCOPE must contain one scope value.")

        audience_url = urlsplit(audience)
        resource_metadata_url = (
            f"{audience_url.scheme}://{audience_url.netloc}/.well-known/oauth-protected-resource"
        )
        return cls(
            issuer=issuer,
            audience=audience,
            required_scope=required_scope,
            jwks_url=issuer + ".well-known/jwks.json",
            resource_metadata_url=resource_metadata_url,
        )

    def protected_resource_metadata(self) -> dict:
        return {
            "resource": self.audience,
            "authorization_servers": [self.issuer],
            "scopes_supported": [self.required_scope],
            "bearer_methods_supported": ["header"],
        }


class Auth0JWTValidator:
    """Validate RS256 Auth0 access tokens with cached JWKS key lookup."""

    def __init__(self, settings: AuthSettings):
        self.settings = settings
        self.jwks_client = PyJWKClient(settings.jwks_url, cache_keys=True, lifespan=300)

    def validate(self, token: str) -> dict:
        try:
            signing_key = self.jwks_client.get_signing_key_from_jwt(token)
            claims = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                audience=self.settings.audience,
                issuer=self.settings.issuer,
                options={"require": ["exp", "iat", "iss", "aud", "sub"]},
            )
        except (PyJWTError, PyJWKClientError) as exc:
            raise AccessTokenError("The access token is invalid or expired.") from exc

        granted_scopes = set(str(claims.get("scope", "")).split())
        permissions = claims.get("permissions", [])
        if isinstance(permissions, list):
            granted_scopes.update(str(value) for value in permissions)
        if self.settings.required_scope not in granted_scopes:
            raise AccessTokenError("The access token does not grant the required scope.")
        return claims

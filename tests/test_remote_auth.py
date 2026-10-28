"""Security regression tests for the remote OAuth boundary."""
import importlib.util
import os
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch

import jwt
from cryptography.hazmat.primitives.asymmetric import rsa
from starlette.testclient import TestClient

fake_server = types.ModuleType("server")
class FakeSession:
    async def __aenter__(self): return self
    async def __aexit__(self, *args): return False
class FakeManager:
    def run(self): return FakeSession()
class FakeMCP:
    session_manager = FakeManager()
    def streamable_http_app(self):
        async def handler(scope, receive, send):
            body = b"mcp protected"
            await send({"type":"http.response.start","status":200,
                        "headers":[(b"content-length",str(len(body)).encode())]})
            await send({"type":"http.response.body","body":body})
        return handler
fake_server.app = FakeMCP()
sys.modules["server"] = fake_server

ENV = {
    "AUTH0_ISSUER": "https://solvero-mcp.eu.auth0.com/",
    "AUTH0_AUDIENCE": "https://solvero-suno-mcp.onrender.com/mcp",
    "AUTH0_REQUIRED_SCOPE": "mcp:tools",
}
with patch.dict(os.environ, ENV, clear=False):
    spec = importlib.util.spec_from_file_location(
        "remote_under_test", Path(__file__).resolve().parents[1] / "remote_server.py"
    )
    remote = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(remote)


class FakeValidator:
    def __init__(self, outcome=None): self.outcome = outcome
    def validate(self, token):
        if isinstance(self.outcome, Exception): raise self.outcome
        return self.outcome or {"sub": "user"}


class AuthBoundaryTests(unittest.TestCase):
    def test_public_health_and_metadata(self):
        with TestClient(remote.application) as client:
            health = client.get("/health").json()
            self.assertEqual(health["status"], "ok")
            self.assertEqual(health["release"], "chat-production-v1")
            self.assertIn("prepare_music_project", health["tools"])
            response = client.get("/.well-known/oauth-protected-resource")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["resource"], ENV["AUTH0_AUDIENCE"])
            self.assertEqual(response.json()["authorization_servers"], [ENV["AUTH0_ISSUER"]])
            self.assertEqual(response.json()["scopes_supported"], ["mcp:tools"])

    def test_mcp_rejects_missing_and_invalid_tokens_with_discovery_challenge(self):
        app = remote.OAuthBearerAuth(remote.web_app, FakeValidator(remote.AccessTokenError("bad")))
        with TestClient(app) as client:
            for headers in ({}, {"Authorization": "Basic abc"}, {"Authorization": "Bearer bad"}):
                with self.subTest(headers=headers):
                    response = client.post("/mcp/", headers=headers)
                    self.assertEqual(response.status_code, 401)
                    self.assertIn("resource_metadata=", response.headers["www-authenticate"])
                    self.assertIn('scope="mcp:tools"', response.headers["www-authenticate"])

    def test_mcp_accepts_validated_token(self):
        app = remote.OAuthBearerAuth(remote.web_app, FakeValidator())
        with TestClient(app) as client:
            response = client.post("/mcp/", headers={"Authorization": "Bearer valid"})
            self.assertEqual(response.status_code, 200)


class JWTValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        cls.public_key = cls.private_key.public_key()

    def token(self, **overrides):
        import time
        now = int(time.time())
        claims = {
            "iss": ENV["AUTH0_ISSUER"], "aud": ENV["AUTH0_AUDIENCE"],
            "sub": "auth0|test", "iat": now, "exp": now + 300, "scope": "mcp:tools",
        }
        claims.update(overrides)
        return jwt.encode(claims, self.private_key, algorithm="RS256", headers={"kid": "test"})

    def validator(self):
        validator = remote.Auth0JWTValidator(remote.settings)
        validator.jwks_client = types.SimpleNamespace(
            get_signing_key_from_jwt=lambda token: types.SimpleNamespace(key=self.public_key)
        )
        return validator

    def test_valid_token(self):
        self.assertEqual(self.validator().validate(self.token())["sub"], "auth0|test")

    def test_wrong_audience_expiry_and_scope_are_rejected(self):
        import time
        cases = [
            self.token(aud="https://other.example/mcp"),
            self.token(exp=int(time.time()) - 1),
            self.token(scope="openid profile"),
        ]
        for token in cases:
            with self.subTest(token=token[:20]), self.assertRaises(remote.AccessTokenError):
                self.validator().validate(token)

    def test_permissions_claim_can_grant_scope(self):
        token = self.token(scope="", permissions=["mcp:tools"])
        self.assertEqual(self.validator().validate(token)["sub"], "auth0|test")


if __name__ == "__main__":
    unittest.main()

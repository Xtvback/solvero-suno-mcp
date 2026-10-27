"""Security regression tests for the remote HTTP authentication boundary."""
import importlib.util
import os
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch

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

with patch.dict(os.environ, {"MCP_BEARER_TOKEN": "a" * 48}):
    spec = importlib.util.spec_from_file_location("remote_under_test", Path(__file__).resolve().parents[1] / "remote_server.py")
    remote = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(remote)

class AuthTests(unittest.TestCase):
    def test_public_health(self):
        with TestClient(remote.application) as client:
            response = client.get("/health")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), {"status": "ok"})

    def test_mcp_rejects_missing_or_wrong_token(self):
        with TestClient(remote.application) as client:
            for headers in ({}, {"Authorization": "Bearer wrong"}):
                with self.subTest(headers=headers):
                    self.assertEqual(client.post("/mcp/", headers=headers).status_code, 401)

    def test_mcp_accepts_valid_token(self):
        with TestClient(remote.application) as client:
            response = client.post("/mcp/", headers={"Authorization": "Bearer " + "a" * 48})
            self.assertEqual(response.status_code, 200)

if __name__ == "__main__":
    unittest.main()

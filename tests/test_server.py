"""Offline tests: stub MCP decorator; no external account/API needed."""
import importlib.util
import os
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

fake_mcp = types.ModuleType("mcp")
fake_server = types.ModuleType("mcp.server")
fake_fastmcp = types.ModuleType("mcp.server.fastmcp")
class FastMCP:
    def __init__(self, name, **kwargs): self.name = name
    def tool(self): return lambda fn: fn
fake_fastmcp.FastMCP = FastMCP
fake_transport_security = types.ModuleType("mcp.server.transport_security")
fake_transport_security.TransportSecuritySettings = lambda **kwargs: kwargs
fake_server.fastmcp = fake_fastmcp
fake_server.transport_security = fake_transport_security
fake_mcp.server = fake_server
sys.modules.update({"mcp": fake_mcp, "mcp.server": fake_server, "mcp.server.fastmcp": fake_fastmcp,
                    "mcp.server.transport_security": fake_transport_security})
spec = importlib.util.spec_from_file_location("server_under_test", Path(__file__).resolve().parents[1] / "server.py")
server = importlib.util.module_from_spec(spec)
spec.loader.exec_module(server)

class OfflineTests(unittest.TestCase):
    def test_tools_exist(self):
        for name in ["list_songs","prepare_song_brief","prepare_music_project",
                     "prepare_release_handoff","save_song_record"]:
            self.assertTrue(callable(getattr(server, name)))
    def test_brief_and_catalogue(self):
        with tempfile.TemporaryDirectory() as d:
            with patch.object(server, "DATA_DIR", Path(d)), patch.object(server, "CATALOGUE", Path(d) / "songs.json"):
                self.assertEqual(server.list_songs(), [])
                brief = server.prepare_song_brief("Teste", "Solvero", "Tema", "Fado")
                self.assertFalse(brief["sent_to_suno"])
                server.save_song_record("Teste", "Solvero", "Fado")
                self.assertEqual(len(server.list_songs("solvero")), 1)
                self.assertEqual(len(server.list_songs("outra")), 0)
    def test_invalid_brief(self):
        with self.assertRaises(ValueError):
            server.prepare_song_brief("", "Solvero", "Tema", "Fado")

if __name__ == "__main__":
    unittest.main()

"""Offline-only authentication safety test. Never contacts Suno."""
import json
import os
from pathlib import Path
import tempfile
import unittest

class AuthBoundaryTest(unittest.TestCase):
    def test_mock_state_not_exposed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            state = root / "auth.json"
            state.write_text(json.dumps({"cookies": [{"name": "TEST_ONLY", "value": "FAKE_TOKEN_DO_NOT_USE"}]}))
            # Validate only the shape, never print or upload this file
            data = json.loads(state.read_text())
            self.assertEqual(len(data["cookies"]), 1)
            self.assertTrue(state.exists())
            state.unlink()
            self.assertFalse(state.exists())

    def test_real_suno_auth_not_configured(self):
        self.assertNotIn("SUNO_COOKIE", os.environ)
        self.assertNotIn("SUNO_SESSION", os.environ)

if __name__ == "__main__":
    unittest.main()

import hashlib
import tempfile
import unittest
from pathlib import Path
from tools.drive_handoff_manifest import prepare_handoff

URL = "https://suno.com/song/be108fa8-2efa-4aea-b32d-22f60b8e78fb"

class DriveHandoffTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "official.mp3"
        self.data = b"ID3" + b"SYNTHETIC-GEOB-PROVENANCE" + bytes(300)
        self.path.write_bytes(self.data)

    def test_pure_manifest(self):
        result = prepare_handoff(self.path, URL, "Static Riot", "Nobody Gets Close to You",
            approved_download=True, existing_names=[])
        self.assertEqual(result["source"]["sha256"], hashlib.sha256(self.data).hexdigest())
        self.assertEqual(result["destination"]["file_name"], "Static Riot - Nobody Gets Close to You.mp3")
        self.assertEqual(result["destination"]["folder_id"], "11xkA5Hc2tqQhYX8tu2HgGZu5rKR_Q62k")
        self.assertFalse(result["policy"]["embed_cover_art"])
        self.assertFalse(result["policy"]["uploaded"])
        self.assertEqual(self.path.read_bytes(), self.data)

    def test_duplicate_blocks_handoff(self):
        with self.assertRaises(ValueError):
            prepare_handoff(self.path, URL, "Static Riot", "Nobody Gets Close to You",
                approved_download=True, existing_names=["STATIC RIOT - NOBODY GETS CLOSE TO YOU.MP3"])

    def test_unauthorized_blocks_handoff(self):
        with self.assertRaises(ValueError):
            prepare_handoff(self.path, URL, "Static Riot", "Nobody Gets Close to You",
                approved_download=False, existing_names=[])

if __name__ == "__main__":
    unittest.main()

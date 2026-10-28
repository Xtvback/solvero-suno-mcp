import unittest
from archive_rules import plan_song_archive

URL = "https://suno.com/song/be108fa8-2efa-4aea-b32d-22f60b8e78fb"

class ArchiveRulesTests(unittest.TestCase):
    def test_static_riot_plan(self):
        r = plan_song_archive(URL, "Static Riot", "Nobody Gets Close to You", [
            "001 - Sweet Taste Of Poison.mp3", "static-riot---loud-guitars.mp3",
        ])
        self.assertEqual(r["filename"], "Static Riot - Nobody Gets Close to You.mp3")
        self.assertTrue(r["download_allowed"])
        self.assertEqual(r["archive_status"], "not-downloaded")

    def test_duplicate_prevents_new_download(self):
        r = plan_song_archive(URL, "STATIC RIOT", "Static Riot - Nobody Gets Close to You", [
            "static riot - nobody gets close to you.mp3"
        ])
        self.assertFalse(r["download_allowed"])

    def test_unknown_band_rejected(self):
        with self.assertRaises(ValueError):
            plan_song_archive(URL, "Unverified Band", "Example")

if __name__ == "__main__":
    unittest.main()

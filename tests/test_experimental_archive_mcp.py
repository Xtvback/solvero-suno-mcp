import asyncio
import unittest
from experimental_archive_mcp import experimental_app, archive_song
URL="https://suno.com/song/be108fa8-2efa-4aea-b32d-22f60b8e78fb"
class ExperimentalMCPTests(unittest.TestCase):
    def test_tool_registered_with_two_phase_schema(self):
        tools=asyncio.run(experimental_app.list_tools())
        matches=[x for x in tools if x.name=="archive_song"]
        self.assertEqual(len(matches),1)
        schema=matches[0].inputSchema
        self.assertIn("stage",schema["properties"])
        self.assertIn("confirmation",schema["properties"])
        self.assertIn("stage",schema["required"])
    def test_prepare_synthetic_only_and_no_upload(self):
        result=archive_song("prepare",URL)
        self.assertEqual(result["status"],"awaiting_confirmation")
        self.assertTrue(result["synthetic_only"])
        self.assertFalse(result["commit_enabled"])
        self.assertFalse(result["uploaded"])
        self.assertEqual(len(result["files"]),3)
    def test_commit_is_blocked_even_with_confirmation(self):
        result=archive_song("commit",URL,confirmation="CONFIRM ARCHIVE abcdef")
        self.assertEqual(result["status"],"blocked")
        self.assertFalse(result["uploaded"])
    def test_invalid_stage_rejected(self):
        with self.assertRaises(ValueError):archive_song("upload",URL)
    def test_invalid_canonical_song_link_rejected(self):
        with self.assertRaises(ValueError):archive_song("prepare","https://untrusted.invalid/song/abc")
if __name__=="__main__":unittest.main()

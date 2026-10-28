import asyncio
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from experimental_archive_mcp import experimental_app,archive_song
URL="https://suno.com/song/be108fa8-2efa-4aea-b32d-22f60b8e78fb"
class ExperimentalMCPTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.env=patch.dict(os.environ,{"SOLVERO_EXPERIMENT_APPROVAL_DB":str(Path(self.tmp.name)/"approvals.sqlite3"),"SOLVERO_EXPERIMENT_AUTHENTICATED_PRINCIPAL":"synthetic-user"})
        self.env.start();self.addCleanup(self.env.stop)
    def test_schema(self):
        tools=asyncio.run(experimental_app.list_tools())
        matches=[x for x in tools if x.name=="archive_song"]
        self.assertEqual(len(matches),1)
        fields=matches[0].inputSchema["properties"]
        for field in ("stage","request_id","confirmation"):self.assertIn(field,fields)
    def test_persistent_prepare(self):
        out=archive_song("prepare",URL)
        self.assertTrue(out["persistent_state"])
        self.assertEqual(out["status"],"awaiting_confirmation")
        self.assertEqual(len(out["files"]),3)
        self.assertTrue(Path(os.environ["SOLVERO_EXPERIMENT_APPROVAL_DB"]).exists())
    def test_commit_consumes_and_never_uploads(self):
        out=archive_song("prepare",URL)
        result=archive_song("commit",URL,request_id=out["request_id"],confirmation=out["confirmation"])
        self.assertEqual(result["status"],"blocked")
        self.assertEqual(result["approval_status"],"consumed")
        self.assertFalse(result["uploaded"])
    def test_replay_blocked(self):
        out=archive_song("prepare",URL)
        args={"request_id":out["request_id"],"confirmation":out["confirmation"]}
        archive_song("commit",URL,**args)
        with self.assertRaises(PermissionError):archive_song("commit",URL,**args)
    def test_changed_title_invalidates(self):
        out=archive_song("prepare",URL)
        with self.assertRaises(PermissionError):archive_song("commit",URL,title="Changed",request_id=out["request_id"],confirmation=out["confirmation"])
    def test_identity_change_refused(self):
        out=archive_song("prepare",URL)
        with patch.dict(os.environ,{"SOLVERO_EXPERIMENT_AUTHENTICATED_PRINCIPAL":"another-user"}):
            with self.assertRaises(PermissionError):archive_song("commit",URL,request_id=out["request_id"],confirmation=out["confirmation"])
    def test_no_identity_fails_closed(self):
        with patch.dict(os.environ,{"SOLVERO_EXPERIMENT_AUTHENTICATED_PRINCIPAL":""}):
            with self.assertRaises(PermissionError):archive_song("prepare",URL)
    def test_bad_url_and_stage(self):
        with self.assertRaises(ValueError):archive_song("prepare","https://invalid.test/song/id")
        with self.assertRaises(ValueError):archive_song("invalid",URL)
if __name__=="__main__":unittest.main()

import pathlib, sqlite3, unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
class ScaffoldTests(unittest.TestCase):
    def test_d1_schema_sqlite_compatible_and_replay_guard(self):
        db=sqlite3.connect(":memory:")
        db.executescript((ROOT/"schema.sql").read_text())
        db.execute("INSERT INTO archive_approvals VALUES (?,?,?,?,?,?,?,?)",
            ("req","synthetic-user","a"*64,"b"*64,"c"*64,200,"pending",100))
        row=db.execute("UPDATE archive_approvals SET state='consumed' WHERE request_id='req' AND state='pending'")
        self.assertEqual(row.rowcount,1)
        self.assertEqual(db.execute("UPDATE archive_approvals SET state='consumed' WHERE request_id='req' AND state='pending'").rowcount,0)
        db.close()
    def test_worker_never_enables_upload_or_unauthenticated_mcp(self):
        code=(ROOT/"src"/"index.js").read_text()
        self.assertIn('uploads_enabled:false',code)
        self.assertIn('oauth_ready:false',code)
        self.assertIn('oauth_not_configured',code)
        self.assertIn('503',code)
    def test_no_live_cloudflare_database_configured(self):
        wrangler=(ROOT/"wrangler.toml").read_text()
        self.assertIn('# database_id =',wrangler)
        self.assertNotIn('database_id = "',wrangler.replace('# database_id =',''))
if __name__=="__main__":unittest.main()

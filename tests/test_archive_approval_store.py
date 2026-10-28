import tempfile,unittest
from pathlib import Path
from tools.archive_approval_store import ApprovalStore
PACKAGE={"files":[{"name":"synthetic.mp3","sha256":"a"*64},{"name":"art.png","sha256":"b"*64},{"name":"manifest.json","sha256":"c"*64}]}
PERMS={"principal":"tester","folder":"synthetic-only","role":"writer"}
class ApprovalTests(unittest.TestCase):
    def setUp(self):
        self.t=tempfile.TemporaryDirectory();self.addCleanup(self.t.cleanup)
        self.p=Path(self.t.name)/"approvals.db"
        self.s=ApprovalStore(self.p);self.addCleanup(self.s.close)
    def test_persistent_store_survives_reopen(self):
        a=self.s.prepare("tester",PACKAGE,PERMS,now=100)
        second=ApprovalStore(self.p)
        try:self.assertEqual(second.confirm(a["request_id"],"tester",a["confirmation"],PACKAGE,PERMS,now=101)["status"],"consumed")
        finally:second.close()
    def test_expiry(self):
        a=self.s.prepare("tester",PACKAGE,PERMS,ttl=10,now=100)
        with self.assertRaises(PermissionError):self.s.confirm(a["request_id"],"tester",a["confirmation"],PACKAGE,PERMS,now=110)
    def test_replay(self):
        a=self.s.prepare("tester",PACKAGE,PERMS,now=100)
        self.s.confirm(a["request_id"],"tester",a["confirmation"],PACKAGE,PERMS,now=101)
        with self.assertRaises(PermissionError):self.s.confirm(a["request_id"],"tester",a["confirmation"],PACKAGE,PERMS,now=102)
    def test_wrong_user(self):
        a=self.s.prepare("tester",PACKAGE,PERMS,now=100)
        with self.assertRaises(PermissionError):self.s.confirm(a["request_id"],"intruder",a["confirmation"],PACKAGE,PERMS,now=101)
    def test_changed_file_hash(self):
        a=self.s.prepare("tester",PACKAGE,PERMS,now=100)
        changed={"files":[{"name":"synthetic.mp3","sha256":"d"*64}]}
        with self.assertRaises(PermissionError):self.s.confirm(a["request_id"],"tester",a["confirmation"],changed,PERMS,now=101)
    def test_changed_permissions(self):
        a=self.s.prepare("tester",PACKAGE,PERMS,now=100)
        with self.assertRaises(PermissionError):self.s.confirm(a["request_id"],"tester",a["confirmation"],PACKAGE,{**PERMS,"role":"reader"},now=101)
    def test_bad_token(self):
        a=self.s.prepare("tester",PACKAGE,PERMS,now=100)
        with self.assertRaises(PermissionError):self.s.confirm(a["request_id"],"tester","wrong",PACKAGE,PERMS,now=101)
    def test_upload_never_enabled(self):
        a=self.s.prepare("tester",PACKAGE,PERMS,now=100)
        self.assertFalse(self.s.confirm(a["request_id"],"tester",a["confirmation"],PACKAGE,PERMS,now=101)["upload_enabled"])
if __name__=="__main__":unittest.main()

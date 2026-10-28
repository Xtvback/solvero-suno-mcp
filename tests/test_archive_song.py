import hashlib,tempfile,unittest
from pathlib import Path
from tools.archive_song import ArchiveRequest,archive_song_prepare,archive_song_commit,archive_song
from tools.safe_drive_transfer import TransferFailure
URL="https://suno.com/song/be108fa8-2efa-4aea-b32d-22f60b8e78fb"
FOLDER="11xkA5Hc2tqQhYX8tu2HgGZu5rKR_Q62k"
class FakePort:
    def __init__(self):
        self.data={}
        self.uploads=0
        self.failure=False
    def list_names(self,folder):
        assert folder==FOLDER
        return [v["name"] for v in self.data.values()]
    def upload(self,folder,name,source):
        if self.failure and self.uploads==1:
            raise RuntimeError("synthetic transfer error")
        self.uploads+=1
        id="synthetic-"+str(self.uploads)
        self.data[id]={"name":name,"raw":Path(source).read_bytes()}
        return {"created":True,"id":id,"name":name,"parent_id":folder}
    def fetch_sha256(self,id):
        return hashlib.sha256(self.data[id]["raw"]).hexdigest()
    def delete(self,id):
        raise AssertionError("No implicit deletion allowed")
class Tests(unittest.TestCase):
    def setUp(self):
        tmp=tempfile.TemporaryDirectory();self.addCleanup(tmp.cleanup)
        root=Path(tmp.name)
        self.audio=root/"official.mp3";self.audio.write_bytes(b"ID3"+bytes(range(256))*2)
        self.cover=root/"cover.png";self.cover.write_bytes(b"synthetic-cover")
        self.manifest=root/"archive.json"
        self.request=ArchiveRequest(self.audio,self.cover,self.manifest,URL,"Static Riot","Synthetic Title","declared official export",True)
        self.p=FakePort();self.original=self.audio.read_bytes()
    def test_prepare_no_transfer(self):
        out=archive_song(self.request,self.p)
        self.assertEqual(out["status"],"awaiting_confirmation")
        self.assertEqual(self.p.uploads,0)
        self.assertTrue(self.manifest.exists())
        self.assertEqual(self.audio.read_bytes(),self.original)
    def test_wrong_confirmation_blocks(self):
        out=archive_song_prepare(self.request,self.p)
        with self.assertRaises(PermissionError):
            archive_song_commit(out,self.p,confirmation="yes")
        self.assertEqual(self.p.uploads,0)
    def test_full_commit_uploads_three_verified(self):
        out=archive_song_prepare(self.request,self.p)
        res=archive_song_commit(out,self.p,confirmation=out["confirmation_phrase"])
        self.assertEqual(len(res["verified_ids"]),3)
        self.assertEqual(self.p.uploads,3)
        self.assertEqual(self.audio.read_bytes(),self.original)
    def test_tampering_after_prepare_refused(self):
        out=archive_song_prepare(self.request,self.p)
        self.audio.write_bytes(self.original+b"x")
        with self.assertRaises(RuntimeError):
            archive_song_commit(out,self.p,confirmation=out["confirmation_phrase"])
        self.assertEqual(self.p.uploads,0)
    def test_duplicate_before_prepare_refused(self):
        self.p.data["existing"]={"name":"STATIC RIOT - SYNTHETIC TITLE.MP3","raw":b"real"}
        with self.assertRaises(ValueError):
            archive_song_prepare(self.request,self.p)
        self.assertEqual(self.p.uploads,0)
        self.assertIn("existing",self.p.data)
    def test_failure_tracks_created_without_unsafe_cleanup(self):
        out=archive_song_prepare(self.request,self.p)
        self.p.failure=True
        with self.assertRaises(TransferFailure) as ctx:
            archive_song_commit(out,self.p,confirmation=out["confirmation_phrase"])
        self.assertEqual(ctx.exception.created_ids,("synthetic-1",))
        self.assertEqual(self.audio.read_bytes(),self.original)
    def test_unauthorized_export_rejected(self):
        bad=ArchiveRequest(self.audio,self.cover,self.manifest,URL,"Static Riot","Synthetic Title","synthetic",False)
        with self.assertRaises(ValueError):archive_song_prepare(bad,self.p)
        self.assertFalse(self.manifest.exists())
if __name__=="__main__":unittest.main()

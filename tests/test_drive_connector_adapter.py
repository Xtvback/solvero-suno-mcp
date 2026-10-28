import hashlib,unittest
from tools.safe_drive_transfer import Component,transfer_verified,TransferFailure
from tools.drive_connector_adapter import DriveConnectorAdapter
FOLDER="fake-static-riot"
class Backend:
    def __init__(self):
        self.db={"real-music":{"name":"real.mp3","folder":FOLDER,"bytes":b"real"}}
        self.count=0;self.deleted=[];self.corrupt=None;self.fail=None;self.swap=None
    def listing(self,folder):
        return {"id":folder,"complete":True,"files":[{"name":v["name"]} for v in self.db.values() if v["folder"]==folder]}
    def upload(self,folder,name,source):
        if self.fail==name: raise RuntimeError("injected failure")
        self.count+=1;id="created-"+str(self.count)
        self.db[id]={"folder":folder,"name":name,"bytes":source}
        return {"success":True,"id":id,"parent_id":folder,"file_name":name}
    def raw(self,id):
        if self.corrupt==id:return b"corrupted"
        return self.db[id]["bytes"]
    def metadata(self,id):
        v=self.db[id]
        return {"id":id,"name":v["name"],"parent_ids":[v["folder"]]}
    def delete(self,id):
        self.deleted.append(id);del self.db[id];return True
    def port(self):
        return DriveConnectorAdapter(self.listing,self.upload,self.raw,self.metadata,self.delete)
def fixtures():
    return [Component(name,data,hashlib.sha256(data).hexdigest()) for name,data in [
        ("synthetic.mp3",b"ID3"+bytes(range(128))),
        ("synthetic.png",b"synthetic-png"),
        ("synthetic.json",b'{"test":true}')]]
class ConnectorAdapterTests(unittest.TestCase):
    def test_three_files_hash_verified(self):
        b=Backend();p=b.port();r=transfer_verified(p,FOLDER,fixtures())
        self.assertEqual(len(r["verified_ids"]),3)
        self.assertEqual(b.deleted,[])
        self.assertIn("real-music",b.db)
    def test_failure_cleanup_keeps_real_music(self):
        b=Backend();b.fail="synthetic.png";p=b.port()
        with self.assertRaises(TransferFailure):transfer_verified(p,FOLDER,fixtures(),allow_test_cleanup=True)
        self.assertEqual(b.deleted,["created-1"])
        self.assertIn("real-music",b.db)
    def test_changed_identity_prevents_delete(self):
        b=Backend();p=b.port()
        r=transfer_verified(p,FOLDER,fixtures())
        first=r["created_ids"][0]
        b.db[first]["name"]="replaced-by-other-process.mp3"
        with self.assertRaises(PermissionError):p.delete(first)
        self.assertIn(first,b.db)
    def test_never_delete_id_not_created(self):
        b=Backend();p=b.port()
        with self.assertRaises(PermissionError):p.delete("real-music")
        self.assertIn("real-music",b.db)
    def test_incomplete_listing_fails_closed(self):
        b=Backend();p=DriveConnectorAdapter(lambda folder:{"id":folder,"complete":False,"files":[]},b.upload,b.raw,b.metadata,b.delete)
        with self.assertRaises(TransferFailure):transfer_verified(p,FOLDER,fixtures())
        self.assertEqual(b.count,0)
    def test_exact_bytes_required(self):
        b=Backend();p=DriveConnectorAdapter(b.listing,b.upload,lambda id:{"file_uri":"not raw bytes"},b.metadata,b.delete)
        with self.assertRaises(TransferFailure):transfer_verified(p,FOLDER,fixtures(),allow_test_cleanup=True)
        self.assertIn("real-music",b.db)
if __name__=="__main__":unittest.main()

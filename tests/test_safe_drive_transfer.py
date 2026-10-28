import unittest
from tools.safe_drive_transfer import Component,transfer_verified,TransferFailure

FOLDER="synthetic-folder"
def parts():
    return [Component("test.mp3","audio","a"*64),Component("test.png","art","b"*64),Component("test.json","json","c"*64)]

class FakeDrive:
    def __init__(self):
        self.files={}
        self.deleted=[]
        self.fail_on=None
        self.mismatch_on=None
        self.next=1
    def list_names(self,folder_id):
        return [v["name"] for v in self.files.values()]
    def upload(self,folder_id,name,source):
        if name==self.fail_on: raise RuntimeError("injected upload failure")
        id="synthetic-"+str(self.next);self.next+=1
        self.files[id]={"name":name,"sha256":{"test.mp3":"a"*64,"test.png":"b"*64,"test.json":"c"*64}[name]}
        return {"created":True,"id":id,"parent_id":folder_id,"name":name}
    def fetch_sha256(self,id):
        f=self.files[id]
        return "f"*64 if f["name"]==self.mismatch_on else f["sha256"]
    def delete(self,id):
        self.deleted.append(id)
        return self.files.pop(id,None) is not None

class TransferTests(unittest.TestCase):
    def test_success_three_verified_and_no_cleanup(self):
        p=FakeDrive();out=transfer_verified(p,FOLDER,parts())
        self.assertEqual(out["status"],"verified")
        self.assertEqual(len(out["verified_ids"]),3)
        self.assertEqual(len(p.files),3)
        self.assertEqual(p.deleted,[])
    def test_preexisting_duplicate_no_delete(self):
        p=FakeDrive();p.files["user-original"]={"name":"test.mp3","sha256":"z"*64}
        with self.assertRaises(TransferFailure) as err:transfer_verified(p,FOLDER,parts(),allow_test_cleanup=True)
        self.assertEqual(p.deleted,[])
        self.assertIn("user-original",p.files)
        self.assertEqual(err.exception.created_ids,())
    def test_midstream_failure_cleanup_only_created(self):
        p=FakeDrive();p.files["user-original"]={"name":"other.mp3","sha256":"q"*64}
        p.fail_on="test.png"
        with self.assertRaises(TransferFailure) as err:transfer_verified(p,FOLDER,parts(),allow_test_cleanup=True)
        self.assertEqual(p.deleted,["synthetic-1"])
        self.assertIn("user-original",p.files)
        self.assertEqual(err.exception.cleanup_results,[{"id":"synthetic-1","deleted":True}])
    def test_remote_hash_mismatch_cleanup(self):
        p=FakeDrive();p.mismatch_on="test.png"
        with self.assertRaises(TransferFailure) as err:transfer_verified(p,FOLDER,parts(),allow_test_cleanup=True)
        self.assertEqual(set(p.deleted),{"synthetic-1","synthetic-2"})
        self.assertEqual(len(p.files),0)
        self.assertIn("mismatch",str(err.exception))
    def test_failure_without_cleanup_retains_created_id_for_manual_review(self):
        p=FakeDrive();p.fail_on="test.png"
        with self.assertRaises(TransferFailure) as err:transfer_verified(p,FOLDER,parts())
        self.assertEqual(err.exception.created_ids,("synthetic-1",))
        self.assertEqual(p.deleted,[])
    def test_no_two_items_same_name(self):
        p=FakeDrive();bad=[parts()[0],parts()[0],parts()[2]]
        with self.assertRaises(ValueError):transfer_verified(p,FOLDER,bad)
        self.assertEqual(p.files,{})
if __name__=="__main__": unittest.main()

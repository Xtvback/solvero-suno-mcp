"""Adapter for the connected Google Drive tool contract.

The caller injects authenticated connector operations, rather than storing
credentials. Binary reads must return exact bytes; otherwise fail closed.
No direct network access and no unsafe guessed cleanup IDs.
"""
import hashlib
from urllib.parse import quote

class DriveConnectorAdapter:
    def __init__(self, fetch_folder, upload_file, fetch_raw_bytes, fetch_metadata, delete_file):
        self._folder=fetch_folder
        self._upload=upload_file
        self._raw=fetch_raw_bytes
        self._metadata=fetch_metadata
        self._delete=delete_file
        self.created={}
    def list_names(self,folder_id):
        response=self._folder(folder_id)
        if response.get("id") != folder_id or response.get("complete") is not True:
            raise RuntimeError("Unverified or incomplete folder listing")
        return [f["name"] for f in response["files"]]
    def upload(self,folder_id,name,source):
        result=self._upload(folder_id,name,source)
        if result.get("success") is not True or not result.get("id"):
            raise RuntimeError("Upload did not confirm a new ID")
        file_id=result["id"]
        # Record the newly created ID immediately, then validate metadata.
        self.created[file_id]={"folder":folder_id,"name":name}
        if result.get("parent_id")!=folder_id or result.get("file_name")!=name:
            raise RuntimeError("Upload metadata mismatch; manual recovery required")
        return {"created":True,"id":file_id,"parent_id":folder_id,"name":name}
    def fetch_sha256(self,file_id):
        data=self._raw(file_id)
        if not isinstance(data,bytes):
            raise RuntimeError("Exact raw bytes unavailable; do not infer checksum")
        return hashlib.sha256(data).hexdigest()
    def delete(self,file_id):
        expected=self.created.get(file_id)
        if expected is None:
            raise PermissionError("Refusing deletion of unowned ID")
        metadata=self._metadata(file_id)
        if (metadata.get("id")!=file_id or
            metadata.get("name")!=expected["name"] or
            expected["folder"] not in metadata.get("parent_ids",[])):
            raise PermissionError("Identity mismatch; manual review required")
        if self._delete(file_id) is not True:
            return False
        self.created.pop(file_id,None)
        return True

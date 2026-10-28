"""SQLite-backed experimental archive approvals. No uploads or external services."""
import hashlib
import hmac
import json
import secrets
import sqlite3
import time
from pathlib import Path

class ApprovalStore:
    def __init__(self,path):
        self.path=Path(path)
        self.path.parent.mkdir(parents=True,exist_ok=True)
        self.db=sqlite3.connect(str(self.path),timeout=15,isolation_level=None)
        self.db.execute("PRAGMA busy_timeout=15000")
        self.db.execute("CREATE TABLE IF NOT EXISTS approvals (id TEXT PRIMARY KEY, principal TEXT NOT NULL, package_digest TEXT NOT NULL, permission_digest TEXT NOT NULL, expires INTEGER NOT NULL, state TEXT NOT NULL, nonce_digest TEXT NOT NULL)")
    @staticmethod
    def digest(value):
        return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
    def prepare(self,principal,package,permissions,ttl=600,now=None):
        if not isinstance(principal,str) or not principal.strip():
            raise ValueError("Authenticated principal required")
        if not isinstance(ttl,int) or not 1<=ttl<=3600:
            raise ValueError("Invalid TTL")
        if not isinstance(package,dict) or not package.get("files"):
            raise ValueError("Package hashes required")
        if not isinstance(permissions,dict) or not permissions:
            raise ValueError("Permission snapshot required")
        now=int(time.time() if now is None else now)
        token=secrets.token_urlsafe(32)
        request_id=secrets.token_urlsafe(24)
        self.db.execute("INSERT INTO approvals VALUES (?,?,?,?,?,?,?)",
            (request_id,principal,self.digest(package),self.digest(permissions),now+ttl,
             "pending",hashlib.sha256(token.encode()).hexdigest()))
        return {"request_id":request_id,"confirmation":token,"expires_at":now+ttl,"status":"pending"}
    def confirm(self,request_id,principal,token,package,permissions,now=None):
        now=int(time.time() if now is None else now)
        self.db.execute("BEGIN IMMEDIATE")
        try:
            row=self.db.execute("SELECT principal,package_digest,permission_digest,expires,state,nonce_digest FROM approvals WHERE id=?",(request_id,)).fetchone()
            if row is None: raise PermissionError("Unknown request")
            owner,pkg,perm,expires,state,nonce=row
            valid=(state=="pending" and now<expires and
                   hmac.compare_digest(owner,principal) and
                   hmac.compare_digest(pkg,self.digest(package)) and
                   hmac.compare_digest(perm,self.digest(permissions)) and
                   hmac.compare_digest(nonce,hashlib.sha256(token.encode()).hexdigest()))
            if not valid: raise PermissionError("Expired, replayed, unauthorized or changed request")
            updated=self.db.execute("UPDATE approvals SET state='consumed' WHERE id=? AND state='pending'",(request_id,))
            if updated.rowcount!=1:raise PermissionError("Replay detected")
            self.db.execute("COMMIT")
            return {"status":"consumed","upload_enabled":False,"request_id":request_id}
        except Exception:
            self.db.execute("ROLLBACK")
            raise
    def close(self):
        self.db.close()

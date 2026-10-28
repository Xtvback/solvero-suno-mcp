"""Synthetic-only experimental MCP; never imported by production server."""
import os
import tempfile
from pathlib import Path
from mcp.server.fastmcp import FastMCP
from tools.archive_approval_store import ApprovalStore
from tools.archive_song import ArchiveRequest, archive_song_prepare

experimental_app=FastMCP("Solvero Archive Experiment")
class ReadOnlySyntheticPort:
    def list_names(self,folder_id): return []

def _db_path():
    return Path(os.environ.get("SOLVERO_EXPERIMENT_APPROVAL_DB", str(Path(tempfile.gettempdir())/"solvero-experimental-approvals.sqlite3")))

def _identity():
    # Trust only an injected server-side authenticated principal.
    # Never trust a user-supplied MCP tool parameter for identity.
    principal=os.environ.get("SOLVERO_EXPERIMENT_AUTHENTICATED_PRINCIPAL","")
    if not principal.strip(): raise PermissionError("Authenticated identity unavailable")
    return principal

def _fixture(suno_url,band,title):
    with tempfile.TemporaryDirectory(prefix="solvero-synthetic-only-") as td:
        root=Path(td)
        a=root/"synthetic.mp3";c=root/"synthetic.png";m=root/"synthetic.json"
        a.write_bytes(b"ID3"+bytes(range(256))*3)
        c.write_bytes(b"synthetic-PNG-fixture")
        req=ArchiveRequest(a,c,m,suno_url,band,title,"synthetic fixture, not Suno",True)
        prepared=archive_song_prepare(req,ReadOnlySyntheticPort(),c2pa_result={"status":"not_checked","synthetic":True})
        return {"files":[{"name":x["destination_name"],"sha256":x["sha256"]} for x in prepared["package"]["files"]],
                "folder_id":prepared["package"]["drive_folder_id"],"synthetic_only":True}

def _permissions(principal):
    # Snapshot is synthetic. Real Drive permission verification remains blocked.
    return {"principal":principal,"scope":"synthetic-only","upload_allowed":False}

@experimental_app.tool()
def archive_song(stage:str,suno_url:str="",band:str="Static Riot",title:str="Synthetic Test",
                 request_id:str="",confirmation:str="")->dict:
    """Synthetic archive approval; prepare persists SQLite, commit consumes approval but never uploads."""
    principal=_identity()
    if not suno_url: raise ValueError("Canonical Suno URL required")
    package=_fixture(suno_url,band,title)
    permissions=_permissions(principal)
    store=ApprovalStore(_db_path())
    try:
        if stage=="prepare":
            result=store.prepare(principal,package,permissions,ttl=600)
            return {"status":"awaiting_confirmation","uploaded":False,"synthetic_only":True,
                    "request_id":result["request_id"],"confirmation":result["confirmation"],
                    "expires_at":result["expires_at"],"files":package["files"],
                    "persistent_state":True,"commit_enabled":False}
        if stage=="commit":
            if not request_id or not confirmation:raise PermissionError("Request ID and confirmation required")
            result=store.confirm(request_id,principal,confirmation,package,permissions)
            return {"status":"blocked","approval_status":result["status"],"uploaded":False,
                    "reason":"Real uploads disabled; synthetic approval consumed"}
        raise ValueError("stage must be prepare or commit")
    finally:store.close()

if __name__=="__main__":experimental_app.run(transport="stdio")

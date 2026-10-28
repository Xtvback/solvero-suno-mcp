"""Experimental two-phase archive_song command (not registered in production MCP).

PREPARE: read-only existing authorized MP3 and separate artwork; new JSON only.
COMMIT: explicit matching confirmation, freshly verified unchanged sources,
        and injected connector supporting exact remote SHA256.
No direct Suno access and no implicit uploads.
"""
from dataclasses import dataclass
from pathlib import Path
from tools.safe_archive_package import prepare_archive_package
from tools.safe_drive_transfer import Component, transfer_verified
from tools.c2pa_safe_archive import sha256

@dataclass(frozen=True)
class ArchiveRequest:
    audio: Path
    cover: Path
    manifest: Path
    suno_url: str
    band: str
    title: str
    declared_source: str
    approved_download: bool

def archive_song_prepare(request: ArchiveRequest, port, *, c2pa_result=None):
    if not isinstance(request,ArchiveRequest):
        raise TypeError("Expected ArchiveRequest")
    if not request.approved_download:
        raise ValueError("Authorized export confirmation required")
    # Planning uses verified folder ID for this band; folder listing is mandatory.
    from archive_rules import plan_song_archive
    plan=plan_song_archive(request.suno_url,request.band,request.title,[])
    folder=plan["drive_folder_id"]
    existing=port.list_names(folder)
    pkg=prepare_archive_package(request.audio,request.cover,request.manifest,
        request.suno_url,request.band,request.title,
        approved_download=request.approved_download,
        existing_names=existing,declared_source=request.declared_source,c2pa_result=c2pa_result)
    return {
        "status":"awaiting_confirmation",
        "package":pkg,
        "request":request,
        "confirmation_phrase":"CONFIRM ARCHIVE "+pkg["files"][0]["sha256"][:12],
    }

def archive_song_commit(prepared, port, *, confirmation: str):
    if prepared.get("status")!="awaiting_confirmation":
        raise ValueError("Package is not awaiting confirmation")
    if confirmation != prepared["confirmation_phrase"]:
        raise PermissionError("Exact explicit confirmation required")
    req=prepared["request"]
    files=prepared["package"]["files"]
    paths=[req.audio,req.cover,req.manifest]
    components=[]
    for entry,path in zip(files,paths):
        if sha256(path)!=entry["sha256"]:
            raise RuntimeError("Source changed after preparation; reprepare required")
        components.append(Component(entry["destination_name"],Path(path),entry["sha256"]))
    # No auto cleanup on error: keep only explicitly created IDs for review.
    return transfer_verified(port,prepared["package"]["drive_folder_id"],components,
                             allow_test_cleanup=False)

def archive_song(request, port, *, stage="prepare", prepared=None, confirmation=None):
    """Explicit MCP tool entrypoint suitable for experimental registration."""
    if stage=="prepare":
        return archive_song_prepare(request,port)
    if stage=="commit" and prepared is not None:
        return archive_song_commit(prepared,port,confirmation=confirmation)
    raise ValueError("Unsupported stage or missing prepared archive")

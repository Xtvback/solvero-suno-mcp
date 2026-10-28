"""Isolated experimental MCP entrypoint; NEVER mount as production server.

Only synthetic fixtures are allowed. Commit deliberately fails closed until durable
authorization, state binding, and source identity verification are implemented.
"""
import hashlib
import tempfile
from pathlib import Path
from mcp.server.fastmcp import FastMCP
from archive_rules import plan_song_archive
from tools.archive_song import ArchiveRequest, archive_song_prepare

experimental_app = FastMCP("Solvero Archive Experiment")

class ReadOnlySyntheticPort:
    def list_names(self, folder_id):
        return []

@experimental_app.tool()
def archive_song(stage: str, suno_url: str = "", band: str = "Static Riot",
                 title: str = "Synthetic Test", confirmation: str = "") -> dict:
    """Synthetic-only C2PA-safe archive preview. Uploads always disabled.

    stage: 'prepare' builds a synthetic package, 'commit' is blocked until
    durable confirmation state and real connector authorization are validated.
    """
    if stage == "commit":
        return {"status":"blocked","uploaded":False,
                "reason":"Durable state, source identity and connector authorization not yet validated"}
    if stage != "prepare":
        raise ValueError("stage must be prepare or commit")
    if not suno_url:
        raise ValueError("Canonical Suno song URL required for archive planning")
    with tempfile.TemporaryDirectory(prefix="solvero-synthetic-only-") as tmp:
        folder=Path(tmp)
        audio=folder/"synthetic.mp3"
        cover=folder/"synthetic.png"
        manifest=folder/"synthetic.json"
        audio.write_bytes(b"ID3"+bytes(range(256))*3)
        cover.write_bytes(b"synthetic-PNG-fixture")
        request=ArchiveRequest(audio,cover,manifest,suno_url,band,title,
            "synthetic fixture, not Suno",True)
        prepared=archive_song_prepare(request,ReadOnlySyntheticPort(),
            c2pa_result={"status":"not_checked","synthetic":True})
        return {"status":"awaiting_confirmation","uploaded":False,"synthetic_only":True,
            "confirmation_required":True,
            "confirmation_phrase":prepared["confirmation_phrase"],
            "files":[{"name":item["destination_name"],"sha256":item["sha256"]}
                     for item in prepared["package"]["files"]],
            "commit_enabled":False,"persistent_state":False}

if __name__ == "__main__":
    experimental_app.run(transport="stdio")

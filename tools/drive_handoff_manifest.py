"""Prepare a safe Drive handoff manifest without moving or modifying source audio.

This is a pure planning step for an *already obtained* official download.
Do not treat a Suno URL as a downloadable file.
"""
import json
from pathlib import Path
from archive_rules import plan_song_archive
from tools.authorized_audio_intake import verify_mp3

def prepare_handoff(path: Path, suno_url: str, band: str, title: str,
                    *, approved_download: bool, existing_names: list[str]) -> dict:
    audio = verify_mp3(path, approved_download)
    archive = plan_song_archive(suno_url, band, title, existing_names)
    if archive["duplicate_name_found"]:
        raise ValueError("Target filename already exists in Drive; no upload authorized.")
    return {
        "source": audio,
        "destination": {
            "folder_id": archive["drive_folder_id"],
            "file_name": archive["filename"],
            "cover_file_id": archive["cover_file_id"],
        },
        "policy": {
            "preserve_original_bytes": True,
            "embed_cover_art": False,
            "cover_stored_separately": True,
            "requires_external_authorized_file_reference": True,
            "uploaded": False,
        }
    }

"""Pure archive planning utilities; no Suno download calls or billable services."""
import re
from urllib.parse import urlparse

BANDS = {
    "static riot": {
        "artist": "Static Riot",
        "drive_folder_id": "11xkA5Hc2tqQhYX8tu2HgGZu5rKR_Q62k",
        "cover_file_id": "13ZHKgTNNVCoeB3V3mRLTrTEEV9-bREj8",
        "playlist": "Static Riot",
    },
}

def plan_song_archive(suno_url: str, band: str, title: str, existing_names: list[str] | None = None) -> dict:
    """Create a conservative upload plan. existing_names must come from a fresh Drive listing."""
    parsed = urlparse(suno_url)
    if parsed.scheme != "https" or parsed.netloc != "suno.com" or not re.fullmatch(r"/song/[a-fA-F0-9-]{36}/?", parsed.path):
        raise ValueError("A canonical https://suno.com/song/<id> link is required.")
    name = " ".join(band.split()).casefold()
    if name not in BANDS:
        raise ValueError("Unconfigured band: add verified Drive folder and cover IDs before archiving.")
    cfg = BANDS[name]
    clean_title = " ".join(title.strip().split())
    if not clean_title:
        raise ValueError("Song title is required.")
    prefix = cfg["artist"] + " - "
    if clean_title.casefold().startswith(prefix.casefold()):
        clean_title = clean_title[len(prefix):]
    if not clean_title:
        raise ValueError("Song title cannot consist only of artist name.")
    filename = f'{cfg["artist"]} - {clean_title}.mp3'
    if any(c in filename for c in '<>:"/\\|?*'):
        raise ValueError("Song title contains invalid filename characters.")
    known_names = existing_names or []
    duplicate = any(x.casefold() == filename.casefold() for x in known_names)
    return {
        "suno_url": suno_url,
        "published_name": f'{cfg["artist"]} - {clean_title}',
        "filename": filename,
        "playlist": cfg["playlist"],
        "drive_folder_id": cfg["drive_folder_id"],
        "cover_file_id": cfg["cover_file_id"],
        "duplicate_name_found": duplicate,
        "download_allowed": not duplicate,
        "archive_status": "already-present-by-name" if duplicate else "not-downloaded",
        "note": "This plan does not download music, spend Suno credits, or upload files. Verify exact Drive content before downloading.",
    }

"""Read-only planning for an MP3 already in a user-controlled Google Drive inbox.

No Google SDK, Suno call, source download, copy, upload, or delete is performed.
Actual transfer uses the connected Google Drive tools after user authorization.
"""
from archive_rules import plan_song_archive

def plan_drive_inbox_item(item: dict, suno_url: str, band: str, title: str,
                          *, official_export_confirmed: bool,
                          target_existing_names: list[str]) -> dict:
    if not official_export_confirmed:
        raise ValueError("The source must have been exported through an authorized Suno Download.")
    if item.get("mime_type") != "audio/mpeg" or not item.get("id") or not str(item.get("title", "")).lower().endswith(".mp3"):
        raise ValueError("Source must be an identified Google Drive MP3 file.")
    if not item.get("parent_ids"):
        raise ValueError("Source folder identity is required.")
    plan = plan_song_archive(suno_url, band, title, target_existing_names)
    if plan["duplicate_name_found"]:
        raise ValueError("Destination filename already exists.")
    if plan["drive_folder_id"] in item["parent_ids"]:
        raise ValueError("Source is already in destination folder.")
    return {
        "source_drive_id": item["id"],
        "source_folder_ids": item["parent_ids"],
        "destination_folder_id": plan["drive_folder_id"],
        "destination_filename": plan["filename"],
        "artwork_file_id": plan["cover_file_id"],
        "requires_raw_file_sha256_before_and_after_upload": True,
        "preserve_source": True,
        "embed_artwork": False,
        "ready_for_connector_handoff": True,
        "transferred": False
    }

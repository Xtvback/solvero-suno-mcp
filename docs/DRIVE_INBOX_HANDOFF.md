# Existing authorized Suno MP3 -> Drive inbox handoff

The Suno official Download menu is the documented route to export audio. The Suno song URL itself is not a download file URI.

If a file **has already been exported** and exists in a user-controlled Google Drive folder (or is supplied as an attachment), an authorized operator can:

1. Confirm the source MP3 is an official download and inspect its folder and MIME type.
2. List the destination music folder and reject name duplicates; do not overwrite existing songs.
3. Run drive_inbox_adapter.py planning logic on source metadata.
4. Fetch source raw binary with the Drive connector (`download_raw_file=true, include_base64=false`).
5. Compute source SHA-256 from bytes if accessible; if not, do not claim end-to-end checksum validation.
6. Upload the returned connector file reference into the approved destination, with the new filename.
7. Fetch back the raw destination and verify SHA-256 when accessible.
8. Preserve the source and separate album artwork (no ID3 modifications).
9. Never delete original source automatically.

No automatic Suno API export is available through this mechanism. Do not store session cookies, invoke unofficial download endpoints, or spend downloads for testing.

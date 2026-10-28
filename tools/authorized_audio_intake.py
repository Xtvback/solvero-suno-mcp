"""Validate audio files already exported via Suno's approved Download action.

No Suno account, network calls, cookies, downloads or external APIs.
This module only checks inputs; it never erases provenance metadata.
"""
import argparse
import hashlib
import json
from pathlib import Path

MP3_MAGIC = (b"ID3",)

def verify_mp3(path: Path, approved_download: bool) -> dict:
    if not approved_download:
        raise ValueError("Explicit confirmation of an authorized Suno download is required.")
    path = path.resolve(strict=True)
    if not path.is_file() or path.suffix.lower() != ".mp3":
        raise ValueError("Expected an existing .mp3 file.")
    size = path.stat().st_size
    if size < 128:
        raise ValueError("File is too small for a usable MP3.")
    with path.open("rb") as f:
        header = f.read(3)
    if header != b"ID3" and not (header[0] == 0xFF and (header[1] & 0xE0) == 0xE0):
        raise ValueError("MP3 frame or ID3 signature not found.")
    sha = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            sha.update(block)
    return {"file_name": path.name, "size": size, "sha256": sha.hexdigest(), "source_confirmed": "approved-download", "modified": False}

def main():
    p = argparse.ArgumentParser()
    p.add_argument("path", type=Path)
    p.add_argument("--approved-download", action="store_true", help="Confirm obtained using Suno's official download control")
    args = p.parse_args()
    print(json.dumps(verify_mp3(args.path, args.approved_download), indent=2))

if __name__ == "__main__":
    main()

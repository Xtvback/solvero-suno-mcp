"""Free local Suno download helper. Uses the official website, not an unofficial API."""
import argparse
import re
from pathlib import Path

from mutagen.id3 import APIC, ID3, ID3NoHeaderError, TALB, TPE1, TIT2
from playwright.sync_api import sync_playwright

def safe_filename(value: str) -> str:
    return re.sub(r'[<>:"/\\|?*\x00-\x1f]', '_', value).strip(' .')[:180]

def add_tags(mp3: Path, cover: Path, artist: str, song_title: str) -> None:
    try:
        tags = ID3(mp3)
    except ID3NoHeaderError:
        tags = ID3()
    tags.delall("APIC")
    tags.setall("TIT2", [TIT2(encoding=3, text=song_title)])
    tags.setall("TPE1", [TPE1(encoding=3, text=artist)])
    tags.setall("TALB", [TALB(encoding=3, text=artist)])
    suffix = cover.suffix.lower()
    mime = "image/png" if suffix == ".png" else "image/jpeg"
    tags.add(APIC(encoding=3, mime=mime, type=3, desc="Cover", data=cover.read_bytes()))
    tags.save(mp3, v2_version=3)

def main() -> None:
    p = argparse.ArgumentParser(description="Download your own Suno song through the Suno UI and embed band artwork.")
    p.add_argument("--url", required=True, help="Owned song URL at https://suno.com/song/...")
    p.add_argument("--artist", required=True, help="Band / sub-band name")
    p.add_argument("--title", required=True, help="Song title without band prefix")
    p.add_argument("--cover", required=True, type=Path, help="Local PNG or JPG cover artwork")
    p.add_argument("--output-dir", required=True, type=Path, help="Local destination folder; can be inside Google Drive for desktop")
    args = p.parse_args()
    if not re.fullmatch(r"https://suno\.com/song/[a-fA-F0-9-]{36}/?", args.url):
        p.error("Only canonical Suno song URLs are accepted.")
    cover = args.cover.expanduser().resolve()
    if not cover.is_file() or cover.suffix.lower() not in (".png", ".jpg", ".jpeg"):
        p.error("Cover must be an existing local PNG or JPEG file.")
    destination = args.output_dir.expanduser().resolve()
    destination.mkdir(parents=True, exist_ok=True)
    filename = safe_filename(f"{args.artist} - {args.title}") + ".mp3"
    final_path = destination / filename
    if final_path.exists():
        p.error(f"Destination already exists: {final_path}; refusing to overwrite.")
    with sync_playwright() as pw:
        profile = (Path.home() / ".solvero-suno-browser").resolve()
        browser = pw.chromium.launch_persistent_context(
            user_data_dir=str(profile), headless=False, accept_downloads=True
        )
        page = browser.pages[0] if browser.pages else browser.new_page()
        page.goto(args.url, wait_until="domcontentloaded")
        print("Sign in in this browser if needed. Use Suno's own More > Download > MP3 controls.")
        print("Only download songs you own or are permitted to download.")
        try:
            with page.expect_download(timeout=300000) as event:
                print("Waiting up to 5 minutes for the MP3 download you initiate in the page...")
            download = event.value
            if not download.suggested_filename.lower().endswith(".mp3"):
                raise ValueError("The Suno download was not an MP3; choose MP3 in the Suno menu.")
            download.save_as(str(final_path))
        finally:
            browser.close()
    try:
        add_tags(final_path, cover, args.artist, args.title)
    except Exception:
        final_path.unlink(missing_ok=True)
        raise
    print(f"READY: {final_path}")
    print("For automatic Drive sync, choose a destination inside a locally synced Google Drive folder.")

if __name__ == "__main__":
    main()

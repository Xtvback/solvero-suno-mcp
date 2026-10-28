"""Read-only provenance manifest generation. Original MP3 is never edited."""
import hashlib
import json
from pathlib import Path

def sha256(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def build_manifest(audio, artist, title, declared_source, cover=None, c2pa=None):
    audio = Path(audio).resolve(strict=True)
    if not audio.is_file() or audio.suffix.lower() != ".mp3":
        raise ValueError("Existing MP3 required")
    if not all(isinstance(x, str) and x.strip() for x in (artist,title,declared_source)):
        raise ValueError("Artist, title and declared source are required")
    before = sha256(audio)
    cover_info = None
    if cover is not None:
        cover = Path(cover).resolve(strict=True)
        if not cover.is_file() or cover.suffix.lower() not in (".jpg",".jpeg",".png"):
            raise ValueError("Separate PNG/JPEG cover required")
        cover_info = {"name":cover.name,"sha256":sha256(cover),"bytes":cover.stat().st_size}
    if c2pa is not None and not isinstance(c2pa,dict):
        raise ValueError("C2PA result must be a dictionary")
    result = {
        "schema_version":"solvero-c2pa-safe-1",
        "artist":artist.strip(),"title":title.strip(),
        "source":{"declared":declared_source.strip(),"verified":False},
        "original_audio":{"name":audio.name,"sha256":before,"bytes":audio.stat().st_size,"modified":False},
        "artwork_separate":cover_info,
        "c2pa_validation":c2pa if c2pa is not None else {"status":"not_checked"},
        "policy":{"preserve_original":True,"allow_id3_writes":False,"allow_apic_writes":False}
    }
    if sha256(audio) != before:
        raise RuntimeError("Audio changed during manifest generation")
    return result

def write_manifest(manifest, destination, audio):
    destination = Path(destination)
    audio = Path(audio).resolve(strict=True)
    if destination.resolve() == audio or destination.suffix.lower() != ".json":
        raise ValueError("Manifest must be a distinct JSON file")
    if destination.exists():
        raise FileExistsError("Refusing to replace existing manifest")
    before = sha256(audio)
    destination.parent.mkdir(parents=True,exist_ok=True)
    with destination.open("x",encoding="utf-8") as out:
        json.dump(manifest,out,indent=2,ensure_ascii=False,sort_keys=True)
    if sha256(audio) != before:
        raise RuntimeError("Audio modified unexpectedly")
    return destination

def modify_protected_id3(*args,**kwargs):
    raise PermissionError("ID3/APIC writes are forbidden on a protected original")

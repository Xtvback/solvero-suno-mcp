"""Prepare a three-file archive package without writing to MP3/cover inputs."""
from pathlib import Path
from tools.c2pa_safe_archive import build_manifest, write_manifest, sha256
from tools.drive_handoff_manifest import prepare_handoff

def prepare_archive_package(audio, cover, manifest_path, suno_url, band, title, *,
                            approved_download, existing_names, declared_source, c2pa_result=None):
    audio,cover,manifest_path=map(Path,(audio,cover,manifest_path))
    existing_names=list(existing_names)
    plan=prepare_handoff(audio,suno_url,band,title,
        approved_download=approved_download,existing_names=existing_names)
    filename=plan["destination"]["file_name"]
    # All 3 proposed destinations must be absent, case-insensitively.
    cover_name=filename[:-4]+cover.suffix.lower()
    json_name=filename[:-4]+".json"
    targets=[filename,cover_name,json_name]
    if len({n.casefold() for n in targets})!=3:
        raise ValueError("Destination name collision")
    if any(n.casefold() in {x.casefold() for x in existing_names} for n in targets):
        raise FileExistsError("Destination already contains archive component; no uploads authorized")
    if manifest_path.exists():
        raise FileExistsError("Manifest exists; refusing overwrite")
    hashes_before={"audio":sha256(audio),"cover":sha256(cover)}
    manifest=build_manifest(audio,band,title,declared_source,cover=cover,c2pa=c2pa_result)
    manifest["destination"]={"folder_id":plan["destination"]["folder_id"],
                             "audio":filename,"cover":cover_name,"manifest":json_name}
    # Write only new JSON, never mutate source MP3 or artwork.
    write_manifest(manifest,manifest_path,audio)
    hashes_after={"audio":sha256(audio),"cover":sha256(cover)}
    if hashes_before!=hashes_after:
        raise RuntimeError("Source bytes changed during package creation")
    return {"archive":manifest,"files":[
        {"kind":"original_mp3","source_name":audio.name,"destination_name":filename,"sha256":hashes_after["audio"]},
        {"kind":"separate_cover","source_name":cover.name,"destination_name":cover_name,"sha256":hashes_after["cover"]},
        {"kind":"json_manifest","source_name":manifest_path.name,"destination_name":json_name,"sha256":sha256(manifest_path)}],
        "drive_folder_id":plan["destination"]["folder_id"],
        "preflight":{"fresh_drive_listing_required":True,"no_overwrite":True,"atomic_upload":False,
                     "verify_remote_sha256_each_file":True,"upload_performed":False}}

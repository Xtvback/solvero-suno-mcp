"""Pure, offline Solvero music-production planning. No provider calls or writes."""
from __future__ import annotations

import re
import wave
from datetime import date
from pathlib import Path

AUDIO_EXTENSIONS = {".wav", ".flac", ".aiff", ".aif", ".mp3", ".m4a", ".wma"}
SECTION_LINE = re.compile(r"^\s*(?:\[|\()?\s*(verse|chorus|bridge|intro|outro|pre[- ]?chorus|hook)[^\n]*$", re.I)
JPEG_SOF = {0xC0,0xC1,0xC2,0xC3,0xC5,0xC6,0xC7,0xC9,0xCA,0xCB,0xCD,0xCE,0xCF}


def _required(value: str, field: str, maximum: int = 500) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} is required.")
    result = value.strip()
    if len(result) > maximum:
        raise ValueError(f"{field} is too long.")
    return result


def _optional_date(value: str) -> str:
    if not value:
        return ""
    try:
        return date.fromisoformat(value).isoformat()
    except ValueError as exc:
        raise ValueError("release_date must use YYYY-MM-DD.") from exc


def plain_distribution_lyrics(lyrics: str) -> str:
    """Remove Suno section labels while preserving every performed lyric line."""
    lines = []
    blank = False
    for raw in lyrics.replace("\r\n", "\n").replace("\r", "\n").split("\n"):
        line = raw.strip()
        if SECTION_LINE.match(line):
            if lines and not blank:
                lines.append("")
                blank = True
            continue
        if not line:
            if lines and not blank:
                lines.append("")
                blank = True
            continue
        lines.append(line)
        blank = False
    while lines and not lines[-1]:
        lines.pop()
    return "\n".join(lines)


def _title_warnings(title: str) -> list[str]:
    lowered = title.casefold()
    warnings = []
    if "http://" in lowered or "https://" in lowered or "www." in lowered:
        warnings.append("Remove URLs from the track title.")
    if re.search(r"\b(19|20)\d{2}\b", title):
        warnings.append("Review the year/date in the title; stores may reject it as extra information.")
    if re.search(r"\b\d{2,3}\s*bpm\b", lowered):
        warnings.append("Remove BPM information from the track title.")
    return warnings


def _jpeg_dimensions(path: Path) -> tuple[int,int,int]:
    data=path.read_bytes()
    if len(data)<4 or data[:2]!=b"\xff\xd8":
        raise ValueError("Cover is not a valid JPEG file.")
    pos=2
    while pos+4<=len(data):
        if data[pos]!=0xFF:
            pos+=1;continue
        while pos<len(data) and data[pos]==0xFF: pos+=1
        if pos>=len(data): break
        marker=data[pos];pos+=1
        if marker in {0xD8,0xD9}: continue
        if pos+2>len(data): break
        length=int.from_bytes(data[pos:pos+2],"big")
        if length<2 or pos+length>len(data): break
        if marker in JPEG_SOF:
            if length<8: break
            height=int.from_bytes(data[pos+3:pos+5],"big")
            width=int.from_bytes(data[pos+5:pos+7],"big")
            components=data[pos+7]
            return width,height,components
        pos+=length
    raise ValueError("Cover JPEG dimensions could not be read.")


def _inspect_assets(audio: Path,cover: Path) -> tuple[list[str],list[str],dict]:
    errors=[];warnings=[];details={}
    if not audio.is_file():
        errors.append("Audio file does not exist locally.")
    elif audio.suffix.casefold() not in AUDIO_EXTENSIONS:
        errors.append("Unsupported audio extension for the DistroKid handoff.")
    elif audio.suffix.casefold()==".wav":
        try:
            with wave.open(str(audio),"rb") as wav:
                details["audio"]={"format":"WAV","channels":wav.getnchannels(),
                    "sample_rate":wav.getframerate(),"bit_depth":wav.getsampwidth()*8,
                    "frames":wav.getnframes()}
            if details["audio"]["sample_rate"]<44100:
                warnings.append("Audio sample rate is below the typical 44.1 kHz upload rate.")
            if details["audio"]["bit_depth"]<16:
                warnings.append("Audio bit depth is below the typical 16-bit upload depth.")
        except (wave.Error,EOFError):
            errors.append("Audio has a .wav extension but is not a readable WAV file.")
    if not cover.is_file():
        errors.append("Cover file does not exist locally.")
    elif cover.suffix.casefold() not in {".jpg", ".jpeg"}:
        errors.append("Cover should be a JPEG file.")
    else:
        try:
            width,height,components=_jpeg_dimensions(cover)
            details["cover"]={"format":"JPEG","width":width,"height":height,"components":components}
            if width<1000 or height<1000:
                errors.append("Cover must be at least 1000x1000 pixels.")
            if width!=height:
                warnings.append("Cover should be perfectly square.")
            if width!=3000 or height!=3000:
                warnings.append("DistroKid recommends 3000x3000 pixels.")
            if components==4:
                warnings.append("Four-component JPEG may be CMYK; confirm RGB before handoff.")
        except ValueError as exc:
            errors.append(str(exc))
    return errors,warnings,details


def prepare_music_project(
    *, title: str, artist: str, concept: str, style: str,
    lyrics: str = "", language: str = "pt-PT", cover_direction: str = "",
    genre: str = "", release_date: str = "", explicit: bool = False,
    instrumental: bool = False,
) -> dict:
    title = _required(title, "title", 200)
    artist = _required(artist, "artist", 200)
    concept = _required(concept, "concept", 2000)
    style = _required(style, "style", 1000)
    language = _required(language, "language", 32)
    release_date = _optional_date(release_date)
    if instrumental and lyrics.strip():
        raise ValueError("An instrumental project cannot include lyrics.")
    suno_lyrics = lyrics.strip()
    distribution_lyrics = "" if instrumental else plain_distribution_lyrics(suno_lyrics)
    cover_subject = cover_direction.strip() or concept
    cover_prompt = (
        f"Original square album artwork for '{title}' by {artist}. {cover_subject}. "
        "No typography, no logos, no URLs, no QR codes, no streaming-service marks, "
        "no stock-photo look. Strong focal composition, production-ready detail."
    )
    handoff = {
        "title": title,
        "artist": artist,
        "genre": genre.strip(),
        "lyrics": distribution_lyrics,
        "release_date": release_date,
        "audio_path": None,
        "cover_path": None,
    }
    return {
        "schema_version": 1,
        "project": {"title": title, "artist": artist, "concept": concept, "status": "creative_ready"},
        "suno_generation": {
            "status": "approval_required",
            "submitted": False,
            "request": {"title": title, "style": style, "lyrics": suno_lyrics,
                        "language": language, "instrumental": instrumental},
            "approval_gate": "Confirm provider access and any cost before generation.",
        },
        "cover_generation": {
            "status": "approval_required",
            "generated": False,
            "prompt": cover_prompt,
            "delivery": {"format": "JPEG", "width": 3000, "height": 3000,
                         "color_space": "RGB", "minimum_width": 1000, "minimum_height": 1000},
        },
        "distribution": {
            "status": "waiting_for_audio_and_cover",
            "explicit": bool(explicit),
            "instrumental": bool(instrumental),
            "plain_lyrics": distribution_lyrics,
            "distrokid_prepare_release_args": handoff,
            "final_submission": "manual_user_click",
        },
        "warnings": _title_warnings(title),
        "safety": {"provider_calls": False, "uploads": False, "publishing": False},
    }


def prepare_release_handoff(
    *, title: str, artist: str, audio_path: str, cover_path: str,
    genre: str = "", lyrics: str = "", release_date: str = "",
) -> dict:
    title = _required(title, "title", 200)
    artist = _required(artist, "artist", 200)
    release_date = _optional_date(release_date)
    audio = Path(_required(audio_path, "audio_path", 4096)).expanduser().resolve()
    cover = Path(_required(cover_path, "cover_path", 4096)).expanduser().resolve()
    errors = []
    warnings = _title_warnings(title)
    asset_errors,asset_warnings,asset_details=_inspect_assets(audio,cover)
    errors.extend(asset_errors);warnings.extend(asset_warnings)
    args = {"title": title, "artist": artist, "audio_path": str(audio),
            "cover_path": str(cover), "genre": genre.strip(),
            "lyrics": plain_distribution_lyrics(lyrics), "release_date": release_date}
    return {
        "status": "ready_for_distrokid_preparation" if not errors else "incomplete",
        "errors": errors,
        "warnings": warnings,
        "asset_details": asset_details,
        "distrokid_prepare_release_args": args,
        "next_action": "Call Solvero DistroKid MCP prepare_release, review the result, then let the user click submit.",
        "final_submission": "manual_user_click",
        "uploads": False,
        "publishing": False,
    }

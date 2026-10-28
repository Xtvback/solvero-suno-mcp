"""Solvero Suno MCP: local catalogue and production briefs; no unofficial Suno API calls."""
import json
import os
from pathlib import Path
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from production_workflow import prepare_music_project as build_music_project
from production_workflow import prepare_release_handoff as build_release_handoff

PUBLIC_HOST = os.environ.get("SOLVERO_PUBLIC_HOST", "solvero-suno-mcp.onrender.com")
app = FastMCP(
    "Solvero Suno",
    transport_security=TransportSecuritySettings(
        enable_dns_rebinding_protection=True,
        allowed_hosts=[PUBLIC_HOST, f"{PUBLIC_HOST}:*", "localhost:*", "127.0.0.1:*"],
        allowed_origins=["https://chatgpt.com"],
    ),
)
DATA_DIR = Path(os.environ.get("SOLVERO_DATA_DIR", "./data")).resolve()
CATALOGUE = DATA_DIR / "songs.json"

def load_songs() -> list[dict]:
    if not CATALOGUE.exists():
        return []
    data = json.loads(CATALOGUE.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("The catalogue must contain a JSON list.")
    return data

@app.tool()
def list_songs(artist: str = "") -> list[dict]:
    """List local song records, optionally filtered by artist."""
    songs = load_songs()
    return [song for song in songs if str(song.get("artist", "")).casefold() == artist.casefold()] if artist else songs

@app.tool()
def prepare_song_brief(title: str, artist: str, concept: str, style: str, language: str = "pt-PT") -> dict:
    """Prepare a Suno-ready creative brief without submitting it to Suno."""
    if not all(v.strip() for v in (title, artist, concept, style)):
        raise ValueError("Title, artist, concept and style are required.")
    return {"title": title.strip(), "artist": artist.strip(), "concept": concept.strip(),
            "style_prompt": style.strip(), "language": language.strip(),
            "status": "draft", "sent_to_suno": False}

@app.tool()
def prepare_music_project(title: str, artist: str, concept: str, style: str,
                          lyrics: str = "", language: str = "pt-PT",
                          cover_direction: str = "", genre: str = "",
                          release_date: str = "", explicit: bool = False,
                          instrumental: bool = False) -> dict:
    """Prepare Suno generation, cover and DistroKid handoff; makes no provider calls."""
    return build_music_project(title=title, artist=artist, concept=concept, style=style,
                               lyrics=lyrics, language=language, cover_direction=cover_direction,
                               genre=genre, release_date=release_date, explicit=explicit,
                               instrumental=instrumental)

@app.tool()
def prepare_release_handoff(title: str, artist: str, audio_path: str, cover_path: str,
                            genre: str = "", lyrics: str = "",
                            release_date: str = "") -> dict:
    """Validate local assets and prepare arguments for Solvero DistroKid MCP; never uploads."""
    return build_release_handoff(title=title, artist=artist, audio_path=audio_path,
                                 cover_path=cover_path, genre=genre, lyrics=lyrics,
                                 release_date=release_date)

@app.tool()
def save_song_record(title: str, artist: str, style: str, lyrics: str = "", suno_url: str = "") -> dict:
    """Save a local song record. No audio download or Suno account access."""
    if not title.strip() or not artist.strip():
        raise ValueError("Title and artist are required.")
    songs = load_songs()
    record = {"title": title.strip(), "artist": artist.strip(), "style": style.strip(),
              "lyrics": lyrics, "suno_url": suno_url, "status": "draft"}
    songs.append(record)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    tmp = CATALOGUE.with_suffix(".tmp")
    tmp.write_text(json.dumps(songs, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(CATALOGUE)
    return record

if __name__ == "__main__":
    app.run(transport="stdio")

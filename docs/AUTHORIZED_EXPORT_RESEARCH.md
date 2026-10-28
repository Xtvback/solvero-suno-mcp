# Suno authorized export research — 2026-10-28

## Verified official channels
- Suno Help: Library/Workspace > More actions > Download > MP3, WAV and other available formats: https://help.suno.com/en/articles/2409921 and https://help.suno.com/en/articles/13926081
- Multiple tracks: Suno's Download All gives a ZIP via the web UI; download quotas still apply.
- Re-download of the same song and different formats of the same song do not consume another download: https://help.suno.com/en/articles/13926209
- API platform login at https://platform.suno.com/ advertises generation API, but its public login page does **not** document an export endpoint for existing personal songs, public account eligibility, or free pricing.
- Free Suno C2PA detection API, https://suno.com/suno-credentials , verifies provenance. It is **not** an audio download/export API.
- Current Suno Terms https://suno.com/terms/ bar unauthorized extraction/scraping and obtaining music outside the intended download channel, and disallow stripping provenance metadata to conceal origin.

## Implementation
- tools/authorized_audio_intake.py: validates explicit approved-download confirmation, checks that the file exists and resembles an MP3, hashes the input and leaves bytes unchanged.
- tests/test_authorized_audio_intake.py: synthetic-only tests for refusal, acceptance, immutability and rejection. This does **not** demonstrate that the mock bytes represent playable audio.
- A real end-to-end archive would require an official export to supply a real file reference to ChatGPT; after that, the existing Google Drive connector can upload and read back the file. No new secrets/cookies are added.
- Cover embedding should avoid stripping or invalidating Suno C2PA/provenance; validate preservation after edit before any automated release.

## Status and conditions
No authenticated Suno API export has been executed, no downloads consumed, no paid service used, and live MCP remains unchanged. Do not claim full automatic Suno-to-Drive integration until a supported file handoff exists.

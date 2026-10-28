# Solvero chat production flow

## Goal

Let the user direct a release in natural language while ChatGPT coordinates
creative work and the two Solvero MCPs. The system prepares everything; the
user retains the final DistroKid submit click.

## Conversation sequence

1. ChatGPT develops the concept, candidate title, lyrics and music direction.
2. `Solvero Suno MCP.prepare_music_project` freezes the approved creative plan.
3. The Suno generation request remains `approval_required` until official API
   access and any cost are confirmed.
4. ChatGPT creates the cover from the returned cover brief after approval.
5. The chosen audio and cover are checked by `prepare_release_handoff`.
6. Its `distrokid_prepare_release_args` are passed to
   `Solvero DistroKid MCP.prepare_release`.
7. The user reviews the release and performs the final submit click.

## Safety boundary

- `prepare_music_project` and `prepare_release_handoff` are pure planning and
  validation tools. They make no provider calls and write no files.
- No generation job, upload, publication or paid operation occurs implicitly.
- The handoff validates local file existence, supported audio extensions, WAV
  sample rate/bit depth, JPEG readability and artwork dimensions.
- Suno section labels such as `[Verse]` and `[Chorus]` are removed from the
  DistroKid plain-lyrics copy, without removing performed lyric lines.
- A real Suno call requires a separate approval after cost/access preflight.

## DistroKid baseline used

Official DistroKid guidance says artwork must be JPEG, at least 1000x1000,
ideally square 3000x3000 and RGB. It disallows URLs, QR codes, service/social
logos and other listed elements. Typical audio upload is 16-bit, 44.1 kHz WAV,
although other documented formats are accepted.

Sources checked on 2026-10-28:

- https://support.distrokid.com/hc/en-us/articles/360013534334-What-Are-the-Requirements-for-Album-Artwork
- https://support.distrokid.com/hc/en-us/categories/360001857214-Uploading
- https://support.distrokid.com/hc/en-us/articles/360033900034-Release-and-Track-Title-Formatting-Issues
- https://support.distrokid.com/hc/en-us/articles/360050506673-Correcting-Rejected-Lyrics

These checks prepare a handoff; they do not claim to reproduce every current
DistroKid validation rule.

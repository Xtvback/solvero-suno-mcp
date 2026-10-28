# Free local Suno → MP3 with band cover → Google Drive

This is an **experimental local prototype**, separate from the live MCP and its Render deployment. It makes **no unofficial Suno API calls**, uses the normal Suno website, and spends no credits on its own. Actual Suno download limits still apply.

## One-time setup (Windows)

Install Python 3.11+ and optionally Google Drive for desktop, using the free available software and your existing Google storage quota.

```powershell
pip install -r requirements-local.txt
python -m playwright install chromium
```

Save the band's official cover from Google Drive to a local file, for example `C:\Solvero\StaticRiot.png`. If Google Drive for desktop is installed and synchronizing, identify the actual synchronized local `Static Riot\Músicas_` path.

## Download and tag a song

```powershell
python tools/free_suno_download.py --url "https://suno.com/song/be108fa8-2efa-4aea-b32d-22f60b8e78fb" --artist "Static Riot" --title "Nobody Gets Close to You" --cover "C:\Solvero\StaticRiot.png" --output-dir "G:\O meu disco\Solvero\Static Riot\Músicas_"
```

**Adjust the paths for your machine.** The folder ID for the verified Static Riot music folder is `11xkA5Hc2tqQhYX8tu2HgGZu5rKR_Q62k`; the local path above is only an illustration, not a verified path.

The script opens a dedicated browser profile under your own user account. Sign in to Suno there if necessary. On the song page, choose the website's **More → Download → MP3** option. The script waits for that download, saves it under `Static Riot - Nobody Gets Close to You.mp3`, embeds image artwork and ID3 title/artist/album tags, and leaves the file in your chosen local destination. If that destination is a synchronized Google Drive folder, Drive for desktop uploads it automatically using your existing account.

It does **not** rename or publish songs or edit playlists; those were managed separately through the Suno website. It does not upload directly through the Google Drive API, and it does not share browser cookies with the hosted MCP.

## Boundaries

- The download button must be clicked by the user in the local browser; full hands-free capture is not yet implemented.
- The song must be yours or authorized for download. Do not bypass Suno restrictions.
- Does not guarantee download availability; downloads can be limited by subscription.
- No third-party paid transfer service is required. Google Drive storage beyond the quota is not included.
- Do not commit browser profiles, tokens, audio files, or personal credentials to GitHub.
- **Not yet end-to-end tested** against a real Suno download; validate one song before using this for a music library.

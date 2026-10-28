# Suno catalogue access feasibility — 2026-10-28

## Decision: NO verified private-library API access

The official Suno Platform login page advertises an API to **generate** music:
https://platform.suno.com/ . This does **not** demonstrate an API to
**list existing songs** from a consumer Suno account. The publicly accessible
official help articles describe the consumer Library but do not document
a supported library-listing API:

- https://help.suno.com/en/articles/3726849
- https://help.suno.com/en/articles/2551361

The official public C2PA detector API at
https://suno.com/suno-credentials identifies provenance of a supplied
audio file or direct URL. It is **not** a private library enumeration API.
Do not treat it as authentication or catalogue access.

## Gated architecture decision

DO NOT implement unsupported Suno scraping, browser cookie/session extraction,
reverse-engineered private endpoints or third-party paid API as a replacement
for verified authorization. DO NOT ask for Suno cookies or passwords.

First usable milestone can instead be **read-only catalogue from explicit,
user-provided data**: a music manifest with title, artist, Suno public/share
URL, date, description, and status, without private MP3 or tokens. Its
origin is an exported/curated manifest, **not live Suno synchronization**.
If this route is chosen, add a read-only `list_catalogue` MCP tool with
schema validation and safe provenance labels. Avoid exposing unpublished
works publicly without the user's approval.

Future live Suno integration requires:
1. Verified provider-approved API available to this account;
2. Authorized library-list endpoint and permissions/quotas;
3. Provider terms and privacy review;
4. Tested least-privilege authentication using synthetic fixtures;
5. Explicit permission for deployment and the live connection.

## ChatGPT MCP status

User confirmed the ChatGPT UI displays 'Add custom MCP server'.
That confirms UI availability, not this server's compatibility or
a public URL. Remote HTTPS and OAuth are NOT deployed or enabled.
See CHATGPT-CONNECTION.md for connection blockers.

## Prohibition / audit

No real credentials, Suno API calls, Google OAuth, private MP3, paid
services, production mutation, tokens or deployment were used to create
this document.

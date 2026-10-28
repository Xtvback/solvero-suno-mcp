# Suno catalogue access feasibility — 2026-10-28

## Decision: NO verified private-library API access

The official Suno Platform login page advertises an API to **generate** music:
https://platform.suno.com/ . This does **not** demonstrate an API to
**list existing songs** from a consumer Suno account. The publicly accessible
official help articles describe the consumer Library but do not document
a supported library-listing API:

- https://help.suno.com/en/articles/3726849
- https://help.suno.com/en/articles/2551361

The official evidence supports this distinction:

| Capability | Official evidence | Result |
|---|---|---|
| Generate new music through an API | Suno Platform says “Make music with the Suno API” and describes generating songs, covers and mashups | Available as a generation product; account access, pricing and exact endpoints were not tested |
| Browse songs already created | Suno Help describes the Library UI, filters and ordering | Available in Suno's own UI |
| List the signed-in consumer's existing Library through an API | No official public endpoint, scope or OAuth flow found in the sources above | **Not verified / do not implement** |

This is a bounded finding about publicly documented, authorized integration.
It is not proof that Suno has no private or partner API. A provider-approved
library endpoint and authorization grant would change the decision.

Suno's current Terms of Service expressly prohibit obtaining content by means
not intentionally made available and prohibit robots, scraping and similar
data extraction. Official source: https://suno.com/terms . Therefore browser
cookie extraction, private-endpoint reverse engineering and scraping are not
acceptable fallbacks for this project.

The official public C2PA detector API at
https://suno.com/suno-credentials identifies provenance of a supplied
audio file or direct URL. It is **not** a private library enumeration API.
Do not treat it as authentication or catalogue access.

## Gated architecture decision

DO NOT implement unsupported Suno scraping, browser cookie/session extraction,
reverse-engineered private endpoints or third-party paid API as a replacement
for verified authorization. DO NOT ask for Suno cookies or passwords.

First usable milestone is instead **read-only catalogue from explicit,
user-provided data**: a music manifest with title, creator, Suno public/share
URL, date, description, visibility and status, without private MP3 or tokens.
Its origin is a curated manifest, **not live Suno synchronization**.

Implemented locally on this branch:

- read-only MCP tool `list_catalogue`, with filtering and bounded pagination;
- every record is labelled `source: user_manifest`;
- a non-empty manifest is bound to one authenticated `owner_user_id`;
- only HTTPS `suno.com` share links are accepted;
- unknown fields (including `audio_url`/`mp3_url`) are rejected;
- no real catalogue data is committed; tests use synthetic records only;
- the tool is not deployed and cannot yet be called from ChatGPT.

For a future real connection, link-only/unpublished records are customer-
specific data and must remain behind user authentication. An anonymous first
demo may contain only records the user has explicitly approved as public.

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

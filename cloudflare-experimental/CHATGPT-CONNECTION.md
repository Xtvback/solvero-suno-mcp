# Solvero MCP 2.0 — ChatGPT connection preflight (NO DEPLOY)

**Status: NOT CONNECTABLE YET.** This file prepares future setup, not a live connector.
Do not enter any `.example.invalid` URL into ChatGPT. Do not deploy local
`__synthetic/*` endpoints. None of the URLs below currently exist.

## Connection form: intended values, not yet usable

| ChatGPT field | Future value | Ready? |
|---|---|---|
| Display name | Solvero MCP | Yes |
| Description | Read-only Solvero music catalogue, with explicit authorization | Draft only |
| Remote MCP server URL | `https://<reviewed-resource-worker-domain>/mcp` | No: no public Worker deployed |
| Authentication | OAuth 2.1 authorization-code + PKCE, user consent | No: real grant issuance disabled |
| Authorization issuer | `https://<reviewed-auth-worker-domain>` | No: no public issuer |
| Resource metadata | `https://<reviewed-resource-worker-domain>/.well-known/oauth-protected-resource/mcp` | Local only |
| OAuth authorization-server metadata | `https://<reviewed-auth-worker-domain>/.well-known/oauth-authorization-server` | Local only |
| Scopes | `mcp:read` (no write scope) | Prototype |
| Available tools | `synthetic_archive_status` | Synthetic only, not Suno catalogue |
| Privacy policy / trust review | Not available | Required before real connection |

The placeholders are not addresses and must not be interpreted as deployed URLs.
The `.example.invalid` URLs found in current Worker code deliberately do not resolve.

## Status from actual local tests

- Official MCP SDK client: `initialize`, `tools/list`, synthetic tool call over HTTP.
- Local Cloudflare Service Binding: resource protected by OAuth; 401/403;
  audience, expiry, scope, revocation of dummy UUID credentials.
- Local RFC 8414 / RFC 9728 discovery: verified on loopback test configurations.
- Local D1: PKCE S256 synthetic one-time code exchange, failed verifier/client,
  replay rejection. No real OAuth grant or refresh tokens.
- **No real Google OIDC**, Suno library access, DistroKid connection,
  remote HTTPS, ChatGPT connector handshake or real OAuth access token.

## What blocks first real read-only connection

1. Verify Suno's permitted integration/API can list the *user's own existing
   catalogue* with proper account authorization. An MCP proxy does not create
   access to Suno's private library.
2. Finish secure remote authorization server: OIDC JWT signature/JWKS,
   authenticated principal, explicit consent, PKCE/code lifecycle,
   token issuance/revocation and secure secrets. Existing production-oriented
   flow intentionally does **not** issue tokens.
3. Independently review and deploy dedicated HTTPS **read-only** Workers, with
   explicit user approval, separate storage, rate limits, monitoring and
   correct issuer/resource origins. Never deploy localhost test fixtures.
4. Enter the actual HTTPS resource `/mcp` URL in ChatGPT **only after**
   successful security and integration verification. Validate discovery,
   OAuth login and tool listing from ChatGPT's connection UI.
5. First permitted action: read-only listing, without download, writes,
   `archive_song` commit or distribution.

## Hard restrictions

No deploy, no credentials, no live Suno/Google/Work, no paid services,
no MP3/private recordings, no public URL and no real-token issuance are
authorized by this document. All fixtures remain test-only. The mere
presence of an 'Add custom MCP server' UI option does **not** prove this
server is ready or that Suno's catalogue API exists.

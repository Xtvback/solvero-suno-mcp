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
| Available tools | `synthetic_archive_status`, `list_catalogue` | Local only; catalogue uses an explicit manifest, not Suno synchronization |
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
- Read-only catalogue: schema validation, rejection of audio/private fields,
  filtering, pagination and invocation through the official MCP TypeScript client.
- **No real Google OIDC**, Suno library access, DistroKid connection,
  remote HTTPS, ChatGPT connector handshake or real OAuth access token.

## Confirmed ChatGPT connection requirements

OpenAI's official custom MCP guide currently says ChatGPT on the web accepts a
Server URL or Secure MCP Tunnel, supports SSE and Streamable HTTP, and offers
OAuth, no authentication, or mixed authentication:
https://developers.openai.com/api/docs/guides/custom-mcp-server .

OpenAI's official authentication guide says customer-specific data should be
authenticated. For OAuth it requires an OAuth 2.1-compatible MCP flow,
protected-resource metadata, authorization-server discovery, client
identification/registration and PKCE, plus resource-server validation of
signature, issuer, audience/resource, expiry and scopes:
https://developers.openai.com/plugins/build/auth .

Therefore:

- a synthetic/local MCP test is not enough to connect ChatGPT;
- a reachable reviewed HTTPS Server URL **or** an authorized Secure MCP Tunnel
  is required;
- an anonymous public-catalogue demo is technically possible only with records
  explicitly approved as public;
- a personal catalogue containing link-only/unpublished works requires real
  user authentication and authorization;
- the current server uses Streamable HTTP correctly in local tests, but its
  real OAuth issuance and remote origin remain intentionally incomplete.

## What blocks first real read-only connection

1. Live Suno sync remains blocked: no provider-approved API to list the user's
   existing consumer Library was verified. An MCP proxy does not create access.
2. For a personal/link-only catalogue, finish the secure remote authorization server: OIDC JWT signature/JWKS,
   authenticated principal, explicit consent, PKCE/code lifecycle,
   token issuance/revocation and secure secrets. Existing production-oriented
   flow intentionally does **not** issue tokens.
3. Independently review and deploy dedicated HTTPS **read-only** Workers, with
   explicit user approval, separate storage, rate limits, monitoring and
   correct issuer/resource origins. Never deploy localhost test fixtures.
4. Enter the actual HTTPS resource `/mcp` URL in ChatGPT **only after**
   successful security and integration verification. Validate discovery,
   OAuth login and tool listing from ChatGPT's connection UI.
5. First permitted action: `list_catalogue` over an explicit user manifest,
   without download, writes, `archive_song` commit or distribution.

## Shortest viable milestone (chosen)

Use the implemented `list_catalogue` tool with a reviewed metadata-only
manifest. This yields a genuine MCP read-only query while avoiding unsupported
Suno access. It is locally testable now. It becomes callable from ChatGPT only
after one of these separately authorized steps:

1. deploy the reviewed remote server and authentication; or
2. configure an approved Secure MCP Tunnel.

Neither step was performed. No public URL, tunnel, account connection or real
manifest was created.

## Hard restrictions

No deploy, no credentials, no live Suno/Google/Work, no paid services,
no MP3/private recordings, no public URL and no real-token issuance are
authorized by this document. All fixtures remain test-only. The mere
presence of an 'Add custom MCP server' UI option does **not** prove this
server is ready or that Suno's catalogue API exists.

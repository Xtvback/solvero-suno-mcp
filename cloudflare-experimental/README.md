# Solvero MCP 2.0 — experimental local-only security boundary

**Not deployed. Do not use this branch or its test fixtures as a production service.**
Production `main` is unchanged. No real Google login, Suno connection, MP3 or
paid Cloudflare resource is used. No real MCP access token can be issued here.

## Architecture

- `auth-server/index.ts`: experimental authorization Worker; Google OIDC callback,
  state and CSRF; no OAuth authorization-code grant completion.
- `mcp-server/index.ts`: OAuth protected resource, read-only synthetic
  Streamable HTTP subset (`initialize`, `tools/list`, `tools/call`).
- `oauth-state.sql` and `auth-server/state-gate.ts`: local D1 atomic one-time
  state and consent consumption, expiration checks, identity/scope/audience binding.
- `auth-server/local-test.ts` and `mcp-server/local-bound.ts`: **test-only**
  Workers with synthetic bearer tokens. The local fixture issues test UUIDs
  through `/__synthetic/issue`, and revokes them via `/__synthetic/revoke`.
  It does not generate a real OAuth access token or complete Authorization Code.
- `wrangler-auth-binding-local.json` and `wrangler-resource-binding-local.json`
  configure local service binding over ports 8798/8799 without public routes.
  These are not deployment configurations.

## Security invariants

1. All real token issuance and `archive_song` commit/upload remain disabled.
2. No synthetic route is imported into `auth-server/index.ts`,
   `mcp-server/index.ts` or the ordinary `wrangler.toml`.
3. Synthetic endpoints require HTTP loopback origin and are never exposed through
   production configuration. **A Host check alone is not a secure deploy guard**:
   clients could forge Host. Do not deploy local fixture files or configs.
4. Unknown or malformed bearer tokens get 401; valid test tokens with missing
   scope get 403; expired, revoked or wrong-audience test tokens get 401.
   Unexpected backend/Service Binding failures must remain 503 (not silently 401).
5. D1's conditional update provides one-time consumption of login/consent
   authorizations, not one-time use of normal bearer tokens.
6. No credential, token, MP3, user identity or private audio is committed.

## Local testing

In `cloudflare-experimental`, run `npm install --no-audit --no-fund`,
`npm run check`, and `npm run test:d1`. GitHub Actions additionally launches
both local Workers with Wrangler, checks RFC 8414 and RFC 9728 discovery,
401/403, audience, expiry, revocation, and invokes MCP `initialize` and
`tools/list` through a real local Service Binding; it separately exercises
the official MCP TypeScript client.

CI includes static tests to catch fixture references in production configs,
but **cannot technically prevent a person from deliberately deploying a test
file manually**. Only deploy reviewed production entrypoints.

## OAuth and ChatGPT compatibility status

* **Verified in synthetic local tests:** OAuth metadata RFC 8414 on the
  127.0.0.1 issuer, protected resource metadata RFC 9728, MCP JSON-RPC
  Streamable HTTP initialization, tools listing, token audience, missing
  scopes, expiration, simulated revocation, local Service Binding.
* **Not yet verified:** actual Google OpenID Connect consent end-to-end,
  authorization-code issuance and PKCE exchange/replay across both Workers,
  token refresh, real ChatGPT connector behavior, real remote HTTPS origins,
  and hardening of every network/revocation failure mode.
* The prior issuer configured with `.example.invalid` does not match
  localhost and may return 404 for RFC 8414 local discovery. The dedicated
  loopback issuer is the tested configuration, not a fix for deployment.

## Release gate

Before considering any real ChatGPT connection, independently review
OIDC signature verification (replace experimental Google tokeninfo with
JWKS-based verification), authenticated user and consent, D1 replay safety,
OAuth code and token lifecycle, safe endpoints and secrets, remote HTTPS
metadata, rate limiting, errors, and full official MCP client conformance.
No deploy or production modification is authorized by these tests.

# Solvero remote MCP experiment — fail closed

This directory is NOT deployed. It is isolated from the production Python MCP.
The Cloudflare Worker serves /health only and deliberately refuses /mcp with 503,
until an OAuth 2.1 authorization server with token issuance, PKCE, discovery,
client registration/metadata, consent, refresh tokens and principal verification
is integrated and security-tested.

Cloudflare D1 schema stores request IDs, hashes, expiry and principal IDs;
it stores no MP3 bytes or Suno credentials. Production's Python SQLite cannot
be attached directly to Workers; this is an alternative persistence design.
Do not copy this scaffold into production. The schema is not applied to any live D1 database.

Before enabling any remote MCP tool:
1. Create a separate Cloudflare Worker and D1 database, explicitly Free plan.
2. Integrate official OAuthResourceServer + OAuthAuthorizationServer with an
   external authenticated user identity and consent.
3. Verify state, PKCE, client registration/CIMD and refresh-token flows in a
   real ChatGPT connector test. Reject all unauthenticated requests.
4. Bind approved identity, package hashes and permission snapshots to D1.
5. Keep commit upload-disabled, including for authorized synthetic requests.
6. Validate rate limits, audit logs, full upload failure scenarios and consent.

No service was deployed, no billing account changed, no songs touched.

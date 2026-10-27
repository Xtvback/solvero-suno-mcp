# OAuth implementation decision (pending identity provider)

The current remote server uses a **static bearer token**, not OAuth. A public `/health` route is intentionally unauthenticated; MCP routes remain token-protected. Do **not** register this server as a ChatGPT OAuth connector yet.

## Required for production
- Choose a trusted OAuth authorization server / identity provider and register an OAuth client.
- Support Authorization Code + PKCE, redirect URI validation, token expiration and refresh (if applicable).
- Publish authorization-server and protected-resource metadata at the expected HTTPS endpoints.
- Validate access token issuer, audience, signature, expiry and scopes on **every** MCP request.
- Bind tokens to the correct owner and enforce tool-level authorization.
- Never log or commit secrets, codes, refresh tokens or private user content.
- Add end-to-end tests for invalid issuer/audience/scope, expired tokens, token revocation and unauthorized access.
- Verify ChatGPT custom connector compatibility in the target account before activation.

## Decision needed
Choose an identity provider and hosting configuration. Do not invent OAuth issuer URLs or client secrets. No provider has been configured, and no OAuth authentication flow has been tested.

## Current limitations
- Render Free may sleep and lose local files after restart or redeployment.
- The current tools do not access Suno or DistroKid accounts.
- A successful `/health` response is not proof that MCP authorization or tools work.

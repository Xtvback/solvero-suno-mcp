# Auth0 OAuth implementation

The remote server validates Auth0-issued RS256 access tokens. `/health` and the RFC 9728 protected-resource metadata routes are public; `/mcp` requires a token for this server's audience with the `mcp:tools` scope.

## Implemented

- Auth0 supplies Authorization Code + PKCE and authorization-server discovery.
- The server validates issuer, audience, expiration and RS256 signatures from Auth0 JWKS.
- The server requires `mcp:tools` from the token's `scope` or `permissions` claims.
- Unauthorized requests return a Bearer challenge pointing to protected-resource metadata.
- No Auth0 client secret is stored in this resource server.

## Deployment requirements

- Enable Auth0's Resource Parameter Compatibility Profile.
- Keep the ChatGPT OAuth client separate from this API resource and configure the exact ChatGPT callback.
- Never log or commit client secrets, codes, refresh tokens or private user content.
- Complete an interactive ChatGPT login and MCP tool test before calling the integration production-ready.

## Current limitations

- Render Free may sleep and lose local files after restart or redeployment.
- The tools do not access Suno accounts or unofficial Suno APIs.
- A successful `/health` response is not proof that OAuth or MCP tools work.

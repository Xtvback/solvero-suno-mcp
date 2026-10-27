# OAuth rollout checklist

1. Register the two MCP resources with an OAuth provider supporting the ChatGPT connector flow.
2. Record the provider's issuer and JWKS endpoints; do not guess them.
3. Configure each resource's distinct audience and required scope.
4. Implement protected-resource metadata and OAuth discovery.
5. Verify JWT signatures using provider JWKS; validate issuer, audience, expiry and scopes.
6. Test missing, malformed, expired and wrong-audience tokens.
7. Test authorized MCP initialize and tools/list requests end-to-end.
8. Enable OAuth in a staging deployment before removing the existing bearer-token fallback.
9. Register both HTTPS MCP endpoints in ChatGPT and validate login.
10. Only then explore Suno/DistroKid provider integrations.

Current status: **planning only**. This repository does not yet support OAuth.

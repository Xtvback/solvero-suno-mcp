# OAuth rollout checklist

1. [x] Register the resource in Auth0 with its distinct audience and `mcp:tools` scope.
2. [x] Publish RFC 9728 protected-resource metadata.
3. [x] Validate Auth0 RS256 JWT signatures, issuer, audience, lifetime and scope.
4. [x] Return a discoverable `WWW-Authenticate` challenge on unauthorized MCP requests.
5. [x] Test missing, malformed, expired and wrong-audience tokens offline.
6. [ ] Enable Auth0's Resource Parameter Compatibility Profile for the tenant.
7. [ ] Configure the predefined ChatGPT OAuth client callback and grants in Auth0.
8. [ ] Deploy the OAuth build on Render Free and verify metadata plus `401` behavior.
9. [ ] Register the HTTPS MCP endpoint in ChatGPT with the predefined OAuth client.
10. [ ] Complete an interactive login and test initialize, tools/list and tool calls end-to-end.

The static bearer fallback has been removed. `/health` and protected-resource metadata are
public; `/mcp` requires a valid Auth0 access token with `mcp:tools`.

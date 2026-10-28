# Roadmap: remote MCP and integrations

## Current security boundary
- Local MCP is available via stdio. The remote Streamable HTTP endpoint is deployed on Render Free and protected by Auth0 OAuth.
- `/mcp` requires an RS256 token with the correct issuer, audience, lifetime and `mcp:tools` scope.
- `/health` and RFC 9728 protected-resource metadata are intentionally public.
- No API keys, tokens or passwords should be committed to this public repository.
- The local catalogue/manifest is not a cloud database. Treat its contents as private.
- Files are not uploaded to Suno or DistroKid by this project.

## Remote deployment status
1. [x] Publish the Streamable HTTP endpoint over HTTPS on Render Free.
2. [x] Implement Auth0 discovery, protected-resource metadata and JWT validation.
3. [x] Require authorization for every MCP request.
4. [x] Test the local MCP protocol and the public authentication boundary.
5. [ ] Register the connector in ChatGPT and complete the first interactive login and tool call.
6. [ ] Add durable storage and rate limiting before storing important or multi-user data.

## Provider integrations
Suno: verify the official developer/API offering, account eligibility, licensing and permitted operations before adding any API calls. Avoid unofficial scraping or credential sharing.

## Chat production workflow
- [x] Produce one dry-run contract for concept, title, lyrics, Suno request,
  cover brief and DistroKid handoff.
- [x] Convert generation lyrics into distribution-ready plain lyrics without
  section labels.
- [x] Validate local WAV metadata and JPEG dimensions without uploading files.
- [x] Keep the final DistroKid submission as a manual user click.
- [ ] Add the verified official Suno generation request only after account,
  endpoint, quota and cost authorization.
- [ ] Generate a real cover only after the user approves its creative brief.
- [ ] Exercise the handoff with real user-approved audio and cover files.

## Verification
Offline tests cover syntax, OAuth validation and MCP routing. Live checks cover the Render health, metadata and unauthorized boundary. They do not test a real Suno account, a completed ChatGPT login or publication.

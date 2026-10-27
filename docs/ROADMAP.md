# Roadmap: remote MCP and integrations

## Current security boundary
- Local MCP via stdio only. No remote HTTPS endpoint and no OAuth yet.
- No API keys, tokens or passwords should be committed to this public repository.
- The local catalogue/manifest is not a cloud database. Treat its contents as private.
- Files are not uploaded to Suno or DistroKid by this project.

## Remote deployment (future)
1. Choose a hosting provider with persistent HTTPS and secrets management.
2. Implement Streamable HTTP transport and authentication compatible with ChatGPT's connector requirements.
3. Require authorization for every tool, apply rate limits, and scope access to one owner.
4. Validate input, audit data handling, and test access controls before enabling remote access.
5. Configure the connector only after an externally reachable authenticated endpoint exists.

## Provider integrations
Suno: verify the official developer/API offering, account eligibility, licensing and permitted operations before adding any API calls. Avoid unofficial scraping or credential sharing.

## Verification
GitHub Actions performs Python syntax checks and offline unit tests. Those tests do not verify provider APIs, deployment, OAuth or actual publication.

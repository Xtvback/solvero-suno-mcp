# Optional remote transport (experimental)

`remote_server.py` exposes MCP Streamable HTTP at `/mcp/` behind a static bearer token. It is a **development-only, single-owner** transport, not OAuth. **Do not connect it as a production ChatGPT custom connector**: ChatGPT-compatible OAuth, token lifecycle, resource indicators, authorization checks, and a public HTTPS endpoint still need to be implemented and verified.

## Local start

```bash
pip install -r requirements.txt
export MCP_BEARER_TOKEN="$(python -c 'import secrets; print(secrets.token_urlsafe(48))')"
python remote_server.py
```

On Windows PowerShell, set the environment variable manually to a long randomly generated secret before running. The default bind is localhost:8000. For Docker deployment, configure `MCP_BEARER_TOKEN` as a secret in the hosting provider; never commit it to GitHub. HTTPS termination, durable storage, backups, rate limiting and OAuth are not supplied by this repository.

**Security:** An empty/short token causes startup to fail; all HTTP requests without the token receive 401. The current transport is not a complete authorization solution. Do not publish any port publicly without an HTTPS proxy and additional controls.

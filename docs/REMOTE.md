# Remote transport

`remote_server.py` exposes MCP Streamable HTTP at `/mcp` behind Auth0 OAuth. It validates RS256 signatures, issuer, the server-specific audience, token lifetime and `mcp:tools`. `/health` and protected-resource metadata remain public.

## Local start

```bash
pip install -r requirements.txt
export AUTH0_ISSUER="https://solvero-mcp.eu.auth0.com/"
export AUTH0_AUDIENCE="https://solvero-suno-mcp.onrender.com/mcp"
export AUTH0_REQUIRED_SCOPE="mcp:tools"
python remote_server.py
```

The default bind is localhost:8000. No Auth0 client secret belongs in this resource server or repository. Render terminates HTTPS; durable storage, backups and rate limiting remain separate deployment concerns.

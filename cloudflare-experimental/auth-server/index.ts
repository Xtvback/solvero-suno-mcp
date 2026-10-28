import { AuthorizationError, OAuthAuthorizationServer } from "@cloudflare/workers-oauth-provider";
import { WorkerEntrypoint } from "cloudflare:workers";

// Experimental only. No identity provider configured: authorization MUST fail closed.
interface Env { OAUTH_KV: KVNamespace }
export const RESOURCE = "https://solvero-archive-experimental.example.invalid/mcp";
export const ISSUER = "https://solvero-auth-experimental.example.invalid";
const server = new OAuthAuthorizationServer<Env>({
  issuer: ISSUER, resources: [RESOURCE], scopesSupported: ["mcp:read", "offline_access"],
  clientIdMetadataDocumentEnabled: true,
});
async function authorize(request: Request, env: Env): Promise<Response> {
  const oauth = server.getOAuthApi(env);
  try {
    // Library validates PKCE S256, client metadata and resource registration.
    await oauth.parseAuthRequest(request);
  } catch (err) {
    if (err instanceof AuthorizationError) {
      return err.redirectTo ? Response.redirect(err.redirectTo, 302)
        : new Response("Invalid OAuth authorization request",{status:400});
    }
    throw err;
  }
  // No fake user/automatic consent. A real upstream authenticated login + CSRF-safe
  // consent screen must be added before calling completeAuthorization().
  return new Response("Verified user login and explicit consent not configured",{
    status:503,headers:{"cache-control":"no-store"}
  });
}
export default class AuthServer extends WorkerEntrypoint<Env> {
  fetch(request: Request) {
    if(new URL(request.url).pathname==="/authorize")return authorize(request,this.env);
    return server.fetch(request,this.env,this.ctx);
  }
  validateToken(resource: string, token: string) {
    return server.validateToken(resource,token,this.env);
  }
}

import { OAuthResourceServer, insufficientScope,
  type AuthorizationServerBinding } from "@cloudflare/workers-oauth-provider";
interface AuthProps { userId: string }
interface Env { AUTH_SERVER: AuthorizationServerBinding<AuthProps>; APPROVALS_DB: D1Database }
const RESOURCE = "https://solvero-archive-experimental.example.invalid/mcp";
export default new OAuthResourceServer<Env,AuthProps>({
  resourceMetadata: {resource:RESOURCE,authorization_servers:[
    "https://solvero-auth-experimental.example.invalid"],
    resource_name:"Solvero Synthetic Archive Experiment"},
  requiredScopes:["mcp:read"],
  validateToken:(env)=>env.AUTH_SERVER.validateToken,
  handler:{
    fetch(request,env,ctx) {
      if(!ctx.auth.scope.includes("mcp:read"))
        return insufficientScope(ctx.auth,["mcp:read"]);
      const path=new URL(request.url).pathname;
      if(path==="/health")return Response.json({mode:"synthetic-only",uploaded:false});
      // The MCP transport is deliberately not wired until auth can be proven.
      return Response.json({error:"mcp_transport_not_activated",
        authenticated_subject_present:Boolean(ctx.props.userId),
        uploads_enabled:false},{status:503});
    }
  }
});

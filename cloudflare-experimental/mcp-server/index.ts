import { OAuthResourceServer, insufficientScope,
  type AuthorizationServerBinding } from "@cloudflare/workers-oauth-provider";
import {syntheticMcp} from "./transport";
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
      if(!ctx.props.userId)return new Response("Missing verified principal",{status:403});
      if(path!=="/mcp")return new Response("Not found",{status:404});
      return syntheticMcp(request);
    }
  }
});

import { OAuthResourceServer, insufficientScope,
  type AuthorizationServerBinding } from "@cloudflare/workers-oauth-provider";
import {syntheticMcp} from "./transport";
import {parseCatalogueManifest} from "./catalogue.ts";
interface AuthProps { userId: string }
interface Env { AUTH_SERVER: AuthorizationServerBinding<AuthProps>; APPROVALS_DB: D1Database; CATALOGUE_MANIFEST_JSON?: string }
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
      try {
        const catalogue=parseCatalogueManifest(env.CATALOGUE_MANIFEST_JSON);
        if(catalogue.owner_user_id&&catalogue.owner_user_id!==ctx.props.userId)
          return new Response("Catalogue owner mismatch",{status:403});
        return syntheticMcp(request,catalogue);
      }
      catch { return new Response("Catalogue configuration unavailable",{status:503}); }
    }
  }
});

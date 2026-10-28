/** Local-only test fixture. NEVER deploy or import into production. */
import {OAuthResourceServer,insufficientScope} from "@cloudflare/workers-oauth-provider";
import {syntheticMcp} from "./transport";
const RESOURCE="http://127.0.0.1:8789/mcp";
export default new OAuthResourceServer({
 resourceMetadata:{resource:RESOURCE,authorization_servers:["http://127.0.0.1:8788"],resource_name:"Solvero local test"},
 requiredScopes:["mcp:read"],
 validateToken:()=>async(resource:string,token:string)=>{
  if(token!=="synthetic-read"&&token!=="synthetic-no-scope"&&token!=="synthetic-wrong-audience")return null;
  return {props:{userId:"synthetic-user"},audience:token==="synthetic-wrong-audience"?"http://127.0.0.1:8789/other":resource,
          scope:token==="synthetic-no-scope"?[]:["mcp:read"],userId:"synthetic-user",clientId:"synthetic-client"};
 },
 handler:{fetch(request,_env,ctx){
  if(!ctx.auth.scope.includes("mcp:read"))return insufficientScope(ctx.auth,["mcp:read"]);
  if(new URL(request.url).pathname!=="/mcp")return new Response("Not found",{status:404});
  return syntheticMcp(request);
 }}
});

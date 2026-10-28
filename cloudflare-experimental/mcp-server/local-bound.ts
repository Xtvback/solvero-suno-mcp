// Local-only resource Worker with real Cloudflare service binding.
import {OAuthResourceServer,insufficientScope,type AuthorizationServerBinding} from "@cloudflare/workers-oauth-provider";
import {syntheticMcp} from "./transport";
interface Env{AUTH_SERVER:AuthorizationServerBinding<{userId:string}>}
export default new OAuthResourceServer<Env,{userId:string}>({
 resourceMetadata:{resource:"http://127.0.0.1:8799/mcp",authorization_servers:["http://127.0.0.1:8798"],resource_name:"Solvero bound local test"},
 requiredScopes:["mcp:read"],
 validateToken:(env)=>async(resource:string,token:string)=>{
  if(!/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(token))return null;
  return env.AUTH_SERVER.validateToken(resource,token);
 },
 handler:{fetch(request,env,ctx){
  if(!ctx.auth.scope.includes("mcp:read"))return insufficientScope(ctx.auth,["mcp:read"]);
  if(!ctx.props.userId)return new Response("Invalid principal",{status:403});
  if(new URL(request.url).pathname!=="/mcp")return new Response("Not found",{status:404});
  return syntheticMcp(request);
 }}
});

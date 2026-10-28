// STRICTLY LOCAL SYNTHETIC FIXTURE. Not an OAuth authorization grant or deployable issuer.
import {OAuthAuthorizationServer} from "@cloudflare/workers-oauth-provider";
import {WorkerEntrypoint} from "cloudflare:workers";
import {syntheticCodeRequest,syntheticCodeExchange} from "./synthetic-code";
interface Env {OAUTH_KV:KVNamespace; APPROVALS_DB:D1Database}
const issuer="http://127.0.0.1:8798";
const resource="http://127.0.0.1:8799/mcp";
const server=new OAuthAuthorizationServer<Env>({issuer,resources:[resource],scopesSupported:["mcp:read"],clientIdMetadataDocumentEnabled:false});
function local(req:Request){const u=new URL(req.url);return u.protocol==="http:"&&u.hostname==="127.0.0.1"&&u.port==="8798";}
export default class SyntheticAuth extends WorkerEntrypoint<Env>{
 async fetch(request:Request){
  const url=new URL(request.url);
  if(url.pathname==="/authorize")return new Response("Synthetic auth disabled",{status:503});
  if(url.pathname==="/__synthetic/code"||url.pathname==="/__synthetic/exchange"){
   if(!local(request)||request.method!=="POST")return new Response("Not permitted",{status:403});
   const body=await request.json() as {challenge?:string;code?:string;verifier?:string;client?:string;redirect?:string};
   if(url.pathname.endsWith("/code")){
    const code=await syntheticCodeRequest(this.env.APPROVALS_DB,body.challenge??"",body.redirect??"",body.client??"");
    return code?Response.json({code,synthetic:true},{headers:{"cache-control":"no-store"}}):new Response("Invalid PKCE request",{status:400});
   }
   const ok=await syntheticCodeExchange(this.env.APPROVALS_DB,body.code??"",body.verifier??"",body.redirect??"",body.client??"");
   return Response.json({exchanged:ok,synthetic:true},{status:ok?200:400,headers:{"cache-control":"no-store"}});
  }
  if(url.pathname==="/__synthetic/issue"||url.pathname==="/__synthetic/revoke"){
   if(!local(request)||request.method!=="POST")return new Response("Not permitted",{status:403});
   const body=await request.json() as {token?:string;scope?:string;audience?:string;expires?:number};
   if(url.pathname.endsWith("/issue")){
    const token=crypto.randomUUID(),expires=Date.now()+Math.min(60000,Math.max(-1000,Number(body.expires??60000)));
    await this.env.OAUTH_KV.put("fixture:"+token,JSON.stringify({scope:body.scope??"mcp:read",audience:body.audience??resource,expires}));
    return Response.json({token,synthetic:true},{headers:{"cache-control":"no-store"}});
   }
   if(typeof body.token!=="string")return new Response("Missing token",{status:400});
   await this.env.OAUTH_KV.delete("fixture:"+body.token);
   return Response.json({revoked:true,synthetic:true},{headers:{"cache-control":"no-store"}});
  }
  return server.fetch(request,this.env,this.ctx);
 }
 async validateToken(audience:string,token:string){
  // Test tokens are never genuine OAuth access tokens.
  if(!/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(token))return null;
  const stored=await this.env.OAUTH_KV.get("fixture:"+token);
  if(!stored)return null;
  const v=JSON.parse(stored) as {scope:string;audience:string;expires:number};
  if(v.expires<=Date.now()||v.audience!==audience)return null;
  return {props:{userId:"synthetic-principal"},audience:v.audience,scope:v.scope? v.scope.split(" "):[],
    userId:"synthetic-principal",clientId:"synthetic-client"};
 }
}

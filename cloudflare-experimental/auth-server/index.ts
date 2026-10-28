import { AuthorizationError, OAuthAuthorizationServer, type AuthRequest } from "@cloudflare/workers-oauth-provider";
import { WorkerEntrypoint } from "cloudflare:workers";
import {claimLogin,claimConsent} from "./state-gate";
import {randomToken,sha256url,googleLoginUrl,exchangeGoogleCode,verifyGoogleIdToken, type PendingLogin} from "./google-oidc";
interface Env { OAUTH_KV: KVNamespace; APPROVALS_DB:D1Database; GOOGLE_CLIENT_ID?:string; GOOGLE_CLIENT_SECRET?:string }
export const RESOURCE="https://solvero-archive-experimental.example.invalid/mcp";
export const ISSUER="https://solvero-auth-experimental.example.invalid";
const server=new OAuthAuthorizationServer<Env>({
 issuer:ISSUER,resources:[RESOURCE],scopesSupported:["mcp:read","offline_access"],clientIdMetadataDocumentEnabled:true
});
const noStore={"cache-control":"no-store"};
function fail(message:string,status=400){return new Response(message,{status,headers:noStore});}
function cookieValue(request:Request,key:string){
 const match=request.headers.get("cookie")?.match(new RegExp("(?:^|; )"+key+"=([^;]+)"));
 return match?match[1]:undefined;
}
async function authorize(request:Request,env:Env):Promise<Response>{
 if(!env.GOOGLE_CLIENT_ID||!env.GOOGLE_CLIENT_SECRET)return fail("Google OAuth credentials are not configured",503);
 const oauth=server.getOAuthApi(env);
 let oauthRequest:AuthRequest;
 try{oauthRequest=await oauth.parseAuthRequest(request);}
 catch(err){if(err instanceof AuthorizationError)return err.redirectTo?Response.redirect(err.redirectTo,302):fail("Invalid OAuth request");throw err;}
 const state=randomToken(),verifier=randomToken(),nonce=randomToken(),browser=randomToken();
 const challenge=await sha256url(verifier);
 const redirectUri=ISSUER+"/google/callback";
 const pending:PendingLogin={state,verifier,nonce,created:Date.now(),clientId:env.GOOGLE_CLIENT_ID,redirectUri,oauthRequest:JSON.stringify(oauthRequest)};
 const browserHash=await sha256url(browser);
 await env.APPROVALS_DB.prepare("INSERT INTO oauth_login_states (state_hash,browser_hash,client_id,redirect_uri,scope_hash,resource_uri,created_at,expires_at,consumed_at) VALUES (?,?,?,?,?,?,?,?,NULL)")
   .bind(await sha256url(state),browserHash,oauthRequest.clientId,oauthRequest.redirectUri,await sha256url(JSON.stringify(oauthRequest.scope)),RESOURCE,Date.now(),Date.now()+300000).run();
 await env.OAUTH_KV.put("login:"+state,JSON.stringify({...pending,browserHash}),{expirationTtl:300});
 return new Response(null,{status:302,headers:{
   location:googleLoginUrl(env.GOOGLE_CLIENT_ID,redirectUri,state,challenge,nonce),
   "set-cookie":"solvero_browser="+browser+"; HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=300",
   ...noStore}});
}
async function callback(request:Request,env:Env):Promise<Response>{
 if(!env.GOOGLE_CLIENT_SECRET)return fail("Login unavailable",503);
 const url=new URL(request.url),state=url.searchParams.get("state"),code=url.searchParams.get("code");
 if(!state||!code)return fail("Google authorization denied or incomplete");
 const stored=await env.OAUTH_KV.get("login:"+state);
 if(!stored)return fail("Expired or unknown login state");
 const pending=JSON.parse(stored) as PendingLogin & {browserHash:string};
 const browser=cookieValue(request,"solvero_browser");
 if(!browser||await sha256url(browser)!==pending.browserHash||pending.state!==state||Date.now()-pending.created>300000)return fail("Browser or state mismatch",403);
 // D1 must later be used for atomic compare-and-consume; KV delete alone is not atomic.
 // Therefore remote OAuth grant completion remains intentionally disabled.
 if(!await claimLogin(env.APPROVALS_DB,await sha256url(state),pending.browserHash,Date.now()))return fail("Login replay or expired",403);
 await env.OAUTH_KV.delete("login:"+state);
 const tokens=await exchangeGoogleCode(code,pending,env.GOOGLE_CLIENT_SECRET);
 if(typeof tokens.id_token!=="string")return fail("No Google ID token",403);
 const identity=await verifyGoogleIdToken(tokens.id_token,pending.clientId,pending.nonce);
 if(!identity.sub)return fail("Verified identity missing",403);
 const original=JSON.parse(pending.oauthRequest) as AuthRequest;
 const consentId=randomToken(),csrf=randomToken(),principal=await sha256url(identity.sub);
 const scope=await sha256url(JSON.stringify(original.scope));
 await env.APPROVALS_DB.prepare("INSERT INTO oauth_consents (consent_hash,state_hash,principal_hash,client_id,redirect_uri,scope_hash,resource_uri,csrf_hash,expires_at,consumed_at) VALUES (?,?,?,?,?,?,?,?,?,NULL)")
 .bind(await sha256url(consentId),await sha256url(state),principal,original.clientId,original.redirectUri,scope,RESOURCE,await sha256url(csrf),Date.now()+300000).run();
 await env.OAUTH_KV.put("consent:"+consentId,JSON.stringify({principal,client:original.clientId,redirect:original.redirectUri,scope,resource:RESOURCE}),{expirationTtl:300});
 const page="<h1>Solvero experimental</h1><p>Autorizar leitura sintética? Cliente: "+original.clientId.replace(/[^a-zA-Z0-9._-]/g,"")+"</p><form method='POST' action='/consent'><input name='id' type='hidden' value='"+consentId+"'><input name='csrf' type='hidden' value='"+csrf+"'><button name='decision' value='approve'>Autorizar</button><button name='decision' value='deny'>Recusar</button></form>";
 return new Response(page,{status:200,headers:{"content-type":"text/html; charset=utf-8","set-cookie":"solvero_consent="+consentId+"; HttpOnly; Secure; SameSite=Strict; Path=/; Max-Age=300",...noStore}});
}
async function consent(request:Request,env:Env):Promise<Response>{
 if(request.method!=="POST")return fail("POST required",405);
 const form=await request.formData();
 const id=form.get("id"),csrf=form.get("csrf"),decision=form.get("decision");
 if(typeof id!=="string"||typeof csrf!=="string"||cookieValue(request,"solvero_consent")!==id)return fail("CSRF or browser mismatch",403);
 if(decision!=="approve"&&decision!=="deny")return fail("Explicit decision required",400);
 const data=await env.OAUTH_KV.get("consent:"+id);
 if(!data)return fail("Consent missing or expired",403);
 const v=JSON.parse(data) as {principal:string;client:string;redirect:string;scope:string;resource:string};
 const valid=await claimConsent(env.APPROVALS_DB,{id:await sha256url(id),user:v.principal,csrf:await sha256url(csrf),client:v.client,redirect:v.redirect,scope:v.scope,resource:v.resource},Date.now());
 if(!valid)return fail("Consent replay or mismatch",403);
 await env.OAUTH_KV.delete("consent:"+id);
 return fail(decision==="approve"?"Consent recorded; token issuance disabled":"Consent refused",503);
}
export default class AuthServer extends WorkerEntrypoint<Env>{
 fetch(request:Request){
  const path=new URL(request.url).pathname;
  if(path==="/authorize")return authorize(request,this.env);
  if(path==="/google/callback")return callback(request,this.env);
  if(path==="/consent")return consent(request,this.env);
  return server.fetch(request,this.env,this.ctx);
 }
 validateToken(resource:string,token:string){return server.validateToken(resource,token,this.env);}
}

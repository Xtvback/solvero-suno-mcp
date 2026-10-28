import { AuthorizationError, OAuthAuthorizationServer, type AuthRequest } from "@cloudflare/workers-oauth-provider";
import { WorkerEntrypoint } from "cloudflare:workers";
import {randomToken,sha256url,googleLoginUrl,exchangeGoogleCode,verifyGoogleIdToken, type PendingLogin} from "./google-oidc";
interface Env { OAUTH_KV: KVNamespace; GOOGLE_CLIENT_ID?:string; GOOGLE_CLIENT_SECRET?:string }
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
 await env.OAUTH_KV.put("login:"+state,JSON.stringify({...pending,browserHash:await sha256url(browser)}),{expirationTtl:300});
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
 await env.OAUTH_KV.delete("login:"+state);
 const tokens=await exchangeGoogleCode(code,pending,env.GOOGLE_CLIENT_SECRET);
 if(typeof tokens.id_token!=="string")return fail("No Google ID token",403);
 const identity=await verifyGoogleIdToken(tokens.id_token,pending.clientId,pending.nonce);
 if(!identity.sub)return fail("Verified identity missing",403);
 return fail("Google identity validated; consent and MCP token issuance remain blocked until atomic state and CSRF validation",503);
}
export default class AuthServer extends WorkerEntrypoint<Env>{
 fetch(request:Request){
  const path=new URL(request.url).pathname;
  if(path==="/authorize")return authorize(request,this.env);
  if(path==="/google/callback")return callback(request,this.env);
  return server.fetch(request,this.env,this.ctx);
 }
 validateToken(resource:string,token:string){return server.validateToken(resource,token,this.env);}
}

/** Google OpenID Connect helpers: PKCE and state remain server-side. No tokens logged. */
const enc=new TextEncoder();
function b64url(bytes:Uint8Array):string {let s="";for(const x of bytes)s+=String.fromCharCode(x);return btoa(s).replace(/\+/g,"-").replace(/\//g,"_").replace(/=+$/,"");}
export function randomToken():string {const bytes=new Uint8Array(32);crypto.getRandomValues(bytes);return b64url(bytes);}
export async function sha256url(text:string):Promise<string>{return b64url(new Uint8Array(await crypto.subtle.digest("SHA-256",enc.encode(text))));}
export interface PendingLogin {state:string;verifier:string;nonce:string;created:number;clientId:string;redirectUri:string;oauthRequest:string;}
export function googleLoginUrl(clientId:string,redirectUri:string,state:string,challenge:string,nonce:string):string {
  const q=new URLSearchParams({client_id:clientId,redirect_uri:redirectUri,response_type:"code",scope:"openid email",state,code_challenge:challenge,code_challenge_method:"S256",nonce,prompt:"select_account"});
  return "https://accounts.google.com/o/oauth2/v2/auth?"+q.toString();
}
export async function exchangeGoogleCode(code:string,pending:PendingLogin,clientSecret:string):Promise<Record<string,unknown>>{
  const res=await fetch("https://oauth2.googleapis.com/token",{method:"POST",headers:{"content-type":"application/x-www-form-urlencoded"},
    body:new URLSearchParams({code,client_id:pending.clientId,client_secret:clientSecret,redirect_uri:pending.redirectUri,grant_type:"authorization_code",code_verifier:pending.verifier})});
  if(!res.ok)throw new Error("Google token exchange failed");
  return await res.json() as Record<string,unknown>;
}
export async function verifyGoogleIdToken(idToken:string,clientId:string,nonce:string):Promise<{sub:string,email?:string}>{
  // Google's tokeninfo validation endpoint is solely for experimental use.
  // Production should verify JWT signature locally with Google's rotating JWKs.
  const res=await fetch("https://oauth2.googleapis.com/tokeninfo?id_token="+encodeURIComponent(idToken));
  if(!res.ok)throw new Error("Google ID token invalid");
  const t=await res.json() as Record<string,unknown>;
  if(t.aud!==clientId||t.iss!=="https://accounts.google.com"&&t.iss!=="accounts.google.com"||
     t.nonce!==nonce||!t.sub||Number(t.exp)*1000<=Date.now())
    throw new Error("Google issuer, audience, nonce or expiry invalid");
  return {sub:String(t.sub),email:typeof t.email==="string"?t.email:undefined};
}

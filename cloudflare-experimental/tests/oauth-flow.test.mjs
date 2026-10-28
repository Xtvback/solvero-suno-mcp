import assert from "node:assert/strict";
import {test} from "node:test";
import {googleLoginUrl,sha256url,exchangeGoogleCode,verifyGoogleIdToken} from "../auth-server/google-oidc.ts";
import {claimLogin,claimConsent} from "../auth-server/state-gate.ts";
import {Miniflare} from "miniflare";
const schema=`CREATE TABLE oauth_login_states (state_hash TEXT PRIMARY KEY,browser_hash TEXT,client_id TEXT,redirect_uri TEXT,scope_hash TEXT,resource_uri TEXT,created_at INTEGER,expires_at INTEGER,consumed_at INTEGER);
CREATE TABLE oauth_consents (consent_hash TEXT PRIMARY KEY,state_hash TEXT,principal_hash TEXT,client_id TEXT,redirect_uri TEXT,scope_hash TEXT,resource_uri TEXT,csrf_hash TEXT,expires_at INTEGER,consumed_at INTEGER);`;
test("synthetic OAuth: Google PKCE, token exchange, ID verification, D1 consent and replay",async()=>{
 const original=globalThis.fetch;let calls=0;
 globalThis.fetch=async(url,options)=>{
   calls++;
   if(String(url).includes("/tokeninfo"))return Response.json({aud:"test-client",iss:"https://accounts.google.com",nonce:"test-nonce",sub:"synthetic-sub",exp:Math.floor(Date.now()/1000)+300});
   if(String(url)==="https://oauth2.googleapis.com/token"){
     assert.equal(new URLSearchParams(options.body).get("code_verifier"),"synthetic-verifier");
     return Response.json({id_token:"fake-test-id-token"});
   }
   throw new Error("Unexpected external call");
 };
 const mf=new Miniflare({modules:true,script:'export default {fetch(){return new Response("offline")}}',d1Databases:{DB:"00000000-0000-4000-8000-000000000002"}});
 try {
 const db=await mf.getD1Database("DB");for(const sql of schema.split(";").map(s=>s.trim()).filter(Boolean))await db.prepare(sql).run();
 const url=new URL(googleLoginUrl("test-client","https://example.invalid/callback","state",await sha256url("synthetic-verifier"),"test-nonce"));
 assert.equal(url.searchParams.get("code_challenge_method"),"S256");
 assert.equal(url.searchParams.get("nonce"),"test-nonce");
 const pending={clientId:"test-client",redirectUri:"https://example.invalid/callback",verifier:"synthetic-verifier",state:"state",nonce:"test-nonce",created:Date.now(),oauthRequest:"{}"};
 const token=await exchangeGoogleCode("fake-code",pending,"test-secret");
 const identity=await verifyGoogleIdToken(String(token.id_token),pending.clientId,pending.nonce);
 assert.equal(identity.sub,"synthetic-sub");
 const now=Date.now(),user=await sha256url(identity.sub),csrf=await sha256url("csrf");
 await db.prepare("INSERT INTO oauth_login_states VALUES (?,?,?,?,?,?,?,?,NULL)").bind("state","browser","test-client",pending.redirectUri,"read","mcp",now,now+300000).run();
 assert.equal(await claimLogin(db,"state","browser",now+1),true);
 assert.equal(await claimLogin(db,"state","browser",now+2),false);
 await db.prepare("INSERT INTO oauth_consents VALUES (?,?,?,?,?,?,?,?,?,NULL)").bind("consent","state",user,"test-client",pending.redirectUri,"read","mcp",csrf,now+300000).run();
 const values={id:"consent",user,csrf,client:"test-client",redirect:pending.redirectUri,scope:"read",resource:"mcp"};
 assert.equal(await claimConsent(db,{...values,csrf:"wrong"},now+3),false);
 assert.equal(await claimConsent(db,values,now+4),true);
 assert.equal(await claimConsent(db,values,now+5),false);
 assert.equal(calls,2);
 }finally{globalThis.fetch=original;await mf.dispose();}
});
test("synthetic Google identity rejects wrong audience, nonce and expiry",async()=>{
 const original=globalThis.fetch;
 try{
 for(const field of ["aud","nonce","exp"]){
  const info={aud:"test-client",iss:"https://accounts.google.com",nonce:"test-nonce",sub:"synthetic",exp:Math.floor(Date.now()/1000)+300};
  info[field]=field==="exp"?1:"invalid";
  globalThis.fetch=async()=>Response.json(info);
  await assert.rejects(()=>verifyGoogleIdToken("fake","test-client","test-nonce"));
 }
 }finally{globalThis.fetch=original;}
});

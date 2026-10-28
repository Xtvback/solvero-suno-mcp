import assert from "node:assert/strict";
import {test} from "node:test";
import {readFile} from "node:fs/promises";
import {Miniflare} from "miniflare";
import {claimLogin,claimConsent} from "../auth-server/state-gate.ts";
const schema=await readFile(new URL("../oauth-state.sql",import.meta.url),"utf8");
async function fixture(){
 const mf=new Miniflare({modules:true,script:'export default {fetch(){return new Response("offline")}}',
 d1Databases:{DB:"00000000-0000-4000-8000-000000000001"}});
 const db=await mf.getD1Database("DB");
 await db.exec(schema);
 return {db,mf};
}
test("actual local D1: concurrent login claims, expiry and browser binding",async()=>{
 const {db,mf}=await fixture();
 try{
 const now=Date.now();
 await db.prepare("INSERT INTO oauth_login_states VALUES (?,?,?,?,?,?,?,?,NULL)").bind("state","browser","client","redirect","scope","resource",now,now+10000).run();
 const results=await Promise.all(Array.from({length:12},()=>claimLogin(db,"state","browser",now+1)));
 assert.equal(results.filter(Boolean).length,1);
 assert.equal(await claimLogin(db,"state","browser",now+2),false);
 await db.prepare("INSERT INTO oauth_login_states VALUES (?,?,?,?,?,?,?,?,NULL)").bind("expired","browser","client","redirect","scope","resource",now-10000,now-1).run();
 assert.equal(await claimLogin(db,"expired","browser",now),false);
 assert.equal(await claimLogin(db,"expired","wrong",now-2000),false);
 }finally{await mf.dispose();}
});
test("actual local D1: consent replay, csrf, principal, client, redirect and scope",async()=>{
 const {db,mf}=await fixture();
 try{
 const now=Date.now(),v={id:"consent",user:"principal",csrf:"csrf",client:"client",redirect:"redirect",scope:"scope",resource:"resource"};
 await db.prepare("INSERT INTO oauth_consents VALUES (?,?,?,?,?,?,?,?,?,NULL)").bind(v.id,"state",v.user,v.client,v.redirect,v.scope,v.resource,v.csrf,now+10000).run();
 assert.equal(await claimConsent(db,{...v,csrf:"invalid"},now),false);
 assert.equal(await claimConsent(db,{...v,user:"invalid"},now),false);
 assert.equal(await claimConsent(db,{...v,client:"invalid"},now),false);
 assert.equal(await claimConsent(db,{...v,redirect:"invalid"},now),false);
 assert.equal(await claimConsent(db,{...v,scope:"invalid"},now),false);
 const results=await Promise.all(Array.from({length:12},()=>claimConsent(db,v,now)));
 assert.equal(results.filter(Boolean).length,1);
 assert.equal(await claimConsent(db,v,now),false);
 }finally{await mf.dispose();}
});

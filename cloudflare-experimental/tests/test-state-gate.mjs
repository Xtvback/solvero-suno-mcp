import assert from "node:assert/strict";
import {test} from "node:test";
import {claimLogin,claimConsent} from "../auth-server/state-gate.ts";
function fakeDb(){
 const claimed=new Set();
 return {prepare(sql){
   return {bind(...args){return {async run(){
     const id=String(args[1]),validExpiry=Number(args.at(-1))<200;
     const unique=id+"-"+(sql.includes("oauth_consents")?"consent":"login");
     const valid=validExpiry && !claimed.has(unique) && args.every(x=>x!=="wrong");
     if(valid)claimed.add(unique);
     return {meta:{changes:valid?1:0}};
   }}}};
 }};
}
test("login gate permits exactly one concurrent claimant",async()=>{
 const db=fakeDb();
 const results=await Promise.all(Array.from({length:20},()=>claimLogin(db,"state","browser",100)));
 assert.equal(results.filter(Boolean).length,1);
});
test("login expiration and browser mismatch reject",async()=>{
 assert.equal(await claimLogin(fakeDb(),"state","browser",201),false);
 assert.equal(await claimLogin(fakeDb(),"state","wrong",100),false);
});
test("consent gate single use, bound principal and csrf",async()=>{
 const db=fakeDb(),v={id:"consent",user:"principal",csrf:"csrf",client:"client",redirect:"redirect",scope:"read",resource:"mcp"};
 assert.equal(await claimConsent(db,v,100),true);
 assert.equal(await claimConsent(db,v,100),false);
 assert.equal(await claimConsent(fakeDb(),{...v,user:"wrong"},100),false);
 assert.equal(await claimConsent(fakeDb(),{...v,csrf:"wrong"},100),false);
});

import assert from "node:assert/strict";
import {test} from "node:test";
import {Miniflare} from "miniflare";
import {readFile} from "node:fs/promises";
const source=await readFile(new URL("../mcp-server/index.ts",import.meta.url),"utf8");
test("metadata and 401 challenge in isolated Worker with synthetic token validator",async()=>{
 const script=`import resourceServer from "./mcp-server/index.ts"; export default resourceServer;`;
 const mf=new Miniflare({modules:true,script,modulesRules:[{type:"ESModule",include:["**/*.ts"]}],
  serviceBindings:{AUTH_SERVER:async()=>Response.json({valid:false})},
  d1Databases:{APPROVALS_DB:"00000000-0000-4000-8000-000000000009"}});
 try{
 const r=await mf.dispatchFetch("https://solvero-archive-experimental.example.invalid/mcp");
 assert.equal(r.status,401);
 const header=r.headers.get("www-authenticate")||"";
 assert.match(header,/Bearer/i);
 assert.match(header,/resource_metadata/);
 const metadata=await mf.dispatchFetch("https://solvero-archive-experimental.example.invalid/.well-known/oauth-protected-resource/mcp");
 assert.equal(metadata.status,200);
 const json=await metadata.json();
 assert.deepEqual(json.scopes_supported,["mcp:read"]);
 }finally{await mf.dispose();}
});

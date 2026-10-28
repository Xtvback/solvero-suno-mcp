import assert from "node:assert/strict";
import {test} from "node:test";
import {syntheticMcp} from "../mcp-server/transport.ts";
const endpoint="https://synthetic.invalid/mcp";
function call(method,id=1,params={}) {return syntheticMcp(new Request(endpoint,{method:"POST",headers:{"content-type":"application/json","accept":"application/json, text/event-stream"},body:JSON.stringify({jsonrpc:"2.0",id,method,params})}));}
test("MCP initialize and tools/list and call are synthetic read-only",async()=>{
 const a=await call("initialize",1,{protocolVersion:"2025-06-18",capabilities:{},clientInfo:{name:"synthetic-client",version:"1"}});
 assert.equal(a.status,200);assert.equal((await a.json()).result.protocolVersion,"2025-06-18");
 const b=await call("tools/list");const tools=(await b.json()).result.tools;
 assert.deepEqual(tools.map(x=>x.name),["synthetic_archive_status"]);
 const c=await call("tools/call",3,{name:"synthetic_archive_status",arguments:{}});
 const flags=JSON.parse((await c.json()).result.content[0].text);
 assert.equal(flags.uploads_enabled,false);assert.equal(flags.commit_enabled,false);
});
test("no mutation method, unknown tool, malformed request and wrong Accept",async()=>{
 const u=await call("tools/call",2,{name:"archive_song",arguments:{stage:"commit"}});
 assert.equal(u.status,400);assert.equal((await u.json()).error.code,-32602);
 const x=await call("resources/write");assert.equal((await x.json()).error.code,-32601);
 const wrong=await syntheticMcp(new Request(endpoint,{method:"POST",headers:{"content-type":"application/json","accept":"application/json"},body:"{}"}));
 assert.equal(wrong.status,406);
 const bad=await syntheticMcp(new Request(endpoint,{method:"POST",headers:{"content-type":"application/json","accept":"application/json,text/event-stream"},body:"{"}));
 assert.equal((await bad.json()).error.code,-32700);
 const del=await syntheticMcp(new Request(endpoint,{method:"DELETE"}));assert.equal(del.status,405);
});
test("MCP notification and GET cannot open writable session",async()=>{
 const n=await syntheticMcp(new Request(endpoint,{method:"POST",headers:{"content-type":"application/json","accept":"application/json,text/event-stream"},body:JSON.stringify({jsonrpc:"2.0",method:"notifications/initialized"})}));
 assert.equal(n.status,202);
 assert.equal((await syntheticMcp(new Request(endpoint))).status,405);
});

import {test} from "node:test";
import assert from "node:assert/strict";
import {createServer} from "node:http";
import {Client} from "@modelcontextprotocol/sdk/client/index.js";
import {StreamableHTTPClientTransport} from "@modelcontextprotocol/sdk/client/streamableHttp.js";
import {syntheticMcp} from "../mcp-server/transport.ts";
test("official MCP client: initialize, tools/list and readonly call over actual localhost HTTP",async()=>{
 const server=createServer(async(req,res)=>{
  const chunks=[];for await(const chunk of req)chunks.push(chunk);
  const url="http://127.0.0.1"+req.url;
  const request=new Request(url,{method:req.method,headers:req.headers,body:["GET","HEAD"].includes(req.method)?undefined:Buffer.concat(chunks)});
  const result=await syntheticMcp(request);res.writeHead(result.status,Object.fromEntries(result.headers));res.end(Buffer.from(await result.arrayBuffer()));
 });
 await new Promise(resolve=>server.listen(0,"127.0.0.1",resolve));
 const port=server.address().port;
 const transport=new StreamableHTTPClientTransport(new URL("http://127.0.0.1:"+port+"/mcp"));
 const client=new Client({name:"solvero-synthetic-official-client",version:"1.0.0"},{capabilities:{}});
 try{
 await client.connect(transport);
 const list=await client.listTools();
 assert.deepEqual(list.tools.map(t=>t.name),["synthetic_archive_status"]);
 const result=await client.callTool({name:"synthetic_archive_status",arguments:{}});
 assert.equal(JSON.parse(result.content[0].text).uploads_enabled,false);
 await assert.rejects(()=>client.callTool({name:"archive_song",arguments:{stage:"commit"}}));
 }finally{await transport.close().catch(()=>{});await new Promise(resolve=>server.close(resolve));}
});

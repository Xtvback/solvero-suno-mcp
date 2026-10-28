/** Stateless MCP Streamable HTTP subset: read-only tools only. */
import {listCatalogue, type CatalogueManifest} from "./catalogue.ts";
const VERSION="2025-06-18";
const response=(id:unknown,result:unknown)=>Response.json({jsonrpc:"2.0",id,result},{headers:{"cache-control":"no-store","mcp-protocol-version":VERSION}});
const error=(id:unknown,code:number,message:string,status=400)=>new Response(JSON.stringify({jsonrpc:"2.0",id,error:{code,message}}),{status,headers:{"content-type":"application/json","cache-control":"no-store"}});
export async function syntheticMcp(request:Request,catalogue:CatalogueManifest={version:1,entries:[]}):Promise<Response>{
 if(request.method==="DELETE")return new Response(null,{status:405,headers:{"allow":"POST, GET"}});
 if(request.method==="GET")return new Response(null,{status:405,headers:{"allow":"POST"}});
 if(request.method!=="POST")return new Response(null,{status:405,headers:{"allow":"POST"}});
 if(!(request.headers.get("content-type")||"").toLowerCase().startsWith("application/json"))return error(null,-32600,"JSON required",415);
 const accept=request.headers.get("accept")||"";
 if(!accept.includes("application/json")||!accept.includes("text/event-stream"))return error(null,-32600,"MCP Accept required",406);
 let body:unknown;
 try {body=await request.json();}catch{return error(null,-32700,"Parse error");}
 if(!body||typeof body!=="object"||Array.isArray(body))return error(null,-32600,"Invalid request");
 const msg=body as Record<string,unknown>;
 if(msg.jsonrpc!=="2.0"||typeof msg.method!=="string")return error(msg.id??null,-32600,"Invalid request");
 if(!Object.prototype.hasOwnProperty.call(msg,"id"))return new Response(null,{status:202});
 if(msg.method==="initialize"){
  const params=msg.params as {protocolVersion?:string}|undefined;
  if(!params||typeof params.protocolVersion!=="string")return error(msg.id,-32602,"protocolVersion required");
  return response(msg.id,{protocolVersion:VERSION,capabilities:{tools:{listChanged:false}},serverInfo:{name:"solvero-synthetic-experiment",version:"0.1.0"}});
 }
 if(msg.method==="ping")return response(msg.id,{});
 if(msg.method==="tools/list")return response(msg.id,{tools:[
  {name:"synthetic_archive_status",description:"Report synthetic-only archive safety flags. Never accesses Suno, Drive or audio.",inputSchema:{type:"object",properties:{},additionalProperties:false},annotations:{readOnlyHint:true,destructiveHint:false,idempotentHint:true,openWorldHint:false}},
  {name:"list_catalogue",description:"List the authorized user-provided Solvero catalogue. Returns metadata and Suno share links only; it never connects to a Suno account or reads audio.",inputSchema:{type:"object",properties:{query:{type:"string",description:"Optional case-insensitive title, creator, description or status filter."},limit:{type:"integer",minimum:1,maximum:100,default:50},cursor:{type:"string",pattern:"^[0-9]+$"}},additionalProperties:false},annotations:{readOnlyHint:true,destructiveHint:false,idempotentHint:true,openWorldHint:false}},
 ]});
 if(msg.method==="tools/call"){
  const p=msg.params as {name?:string;arguments?:Record<string,unknown>}|undefined;
  if(p?.name==="list_catalogue"){
   try {
    const result=listCatalogue(catalogue,p.arguments||{});
    return response(msg.id,{content:[{type:"text",text:JSON.stringify(result)}],structuredContent:result,isError:false});
   } catch (cause) {
    return error(msg.id,-32602,cause instanceof Error?cause.message:"Invalid catalogue query");
   }
  }
  if(p?.name!=="synthetic_archive_status")return error(msg.id,-32602,"Unknown tool");
  if(p.arguments&&Object.keys(p.arguments).length)return error(msg.id,-32602,"Tool takes no arguments");
  return response(msg.id,{content:[{type:"text",text:JSON.stringify({synthetic_only:true,uploads_enabled:false,commit_enabled:false})}],isError:false});
 }
 return error(msg.id,-32601,"Method not found");
}

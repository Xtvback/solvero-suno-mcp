// Fail-closed HTTPS scaffold. This is NOT a functional OAuth server.
// No credential cookies, no audio downloads, no deployment automation.
const json=(value,status,headers={})=>new Response(JSON.stringify(value),{
  status, headers:{"content-type":"application/json; charset=utf-8",
    "cache-control":"no-store",...headers}});
export default {
  async fetch(request,env) {
    const path=new URL(request.url).pathname;
    if(path==="/health")return json({service:"solvero-archive-experimental",
      mode:"synthetic-only",oauth_ready:false,uploads_enabled:false},200);
    if(path==="/mcp")return json({error:"oauth_not_configured",
      message:"OAuth provider, verified identity and resource metadata required before serving MCP"},503);
    return json({error:"not_found"},404);
  }
};

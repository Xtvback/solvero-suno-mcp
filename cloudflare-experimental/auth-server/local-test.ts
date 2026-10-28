// Test-only local issuer. No authorization grant can ever be created here.
import {OAuthAuthorizationServer} from "@cloudflare/workers-oauth-provider";
import {WorkerEntrypoint} from "cloudflare:workers";
interface Env {OAUTH_KV:KVNamespace}
const issuer="http://127.0.0.1:8798";
const server=new OAuthAuthorizationServer<Env>({issuer,resources:["http://127.0.0.1:8799/mcp"],scopesSupported:["mcp:read"],clientIdMetadataDocumentEnabled:false});
export default class SyntheticAuth extends WorkerEntrypoint<Env>{
 fetch(request:Request){
  if(new URL(request.url).pathname==="/authorize")return new Response("Synthetic auth disabled",{status:503});
  return server.fetch(request,this.env,this.ctx);
 }
 validateToken(resource:string,token:string){return server.validateToken(resource,token,this.env);}
}

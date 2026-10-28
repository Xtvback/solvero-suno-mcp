/** Synthetic local PKCE authorization-code fixture backed by atomic D1 consumption.
 * NEVER IMPORT INTO PRODUCTION. No actual OAuth code/token is minted here.
 */
export async function syntheticCodeRequest(db:D1Database,challenge:string,redirect:string,client:string){
 if(!/^[A-Za-z0-9_-]{43}$/.test(challenge)||!redirect.startsWith("http://127.0.0.1/")||!client)return null;
 await db.prepare("CREATE TABLE IF NOT EXISTS synthetic_pkce_codes (code TEXT PRIMARY KEY,challenge TEXT NOT NULL,redirect TEXT NOT NULL,client TEXT NOT NULL,expires INTEGER NOT NULL,consumed INTEGER)").run();
 const code=crypto.randomUUID();
 await db.prepare("INSERT INTO synthetic_pkce_codes VALUES (?,?,?,?,?,NULL)").bind(code,challenge,redirect,client,Date.now()+60000).run();
 return code;
}
export async function syntheticCodeExchange(db:D1Database,code:string,verifier:string,redirect:string,client:string){
 if(!/^[A-Za-z0-9_-]{43,128}$/.test(verifier))return false;
 const dig=new Uint8Array(await crypto.subtle.digest("SHA-256",new TextEncoder().encode(verifier)));
 const value=btoa(String.fromCharCode(...dig)).replace(/\+/g,"-").replace(/\//g,"_").replace(/=+$/,"");
 const result=await db.prepare("UPDATE synthetic_pkce_codes SET consumed=? WHERE code=? AND challenge=? AND redirect=? AND client=? AND consumed IS NULL AND expires>?").bind(Date.now(),code,value,redirect,client,Date.now()).run();
 return result.meta.changes===1;
}

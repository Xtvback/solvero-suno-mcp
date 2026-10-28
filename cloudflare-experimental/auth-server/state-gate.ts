export async function claimLogin(db: D1Database, state: string, browser: string, now: number): Promise<boolean> {
 const result = await db.prepare("UPDATE oauth_login_states SET consumed_at=? WHERE state_hash=? AND browser_hash=? AND consumed_at IS NULL AND expires_at>?").bind(now,state,browser,now).run();
 return result.meta.changes === 1;
}
export async function claimConsent(db: D1Database, values: {id:string; user:string; csrf:string; client:string; redirect:string; scope:string; resource:string}, now:number): Promise<boolean> {
 const result = await db.prepare("UPDATE oauth_consents SET consumed_at=? WHERE consent_hash=? AND principal_hash=? AND csrf_hash=? AND client_id=? AND redirect_uri=? AND scope_hash=? AND resource_uri=? AND consumed_at IS NULL AND expires_at>?").bind(now,values.id,values.user,values.csrf,values.client,values.redirect,values.scope,values.resource,now).run();
 return result.meta.changes === 1;
}

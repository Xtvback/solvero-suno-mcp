-- D1 atomic state transition for experimental OAuth. No token issuance.
CREATE TABLE IF NOT EXISTS oauth_login_states (
 state_hash TEXT PRIMARY KEY,
 browser_hash TEXT NOT NULL,
 client_id TEXT NOT NULL,
 redirect_uri TEXT NOT NULL,
 scope_hash TEXT NOT NULL,
 resource_uri TEXT NOT NULL,
 created_at INTEGER NOT NULL,
 expires_at INTEGER NOT NULL,
 consumed_at INTEGER
);
CREATE TABLE IF NOT EXISTS oauth_consents (
 consent_hash TEXT PRIMARY KEY,
 state_hash TEXT NOT NULL,
 principal_hash TEXT NOT NULL,
 client_id TEXT NOT NULL,
 redirect_uri TEXT NOT NULL,
 scope_hash TEXT NOT NULL,
 resource_uri TEXT NOT NULL,
 csrf_hash TEXT NOT NULL,
 expires_at INTEGER NOT NULL,
 consumed_at INTEGER
);

-- Experimental-only persistent approvals; no music binaries stored.
CREATE TABLE IF NOT EXISTS archive_approvals (
  request_id TEXT PRIMARY KEY,
  principal_id TEXT NOT NULL,
  package_sha256 TEXT NOT NULL,
  permissions_sha256 TEXT NOT NULL,
  confirmation_sha256 TEXT NOT NULL,
  expires_at INTEGER NOT NULL,
  state TEXT NOT NULL CHECK(state IN ('pending','consumed')),
  created_at INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_archive_expiry ON archive_approvals(expires_at);

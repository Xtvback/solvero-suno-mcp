import pathlib, sqlite3, tempfile, unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
SQL=(ROOT/"oauth-state.sql").read_text()
class OAuthD1Tests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
  self.path=pathlib.Path(self.tmp.name)/"test.db"
  self.db=sqlite3.connect(self.path)
  self.db.executescript(SQL)
  self.db.execute("INSERT INTO oauth_login_states VALUES (?,?,?,?,?,?,?,?,NULL)",("state","browser","client","https://example.invalid/cb","scope","resource",100,200))
  self.db.execute("INSERT INTO oauth_consents VALUES (?,?,?,?,?,?,?,?,?,NULL)",("consent","state","principal","client","https://example.invalid/cb","scope","resource","csrf",200))
  self.db.commit();self.addCleanup(self.db.close)
 def test_login_single_use(self):
  sql="UPDATE oauth_login_states SET consumed_at=? WHERE state_hash=? AND browser_hash=? AND consumed_at IS NULL AND expires_at>?"
  self.assertEqual(self.db.execute(sql,(150,"state","browser",150)).rowcount,1)
  self.assertEqual(self.db.execute(sql,(151,"state","browser",151)).rowcount,0)
 def test_expired_or_wrong_browser(self):
  sql="UPDATE oauth_login_states SET consumed_at=? WHERE state_hash=? AND browser_hash=? AND consumed_at IS NULL AND expires_at>?"
  self.assertEqual(self.db.execute(sql,(201,"state","browser",201)).rowcount,0)
  self.assertEqual(self.db.execute(sql,(150,"state","wrong",150)).rowcount,0)
 def test_consent_is_bound_and_single_use(self):
  sql="UPDATE oauth_consents SET consumed_at=? WHERE consent_hash=? AND principal_hash=? AND csrf_hash=? AND client_id=? AND redirect_uri=? AND scope_hash=? AND resource_uri=? AND consumed_at IS NULL AND expires_at>?"
  args=(150,"consent","principal","csrf","client","https://example.invalid/cb","scope","resource",150)
  self.assertEqual(self.db.execute(sql,args).rowcount,1)
  self.assertEqual(self.db.execute(sql,args).rowcount,0)
 def test_consent_changed_identity_or_scope(self):
  sql="UPDATE oauth_consents SET consumed_at=? WHERE consent_hash=? AND principal_hash=? AND csrf_hash=? AND client_id=? AND redirect_uri=? AND scope_hash=? AND resource_uri=? AND consumed_at IS NULL AND expires_at>?"
  for pos in (2,3,4,5,6,7):
   args=[150,"consent","principal","csrf","client","https://example.invalid/cb","scope","resource",150]
   args[pos]="wrong"
   self.assertEqual(self.db.execute(sql,tuple(args)).rowcount,0)
 def test_two_connections_only_one_wins(self):
  c2=sqlite3.connect(self.path)
  try:
   sql="UPDATE oauth_login_states SET consumed_at=? WHERE state_hash=? AND browser_hash=? AND consumed_at IS NULL AND expires_at>?"
   self.assertEqual(self.db.execute(sql,(150,"state","browser",150)).rowcount,1)
   self.db.commit()
   self.assertEqual(c2.execute(sql,(150,"state","browser",150)).rowcount,0)
  finally:c2.close()
if __name__=="__main__":unittest.main()

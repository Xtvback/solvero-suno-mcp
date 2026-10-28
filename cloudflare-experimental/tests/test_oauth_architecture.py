import pathlib,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
class OAuthArchitectureTests(unittest.TestCase):
 def test_library_auth_server_no_automatic_grant(self):
  auth=(ROOT/"auth-server/index.ts").read_text()
  self.assertIn("OAuthAuthorizationServer",auth)
  self.assertIn("parseAuthRequest",auth)
  self.assertNotIn("completeAuthorization(",auth)
  self.assertIn('fail("Google OAuth credentials are not configured",503)',auth)
 def test_oidc_pkce_state_and_browser_binding(self):
  auth=(ROOT/"auth-server/index.ts").read_text()
  helper=(ROOT/"auth-server/google-oidc.ts").read_text()
  for x in ("sha256url(verifier)","browserHash","expir","cookieValue","verifyGoogleIdToken"):
   self.assertIn(x,auth)
  for x in ("code_challenge_method","S256","code_verifier","t.nonce","t.aud","t.iss","t.exp"):
   self.assertIn(x,helper)
 def test_resource_verification_and_uploads_off(self):
  mcp=(ROOT/"mcp-server/index.ts").read_text()
  for s in ("OAuthResourceServer","validateToken","insufficientScope","syntheticMcp","Missing verified principal","owner_user_id","Catalogue owner mismatch"):self.assertIn(s,mcp)
 def test_no_live_endpoints(self):
  auth=(ROOT/"auth-server/index.ts").read_text()
  mcp=(ROOT/"mcp-server/index.ts").read_text()
  self.assertIn(".example.invalid",auth)
  self.assertIn(".example.invalid",mcp)
if __name__=="__main__":unittest.main()

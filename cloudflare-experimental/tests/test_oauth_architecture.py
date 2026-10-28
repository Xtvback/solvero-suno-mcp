import pathlib,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
class OAuthArchitectureTests(unittest.TestCase):
    def test_library_auth_server_not_fake_login(self):
        auth=(ROOT/"auth-server/index.ts").read_text()
        self.assertIn("OAuthAuthorizationServer",auth)
        self.assertIn("parseAuthRequest",auth)
        self.assertNotIn("completeAuthorization(",auth.split("async function authorize")[1].split("export default")[0].replace("// consent screen must be added before calling completeAuthorization().",""))
        self.assertIn("status:503",auth)
    def test_resource_verification_and_uploads_off(self):
        mcp=(ROOT/"mcp-server/index.ts").read_text()
        for s in ("OAuthResourceServer","validateToken","insufficientScope","uploads_enabled:false"):self.assertIn(s,mcp)
        self.assertIn("status:503",mcp)
    def test_endpoint_urls_are_not_live(self):
        auth=(ROOT/"auth-server/index.ts").read_text()
        mcp=(ROOT/"mcp-server/index.ts").read_text()
        self.assertIn(".example.invalid",auth)
        self.assertIn(".example.invalid",mcp)
if __name__=="__main__":unittest.main()

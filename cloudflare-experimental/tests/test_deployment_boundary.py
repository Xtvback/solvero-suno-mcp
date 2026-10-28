"""Reject accidental exposure of localhost synthetic OAuth fixtures in production configs."""
import json
import pathlib
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
class DeploymentBoundary(unittest.TestCase):
 def test_public_configs_exclude_synthetic_issuers(self):
  for path in [ROOT/"wrangler.toml"]:
   txt=path.read_text()
   self.assertNotIn("local-test.ts",txt)
   self.assertNotIn("local-bound.ts",txt)
   self.assertNotIn("__synthetic/issue",txt)
 def test_test_worker_configs_are_explicitly_nonpublic(self):
  for name in ("wrangler-auth-binding-local.json","wrangler-resource-binding-local.json"):
   obj=json.loads((ROOT/name).read_text())
   self.assertIs(obj["workers_dev"],False)
   self.assertNotIn("route",obj)
   self.assertNotIn("routes",obj)
   self.assertNotIn("triggers",obj)
 def test_synthetic_routes_only_in_test_fixture(self):
  paths=list((ROOT/"auth-server").glob("*.ts"))
  for path in paths:
   if path.name=="local-test.ts":continue
   self.assertNotIn("/__synthetic/issue",path.read_text())
   self.assertNotIn("/__synthetic/revoke",path.read_text())
 def test_local_fixture_no_token_inspection_route(self):
  src=(ROOT/"auth-server/local-test.ts").read_text()
  self.assertNotIn("/__synthetic/check",src)
  self.assertIn('u.protocol==="http:"',src)
  self.assertIn('u.hostname==="127.0.0.1"',src)
  self.assertIn('u.port==="8798"',src)
if __name__=="__main__":unittest.main()

import hashlib,json,tempfile,unittest
from pathlib import Path
from tools.safe_archive_package import prepare_archive_package
URL="https://suno.com/song/be108fa8-2efa-4aea-b32d-22f60b8e78fb"
class PackageTests(unittest.TestCase):
    def setUp(self):
        tmp=tempfile.TemporaryDirectory();self.addCleanup(tmp.cleanup)
        self.root=Path(tmp.name);self.audio=self.root/"original.mp3";self.cover=self.root/"cover.png"
        self.data=b"ID3"+bytes(range(256))*4;self.art=b"synthetic-cover"
        self.audio.write_bytes(self.data);self.cover.write_bytes(self.art)
        self.manifest=self.root/"catalog.json"
    def package(self,names=None):
        return prepare_archive_package(self.audio,self.cover,self.manifest,URL,"Static Riot","Synthetic Tune",
            approved_download=True,existing_names=names or [],declared_source="synthetic-only",
            c2pa_result={"state":"not_verified","manifest_present":False})
    def test_three_files_and_sha256_unchanged(self):
        p=self.package()
        self.assertEqual(len(p["files"]),3)
        self.assertEqual(p["files"][0]["sha256"],hashlib.sha256(self.data).hexdigest())
        self.assertEqual(p["files"][1]["sha256"],hashlib.sha256(self.art).hexdigest())
        self.assertEqual(p["files"][2]["sha256"],hashlib.sha256(self.manifest.read_bytes()).hexdigest())
        self.assertEqual(self.audio.read_bytes(),self.data);self.assertEqual(self.cover.read_bytes(),self.art)
        self.assertFalse(p["preflight"]["upload_performed"])
        self.assertEqual(json.loads(self.manifest.read_text())["policy"]["allow_apic_writes"],False)
    def test_duplicate_mp3_blocks_package(self):
        with self.assertRaises(ValueError):self.package(["STATIC RIOT - SYNTHETIC TUNE.MP3"])
        self.assertFalse(self.manifest.exists())
    def test_duplicate_cover_blocks_package(self):
        with self.assertRaises(FileExistsError):self.package(["static riot - synthetic tune.png"])
        self.assertFalse(self.manifest.exists())
    def test_duplicate_json_blocks_package(self):
        with self.assertRaises(FileExistsError):self.package(["Static Riot - Synthetic Tune.json"])
        self.assertFalse(self.manifest.exists())
    def test_existing_manifest_blocks_overwrite(self):
        self.manifest.write_text("DO_NOT_OVERWRITE")
        with self.assertRaises(FileExistsError):self.package()
        self.assertEqual(self.manifest.read_text(),"DO_NOT_OVERWRITE")
    def test_unauthorized_blocks(self):
        with self.assertRaises(ValueError):
            prepare_archive_package(self.audio,self.cover,self.manifest,URL,"Static Riot","Synthetic Tune",
                approved_download=False,existing_names=[],declared_source="synthetic")
        self.assertFalse(self.manifest.exists())
if __name__=="__main__":unittest.main()

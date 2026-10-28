import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from tools.c2pa_safe_archive import build_manifest, write_manifest, modify_protected_id3

class SafeArchiveTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.mp3=self.root/"original.mp3"
        self.original=b"ID3"+b"synthetic-GEOB-C2PA"+bytes(range(256))*3
        self.mp3.write_bytes(self.original)
        self.cover=self.root/"cover.jpg"
        self.cover.write_bytes(b"synthetic artwork")
        self.expected=hashlib.sha256(self.original).hexdigest()
    def manifest(self,**kwargs):
        return build_manifest(self.mp3,"NOVAR","Synthetic", "source declared, not verified",**kwargs)
    def test_hash_original_unchanged(self):
        m=self.manifest(cover=self.cover,c2pa={"integrity":"not_checked"})
        self.assertEqual(m["original_audio"]["sha256"],self.expected)
        self.assertFalse(m["source"]["verified"])
        self.assertFalse(m["policy"]["allow_apic_writes"])
        self.assertEqual(self.mp3.read_bytes(),self.original)
    def test_json_separate_and_original_unchanged(self):
        p=self.root/"manifest.json"
        write_manifest(self.manifest(),p,self.mp3)
        self.assertEqual(json.loads(p.read_text())["original_audio"]["sha256"],self.expected)
        self.assertEqual(self.mp3.read_bytes(),self.original)
    def test_reject_overwriting_manifest(self):
        p=self.root/"manifest.json";p.write_text("KEEP")
        with self.assertRaises(FileExistsError):write_manifest(self.manifest(),p,self.mp3)
        self.assertEqual(p.read_text(),"KEEP")
    def test_block_apic_id3(self):
        with self.assertRaises(PermissionError):modify_protected_id3(self.mp3,"APIC")
        self.assertEqual(self.mp3.read_bytes(),self.original)
    def test_reject_json_over_mp3(self):
        with self.assertRaises(ValueError):write_manifest(self.manifest(),self.mp3,self.mp3)
        self.assertEqual(self.mp3.read_bytes(),self.original)
    def test_invalid_metadata(self):
        with self.assertRaises(ValueError):build_manifest(self.mp3,"NOVAR","Synthetic","")
        bad=self.root/"cover.txt";bad.write_text("x")
        with self.assertRaises(ValueError):self.manifest(cover=bad)
        self.assertEqual(self.mp3.read_bytes(),self.original)

if __name__=="__main__":
    unittest.main()

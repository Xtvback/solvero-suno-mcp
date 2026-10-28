import hashlib
import tempfile
import unittest
from pathlib import Path
from tools.authorized_audio_intake import verify_mp3

class AudioIntakeTests(unittest.TestCase):
    def test_refuse_without_authorization(self):
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/"fixture.mp3"
            f.write_bytes(b"ID3"+bytes(128))
            with self.assertRaises(ValueError):
                verify_mp3(f, False)

    def test_sha256_and_immutable_bytes(self):
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/"fixture.mp3"
            payload=b"ID3"+bytes(128)
            f.write_bytes(payload)
            result=verify_mp3(f, True)
            self.assertEqual(result["size"],len(payload))
            self.assertEqual(result["sha256"],hashlib.sha256(payload).hexdigest())
            self.assertEqual(f.read_bytes(), payload)
            self.assertFalse(result["modified"])

    def test_preserve_synthetic_id3_metadata(self):
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/"fixture.mp3"
            payload=b"ID3" + b"SIMULATED-PROVENANCE-GEOB" + bytes(256)
            f.write_bytes(payload)
            verify_mp3(f, True)
            self.assertEqual(f.read_bytes(), payload)
            self.assertIn(b"SIMULATED-PROVENANCE-GEOB", f.read_bytes())

    def test_reject_other_data(self):
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/"fake.mp3"
            f.write_bytes(b"not-mp3"+bytes(256))
            with self.assertRaises(ValueError):
                verify_mp3(f, True)

    def test_reject_tiny_file(self):
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/"tiny.mp3"
            f.write_bytes(b"ID3")
            with self.assertRaises(ValueError):
                verify_mp3(f, True)

if __name__=="__main__":
    unittest.main()

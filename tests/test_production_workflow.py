import tempfile
import unittest
import wave
from pathlib import Path

from production_workflow import plain_distribution_lyrics,prepare_music_project,prepare_release_handoff


class ProductionWorkflowTests(unittest.TestCase):
    def test_docker_image_includes_workflow_module(self):
        dockerfile = (Path(__file__).parents[1] / "Dockerfile").read_text(encoding="utf-8")
        copy_lines = [line for line in dockerfile.splitlines() if line.startswith("COPY ")]
        self.assertTrue(any("production_workflow.py" in line for line in copy_lines))

    def test_complete_creative_plan_is_dry_run(self):
        result=prepare_music_project(title="Luz do Tejo",artist="Solvero",concept="Lisboa à noite",
            style="synth-pop melancólico",lyrics="[Verse]\nA cidade acorda\n\n[Chorus]\nLuz sobre o Tejo",
            cover_direction="reflexos azuis e âmbar",genre="Pop",release_date="2026-12-01")
        self.assertFalse(result["suno_generation"]["submitted"])
        self.assertFalse(result["cover_generation"]["generated"])
        self.assertEqual(result["cover_generation"]["delivery"]["width"],3000)
        self.assertNotIn("[Verse]",result["distribution"]["plain_lyrics"])
        self.assertEqual(result["distribution"]["final_submission"],"manual_user_click")
        self.assertEqual(result["safety"],{"provider_calls":False,"uploads":False,"publishing":False})

    def test_instrumental_cannot_have_lyrics(self):
        with self.assertRaises(ValueError):
            prepare_music_project(title="X",artist="Y",concept="Z",style="Ambient",
                                  lyrics="words",instrumental=True)

    def test_plain_lyrics_remove_labels_not_words(self):
        value=plain_distribution_lyrics("[Verse 1]\nPrimeira linha\nSegunda linha\n\n(Chorus)\nRefrão")
        self.assertEqual(value,"Primeira linha\nSegunda linha\n\nRefrão")

    def test_release_handoff_requires_real_local_assets_and_never_uploads(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);audio=root/"song.wav";cover=root/"cover.jpg"
            with wave.open(str(audio),"wb") as wav:
                wav.setnchannels(2);wav.setsampwidth(2);wav.setframerate(44100);wav.writeframes(b"\x00\x00\x00\x00"*100)
            cover.write_bytes(b"\xff\xd8\xff\xc0\x00\x11\x08\x0b\xb8\x0b\xb8\x03\x01\x11\x00\x02\x11\x00\x03\x11\x00\xff\xd9")
            result=prepare_release_handoff(title="Song",artist="Artist",audio_path=str(audio),cover_path=str(cover))
            self.assertEqual(result["status"],"ready_for_distrokid_preparation")
            self.assertFalse(result["uploads"]);self.assertFalse(result["publishing"])
            self.assertEqual(result["final_submission"],"manual_user_click")
            self.assertEqual(result["asset_details"]["cover"]["width"],3000)
            self.assertEqual(result["asset_details"]["audio"]["sample_rate"],44100)

    def test_release_handoff_reports_missing_assets(self):
        result=prepare_release_handoff(title="Song",artist="Artist",audio_path="missing.wav",cover_path="missing.png")
        self.assertEqual(result["status"],"incomplete")
        self.assertEqual(len(result["errors"]),2)


if __name__=="__main__": unittest.main()

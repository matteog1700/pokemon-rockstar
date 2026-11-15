#!/usr/bin/env python3
"""Contract tests for Rockstar's actual in-engine startup replacement."""
import importlib.util
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("rockstar_intro", HERE / "apply_intro.py")
intro = importlib.util.module_from_spec(spec)
spec.loader.exec_module(intro)


class GothicIntroTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "src").mkdir()
        (self.root / "sound" / "songs" / "midi").mkdir(parents=True)
        (self.root / "src" / "intro.c").write_text(
            "static void MainCB2_EndIntro(void);\n"
            "void copyright_scene(void) {\n"
            "  CreateTask(Task_Scene1_Load, 0);\n"
            "  SetMainCallback2(MainCB2_Intro);\n}\n"
        )
        (self.root / "sound" / "songs" / "midi" / "mus_intro.mid").write_bytes(b"old")

    def test_replaces_original_intro_and_is_idempotent(self):
        intro.apply(self.root)
        first = (self.root / "src" / "intro.c").read_text()
        midi = (self.root / "sound" / "songs" / "midi" / "mus_intro.mid").read_bytes()
        self.assertIn("CreateTask(Task_RockstarGothicMovie, 0);", first)
        self.assertNotIn("CreateTask(Task_Scene1_Load, 0);", first)
        self.assertIn("DISPCNT_MODE_3", first)
        self.assertIn("ROCKSTAR", first)
        self.assertTrue(midi.startswith(b"MThd"))
        self.assertEqual(int.from_bytes(midi[10:12], "big"), 5)
        intro.apply(self.root)
        self.assertEqual(first, (self.root / "src" / "intro.c").read_text())
        self.assertEqual(midi, (self.root / "sound" / "songs" / "midi" / "mus_intro.mid").read_bytes())

    def test_unexpected_upstream_is_rejected(self):
        (self.root / "src" / "intro.c").write_text("other source")
        with self.assertRaises(RuntimeError):
            intro.apply(self.root)


if __name__ == "__main__":
    unittest.main()

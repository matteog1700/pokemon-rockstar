#!/usr/bin/env python3
"""Fast local contract tests for the Rockstar source patcher."""
import importlib.util
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("rockstar_patches", HERE / "apply_gameplay.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class RockstarPatchesTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.engine = Path(self.tmp.name)
        (self.engine / "src").mkdir()
        (self.engine / "graphics" / "object_events" / "palettes").mkdir(parents=True)
        (self.engine / "include" / "constants").mkdir(parents=True)
        (self.engine / "data" / "maps" / "LittlerootTown").mkdir(parents=True)
        (self.engine / "graphics" / "weather").mkdir(parents=True)
        (self.engine / "graphics" / "weather" / "fog.pal").write_text(
            "JASC-PAL\n0100\n16\n" + "0 0 0\n" * 16
        )
        (self.engine / "src" / "field_weather_effect.c").write_text(
            "    gWeatherPtr->targetRainSpriteCount = 10;\n"
            "    SetRainStrengthFromSoundEffect(SE_RAIN);\n"
        )
        header = "\n".join(f"ITEM_{name}," for name in (*module.BALL_ITEMS, "RARE_CANDY"))
        (self.engine / "include" / "constants" / "items.h").write_text(header)

        palette_dir = self.engine / "graphics" / "object_events" / "palettes"
        palette = "JASC-PAL\n0100\n16\n" + "\n".join(
            f"{i * 11 % 255} {i * 9 % 255} {i * 7 % 255}" for i in range(16)
        ) + "\n"
        for i in range(1, 5):
            for suffix in ("", "_reflection"):
                (palette_dir / f"npc_{i}{suffix}.pal").write_text(palette)

        (self.engine / "src" / "new_game.c").write_text(
            "void NewGameInitData(void) {\n    ClearBag();\n    NewGameInitPCItems();\n}\n"
        )
        (self.engine / "data" / "maps" / "LittlerootTown" / "scripts.inc").write_text(
            "LittlerootTown_Text_OurNewHomeLetsGoInside:\n"
            '    .string "Original introduction.$"\n'
            "LittlerootTown_Text_WaitPlayer:\n"
            '    .string "Wait!$"\n'
            "LittlerootTown_Text_TownSign:\n"
            '    .string "LITTLEROOT TOWN$"\n'
            "LittlerootTown_Text_ProfBirchsLab:\n"
            '    .string "The lab.$"\n'
            "LittlerootTown_Text_CanUsePCToStoreItems:\n"
            '    .string "The power of science is staggering!$"\n'
            "LittlerootTown_Text_BirchSpendsDaysInLab:\n"
            '    .string "Professor Birch studies Pokemon.$"\n'
            "LittlerootTown_Text_IfYouGoInGrassPokemonWillJumpOut:\n"
            '    .string "Wild Pokemon may jump out.$"\n'
        )

    def test_supplies_and_story_are_idempotent(self):
        for _ in range(2):
            module.apply(self.engine)
            module.apply_story(self.engine)
            module.apply_gothic_npcs(self.engine)
            module.apply_pink_rain(self.engine)
        code = (self.engine / "src" / "new_game.c").read_text()
        story = (self.engine / "data" / "maps" / "LittlerootTown" / "scripts.inc").read_text()
        self.assertEqual(code.count("AddBagItem(ITEM_RARE_CANDY, 999);"), 1)
        for name in module.BALL_ITEMS:
            self.assertEqual(code.count(f"AddBagItem(ITEM_{name}, 99);"), 1)
        self.assertEqual(story.count("MOM: Welcome to ROCKSTAR TOWN!"), 1)
        self.assertEqual(story.count("The neon heart of a new legend."), 1)
        self.assertIn("LittlerootTown_Text_ProfBirchsLab:", story)
        palette = (self.engine / "graphics" / "object_events" / "palettes" / "npc_1.pal").read_text().splitlines()
        self.assertEqual(len(palette), 19)
        self.assertEqual(palette[3 + 7], "8 8 24")
        self.assertEqual(palette[3 + 11], "222 222 230")
        weather_pal = (self.engine / "graphics" / "weather" / "fog.pal").read_text().splitlines()
        self.assertEqual(weather_pal[4], "246 123 180")
        rain_src = (self.engine / "src" / "field_weather_effect.c").read_text()
        self.assertEqual(rain_src.count("targetRainSpriteCount = 6;"), 1)


        self.assertEqual(story.count("The streetlights flickered again"), 1)
        self.assertEqual(story.count("PROF. BIRCH has been tracking"), 1)

    def test_unexpected_upstream_source_refused(self):
        (self.engine / "src" / "new_game.c").write_text("unrelated source")
        with self.assertRaises(RuntimeError):
            module.apply(self.engine)


if __name__ == "__main__":
    unittest.main()

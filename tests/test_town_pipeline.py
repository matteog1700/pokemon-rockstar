#!/usr/bin/env python3
"""Regression tests for the procedural Rockstar town planner and Emerald exporter."""
import importlib.util
import json
import struct
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from generate_town_plans import TOWNS, plan
from export_emerald_map import convert, encode

MAPPING = {
    "ground": {"metatile": 1, "collision": 0},
    "road": {"metatile": 2, "collision": 0},
    "building": {"metatile": 3, "collision": 1},
    "decor": {"metatile": 4, "collision": 1},
}

class TownGenerationTests(unittest.TestCase):
    def test_all_twelve_towns_have_distinct_names(self):
        self.assertEqual(len(TOWNS), 12)
        self.assertEqual(len({name for name, _ in TOWNS}), 12)

    def test_seeded_generation_is_reproducible(self):
        for name, theme in TOWNS:
            self.assertEqual(plan(name, theme, 20261111), plan(name, theme, 20261111))

    def test_different_seeds_change_layout(self):
        name, theme = TOWNS[0]
        self.assertNotEqual(plan(name, theme, 1)["tiles"], plan(name, theme, 2)["tiles"])

    def test_all_towns_export_with_verified_mapping(self):
        for name, theme in TOWNS:
            with self.subTest(town=name):
                town = plan(name, theme, 20261111)
                width, height = town["size"]
                data = convert(town, MAPPING)
                self.assertEqual(len(data), width * height * 2)
                words = struct.unpack("<" + "H" * (width * height), data)
                self.assertTrue(all(0 <= w <= 0xFFFF for w in words))
                cx, cy = width // 2, height // 2
                for x, y in ((cx, 0), (cx, height - 1), (0, cy), (width - 1, cy)):
                    self.assertEqual(words[y * width + x] & 0x3FF, 2)

    def test_export_rejects_unmapped_metatiles(self):
        town = plan(*TOWNS[0], 123)
        with self.assertRaises(ValueError):
            convert(town, {"ground": {"metatile": 1}})

    def test_export_rejects_blocked_connection(self):
        town = plan(*TOWNS[0], 123)
        cx = town["size"][0] // 2
        town["tiles"][0][cx] = "building"
        with self.assertRaises(ValueError):
            convert(town, MAPPING)

    def test_encoded_collision(self):
        self.assertEqual(encode(3, 1, 0), 0x403)
        with self.assertRaises(ValueError):
            encode(1024)

if __name__ == "__main__":
    unittest.main()

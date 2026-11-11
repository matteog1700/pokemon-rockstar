#!/usr/bin/env python3
"""Deterministic town layout planner for Pokémon Rockstar.

Outputs JSON planning layouts, NOT Emerald-compatible map binaries.
Use the plans as inputs for a later metatile-aware converter with collision,
warp and map-connection validation.
"""
import argparse
import hashlib
import json
import random
from pathlib import Path

TOWNS = [
    ("Peep Rockstar Town", "neon_gothic"),
    ("Too Poor Town", "neon_forest"),
    ("Ozzy Osbourne City", "gothic"),
    ("Kurt Cobain Town", "grunge"),
    ("Amy Winehouse Town", "gothic"),
    ("David Bowie City", "cyberpunk"),
    ("Freddie Mercury Town", "neon"),
    ("Jimi Hendrix Town", "psychedelic"),
    ("Chester Bennington Town", "industrial"),
    ("Mac Miller Town", "dreamy"),
    ("Juice WRLD Town", "neon"),
    ("XXXTentacion Town", "dark_forest"),
]
PALETTES = {
    "neon_gothic": ["violet", "cyan", "pink"],
    "neon_forest": ["lavender", "teal", "coral"],
    "gothic": ["indigo", "blue", "crimson"],
    "grunge": ["purple", "slate", "cyan"],
    "cyberpunk": ["electric_blue", "magenta", "violet"],
    "neon": ["hot_pink", "cyan", "gold"],
    "psychedelic": ["violet", "lime", "orange"],
    "industrial": ["slate", "purple", "red"],
    "dreamy": ["lilac", "cyan", "peach"],
    "dark_forest": ["midnight", "violet", "turquoise"],
}
BUILDINGS = ["shop", "healing_center", "house", "house", "venue", "studio"]
DECOR = ["tree", "flower", "lamp", "sign", "grave", "mushroom"]

def plan(name, theme, seed, width=32, height=24):
    digest = hashlib.sha256(f"{seed}:{name}".encode()).digest()
    rng = random.Random(int.from_bytes(digest[:8], "big"))
    grid = [["ground" for _ in range(width)] for _ in range(height)]
    cx, cy = width // 2, height // 2
    for y in range(height):
        for dx in (-1, 0, 1):
            grid[y][cx + dx] = "road"
    for x in range(width):
        for dy in (-1, 0, 1):
            grid[cy + dy][x] = "road"
    # Reserve the entire central cross as a guaranteed navigable backbone.
    occupied = set()
    buildings = []
    for kind in BUILDINGS:
        options = []
        for y in range(3, height - 5):
            for x in range(3, width - 6):
                cells = {(xx, yy) for yy in range(y, y + 4) for xx in range(x, x + 5)}
                if any(grid[yy][xx] == "road" for xx, yy in cells):
                    continue
                if cells & occupied:
                    continue
                # Door must face the central north-south road or east-west road.
                door = (x + 2, y + 4)
                if door[1] < height and grid[door[1]][door[0]] == "road":
                    options.append((x, y, door, cells))
        if not options:
            break
        x, y, door, cells = rng.choice(options)
        occupied.update(cells)
        for xx, yy in cells:
            grid[yy][xx] = "building"
        buildings.append({"kind": kind, "x": x, "y": y, "width": 5, "height": 4, "door": list(door)})
    decorations = []
    for _ in range(35):
        x, y = rng.randrange(1, width - 1), rng.randrange(1, height - 1)
        if grid[y][x] != "ground" or (x, y) in occupied:
            continue
        grid[y][x] = "decor"
        decorations.append({"kind": rng.choice(DECOR), "x": x, "y": y})
    return {
        "town": name, "theme": theme, "seed": seed, "palette": PALETTES[theme],
        "size": [width, height], "tiles": grid, "buildings": buildings,
        "decorations": decorations,
        "connections": {"north": [cx, 0], "south": [cx, height - 1],
                        "west": [0, cy], "east": [width - 1, cy]},
        "status": "planning_only_not_gba_map",
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=20261111)
    parser.add_argument("--output", type=Path, default=Path("generated/town_plans"))
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    manifest = []
    for index, (name, theme) in enumerate(TOWNS, 1):
        data = plan(name, theme, args.seed)
        filename = f"town_{index:02d}.json"
        (args.output / filename).write_text(json.dumps(data, indent=2) + "\n")
        manifest.append({"name": name, "theme": theme, "file": filename})
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"Generated {len(manifest)} deterministic town planning layouts in {args.output}")

if __name__ == "__main__":
    main()

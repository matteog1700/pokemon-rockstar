#!/usr/bin/env python3
"""Convert a seeded Rockstar town plan to a 16-bit Emerald map layout.

Requires an explicit mapping of logical tile types to registered metatile IDs.
This tool does NOT register tilesets, map headers, events, or connections.
"""
import argparse
import json
import struct
from pathlib import Path

TILE_KINDS = ("ground", "road", "building", "decor")
MAX_METATILE = 0x3FF
# Emerald map grid entries: metatile ID in bits 0-9, collision in bits 10-11,
# elevation in bits 12-15.
def encode(metatile, collision=0, elevation=0):
    if not 0 <= metatile <= MAX_METATILE:
        raise ValueError(f"Metatile ID out of range: {metatile}")
    if not 0 <= collision <= 3 or not 0 <= elevation <= 15:
        raise ValueError("Collision must be 0..3 and elevation 0..15")
    return metatile | (collision << 10) | (elevation << 12)

def convert(plan, mapping):
    width, height = plan["size"]
    grid = plan["tiles"]
    if not (1 <= width <= 255 and 1 <= height <= 255):
        raise ValueError("Unsupported dimensions")
    if len(grid) != height or any(len(row) != width for row in grid):
        raise ValueError("Nonrectangular tile grid")
    if any(kind not in mapping for kind in TILE_KINDS):
        raise ValueError("Mapping must define all four tile kinds")
    # Ensure all road entrances connect to the central intersection.
    cx, cy = width // 2, height // 2
    for x, y in ((cx, 0), (cx, height - 1), (0, cy), (width - 1, cy)):
        if grid[y][x] != "road":
            raise ValueError(f"Blocked road connection at {(x,y)}")
    out = bytearray()
    for row in grid:
        for kind in row:
            if kind not in TILE_KINDS:
                raise ValueError(f"Unknown tile type: {kind}")
            spec = mapping[kind]
            out.extend(struct.pack("<H", encode(int(spec["metatile"]), int(spec.get("collision", 0)), int(spec.get("elevation", 0)))))
    return bytes(out)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("plan", type=Path)
    p.add_argument("--mapping", type=Path, required=True, help="Verified registered tileset metatile mapping JSON")
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    plan = json.loads(args.plan.read_text())
    mapping = json.loads(args.mapping.read_text())
    payload = convert(plan, mapping)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(payload)
    print(f"Wrote {len(payload)} bytes of Emerald map grid data to {args.output}")
    print("NOTE: register this map layout, tilesets, connections and events in source before it is playable.")

if __name__ == "__main__":
    main()

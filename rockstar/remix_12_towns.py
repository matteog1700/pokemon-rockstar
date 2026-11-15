#!/usr/bin/env python3
"""Deterministic first-pass 12-town remix. Keep original warps, collision and story scripts intact."""
import argparse
import json
import random
from pathlib import Path

# These 12 working town slots reuse currently navigable Emerald maps.
# Names are design assignments, not claims of completed new geography.
TOWNS = (
    ("LittlerootTown", "Rockstar Town", "WEATHER_SUNNY_CLOUDS"),
    ("OldaleTown", "Neon City", "WEATHER_SHADE"),
    ("PetalburgCity", "Electric Forest Town", "WEATHER_RAIN"),
    ("RustboroCity", "Cyberpunk City", "WEATHER_FOG_HORIZONTAL"),
    ("LavaridgeTown", "Lava Rock City", "WEATHER_VOLCANIC_ASH"),
    ("DewfordTown", "Crystal Falls", "WEATHER_SUNNY_CLOUDS"),
    ("SlateportCity", "Midnight Harbor", "WEATHER_SHADE"),
    ("FallarborTown", "Phantom Town", "WEATHER_FOG_HORIZONTAL"),
    ("MauvilleCity", "Thunder Mountain", "WEATHER_RAIN_THUNDERSTORM"),
    ("LilycoveCity", "Starlight City", "WEATHER_SUNNY_CLOUDS"),
    ("VerdanturfTown", "Rainbow Paradise", "WEATHER_SUNNY"),
    ("EverGrandeCity", "Legendary Kingdom", "WEATHER_SUNNY_CLOUDS"),
)

# Standard civilian graphics: no children/quest-critical object identifiers are changed.
GOTHIC_NPC_GRAPHICS = (
    "OBJ_EVENT_GFX_BOY_1", "OBJ_EVENT_GFX_BOY_2", "OBJ_EVENT_GFX_BOY_3",
    "OBJ_EVENT_GFX_GIRL_1", "OBJ_EVENT_GFX_GIRL_2", "OBJ_EVENT_GFX_GIRL_3",
    "OBJ_EVENT_GFX_MAN_1", "OBJ_EVENT_GFX_MAN_2", "OBJ_EVENT_GFX_MAN_3",
    "OBJ_EVENT_GFX_WOMAN_1", "OBJ_EVENT_GFX_WOMAN_2", "OBJ_EVENT_GFX_WOMAN_3",
)

def apply_town_remix(engine: Path, seed: int = 1700) -> None:
    for town_index, (map_id, display, climate) in enumerate(TOWNS):
        path = engine / "data" / "maps" / map_id / "map.json"
        if not path.is_file():
            raise RuntimeError(f"Missing town source: {map_id}")
        original = path.read_text()
        record = json.loads(original)
        if record.get("name") != map_id:
            raise RuntimeError(f"Unexpected map name at {map_id}")
        record["weather"] = climate
        # Deterministically vary the appearance of generic civilian NPCs.
        # Never change object IDs, tile coords, map links, event scripts, or warp sites.
        rng = random.Random(seed + town_index * 101)
        for event in record.get("object_events", []):
            if event.get("local_id") or event.get("flag", "0") != "0":
                continue
            if event.get("graphics_id") in GOTHIC_NPC_GRAPHICS and event.get("trainer_type") == "TRAINER_TYPE_NONE":
                event["graphics_id"] = rng.choice(GOTHIC_NPC_GRAPHICS)
        rendered = json.dumps(record, ensure_ascii=False, indent=2) + "\n"
        if original != rendered:
            path.write_text(rendered)
        print(f"{display}: mapped to {map_id}; themed weather and deterministic civilian variants")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("engine", type=Path)
    parser.add_argument("--seed", type=int, default=1700)
    args = parser.parse_args()
    apply_town_remix(args.engine, args.seed)

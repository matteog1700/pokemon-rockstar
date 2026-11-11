#!/usr/bin/env python3
"""Apply first functional Pokemon Rockstar gameplay changes to a pinned pokeemerald checkout.

Idempotent and fail-closed: refuse an unexpected upstream source layout.
No original ROM files or copyrighted binaries are required.
"""
import argparse
from pathlib import Path

BALL_ITEMS = (
    "MASTER_BALL", "ULTRA_BALL", "GREAT_BALL", "POKE_BALL",
    "SAFARI_BALL", "NET_BALL", "DIVE_BALL", "NEST_BALL",
    "REPEAT_BALL", "TIMER_BALL", "LUXURY_BALL", "PREMIER_BALL",
)
MARKER = "/* POKEMON ROCKSTAR STARTER SUPPLIES */"


def apply(engine: Path) -> None:
    source = engine / "src" / "new_game.c"
    items = engine / "include" / "constants" / "items.h"
    if not source.is_file() or not items.is_file():
        raise RuntimeError("Expected pokeemerald source files were not found")
    item_header = items.read_text()
    for name in (*BALL_ITEMS, "RARE_CANDY"):
        if f"ITEM_{name}" not in item_header:
            raise RuntimeError(f"Upstream item ID missing: ITEM_{name}")
    original = source.read_text()
    if MARKER in original:
        print("Rockstar supplies already applied")
        return
    anchor = "    ClearBag();\n    NewGameInitPCItems();"
    if original.count(anchor) != 1:
        raise RuntimeError("NewGameInitData item initialization differs from expected upstream")
    grants = [f"    AddBagItem(ITEM_{name}, 99);" for name in BALL_ITEMS]
    addition = (
        anchor + "\n    " + MARKER +
        "\n    // Fresh saves only; existing player save data is untouched.\n" +
        "    // The original bag can split quantities across several item slots.\n" +
        "    AddBagItem(ITEM_RARE_CANDY, 999);\n" +
        "\n".join(grants) +
        "\n    /* POKEMON ROCKSTAR END STARTER SUPPLIES */"
    )
    source.write_text(original.replace(anchor, addition, 1))
    print("Applied Rockstar new-game supplies: 999 Rare Candies and 99 of 12 Poke Ball kinds.")



def apply_story(engine: Path) -> None:
    """Introduce Rockstar Town and the region's mystery in actual GBA map dialogue."""
    source = engine / "data" / "maps" / "LittlerootTown" / "scripts.inc"
    if not source.is_file():
        raise RuntimeError("Expected first-town script was not found")
    original = source.read_text()
    if "MOM: Welcome to ROCKSTAR TOWN!" in original:
        print("Rockstar opening already applied")
        return
    start_label = "LittlerootTown_Text_OurNewHomeLetsGoInside:"
    end_label = "LittlerootTown_Text_WaitPlayer:"
    if original.count(start_label) != 1 or original.count(end_label) != 1:
        raise RuntimeError("Opening dialogue labels differ from expected upstream")
    start = original.index(start_label)
    end = original.index(end_label, start)
    introduction = r'''LittlerootTown_Text_OurNewHomeLetsGoInside:
    .string "MOM: Welcome to ROCKSTAR TOWN!\p"
    .string "Every night the streets glow\l"
    .string "with pink and violet light.\p"
    .string "People say a strange signal has\l"
    .string "been waking legendary POKéMON.\p"
    .string "Somewhere past the neon skyline,\l"
    .string "a hidden story is waiting for you.\p"
    .string "Come on, {PLAYER}!\l"
    .string "Let's make this our new home.$"

'''
    updated = original[:start] + introduction + original[end:]
    sign_start = 'LittlerootTown_Text_TownSign:\n'
    sign_end = '\nLittlerootTown_Text_ProfBirchsLab:'
    if updated.count(sign_start) != 1 or updated.count(sign_end) != 1:
        raise RuntimeError("First town sign labels differ from expected upstream")
    a = updated.index(sign_start)
    b = updated.index(sign_end, a)
    sign = r'''LittlerootTown_Text_TownSign:
    .string "ROCKSTAR TOWN\l"
    .string "The neon heart of a new legend.$"
'''
    updated = updated[:a] + sign + updated[b:]

    # Rework the two free-roaming NPCs into early story witnesses.
    start_npc = "LittlerootTown_Text_CanUsePCToStoreItems:"
    end_npc = "LittlerootTown_Text_IfYouGoInGrassPokemonWillJumpOut:"
    if updated.count(start_npc) != 1 or updated.count(end_npc) != 1:
        raise RuntimeError("Rockstar Town NPC dialogue labels differ from upstream")
    a = updated.index(start_npc)
    b = updated.index(end_npc, a)
    witnesses = r'''LittlerootTown_Text_CanUsePCToStoreItems:
    .string "The streetlights flickered again\l"
    .string "last night. That signal is back!\p"
    .string "My POKéMON won't go near the\l"
    .string "old radio tower.$"

LittlerootTown_Text_BirchSpendsDaysInLab:
    .string "PROF. BIRCH has been tracking\l"
    .string "strange POKéMON cries at night.\p"
    .string "They say the sound is coming\l"
    .string "from beyond ROCKSTAR TOWN.$"

'''
    updated = updated[:a] + witnesses + updated[b:]

    source.write_text(updated)
    print("Applied Rockstar Town opening, sign and two NPC story hints.")


# Shared human-NPC palettes in Emerald. Player, rival, Pokemon, and special
# character palettes are left untouched so bespoke Rockstar sprites can follow.
GOTHIC_COLORS = (
    (115, 197, 164),  # transparent background; preserved on apply
    (255, 213, 180),  # skin highlights; preserved on apply
    (255, 197, 148),
    (222, 148, 115),
    (123, 65, 65),
    (65, 65, 82),     # gothic cloth mid-tone / shadow
    (32, 32, 49),     # jacket dark
    (8, 8, 24),       # near-black
    (180, 139, 213),  # neon violet trim
    (115, 65, 156),   # violet shadow
    (41, 16, 65),     # violet near-black
    (222, 222, 230), # silver chain / hardware highlight
    (148, 148, 164), # silver mid-tone
    (65, 65, 82),    # hardware shadows
    (255, 255, 255),
    (0, 0, 0),
)


def apply_gothic_npcs(engine: Path) -> None:
    """Palette pass for shared background NPCs; retains GBA 16-color format."""
    directory = engine / "graphics" / "object_events" / "palettes"
    if not directory.is_dir():
        raise RuntimeError("NPC palette directory missing from Emerald source")
    changed = 0
    for num in range(1, 5):
        for reflection in ("", "_reflection"):
            path = directory / f"npc_{num}{reflection}.pal"
            if not path.is_file():
                raise RuntimeError(f"Missing expected NPC palette: {path.name}")
            lines = path.read_text().splitlines()
            if lines[:3] != ["JASC-PAL", "0100", "16"] or len(lines) != 19:
                raise RuntimeError(f"Unexpected GBA palette: {path.name}")
            original = [tuple(map(int, row.split())) for row in lines[3:]]
            if len(original) != 16 or any(len(rgb) != 3 for rgb in original):
                raise RuntimeError(f"Invalid NPC palette: {path.name}")
            if reflection:
                # Reflections remain tinted and dimmer to fit water lighting.
                colors = list(original[:5]) + [
                    tuple(min(255, int(value * 0.68 + (28 if idx == 2 else 5))) for idx, value in enumerate(rgb))
                    for rgb in GOTHIC_COLORS[5:14]
                ] + list(original[14:])
            else:
                colors = list(original[:5]) + list(GOTHIC_COLORS[5:14]) + list(original[14:])
            data = "\n".join(lines[:3] + [f"{r} {g} {b}" for r, g, b in colors]) + "\n"
            if path.read_text() != data:
                path.write_text(data)
                changed += 1
    print(f"Applied gothic black, silver-chain and violet NPC palette theme: {changed} changed files.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("engine", type=Path)
    engine = parser.parse_args().engine
    apply(engine)
    apply_story(engine)
    apply_gothic_npcs(engine)

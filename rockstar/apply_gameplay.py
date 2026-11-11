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


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("engine", type=Path)
    apply(parser.parse_args().engine)

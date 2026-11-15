#!/usr/bin/env python3
"""Correct the actual New Game character choice in Emerald.

Shows 'LIL PEEP' and 'TOO POOR' as the selectable options, and replaces
Professor Ozzy's obsolete "boy or girl" question. The underlying MALE/FEMALE
save identifiers are retained for engine compatibility. This patch affects
the labels, not the sprite pixels (tracked separately).
"""
import argparse
from pathlib import Path

def change_once(s, old, new, where):
    if s.count(old) != 1:
        raise RuntimeError(f"Missing or ambiguous {where}: {s.count(old)} matches")
    return s.replace(old, new, 1)

def apply(engine: Path):
    main=engine/"src"/"main_menu.c"
    speech=engine/"data"/"text"/"birch_speech.inc"
    s=main.read_text()
    s=change_once(
        s,
        '''static const struct MenuAction sMenuActions_Gender[] = {
    {gText_BirchBoy, {NULL}},
    {gText_BirchGirl, {NULL}}
};''',
        '''/* ROCKSTAR CHARACTER SELECT: preserve save IDs, change player choices. */
static const u8 sRockstarLilPeep[] = _("LIL PEEP");
static const u8 sRockstarTooPoor[] = _("TOO POOR");
static const struct MenuAction sMenuActions_Gender[] = {
    {sRockstarLilPeep, {NULL}},
    {sRockstarTooPoor, {NULL}}
};''',
        "New Game choice labels")
    # The 6-tile window fits BOY/GIRL, but not the two musician names.
    # Expand its tile width; move the following window's tile allocation to
    # avoid VRAM tile overlap after expansion.
    s=change_once(
        s,
        '''        .tilemapLeft = 3,
        .tilemapTop = 5,
        .width = 6,
        .height = 4,
        .paletteNum = 15,
        .baseBlock = 0x6D''',
        '''        .tilemapLeft = 3,
        .tilemapTop = 5,
        .width = 11,
        .height = 4,
        .paletteNum = 15,
        .baseBlock = 0x6D''',
        "choice window size")
    s=change_once(s,
        '''        .width = 9,
        .height = 10,
        .paletteNum = 15,
        .baseBlock = 0x85''',
        '''        .width = 9,
        .height = 10,
        .paletteNum = 15,
        .baseBlock = 0xA0''',
        "following window VRAM allocation")
    main.write_text(s)
    text=speech.read_text()
    text=change_once(text,
        '''gText_Birch_BoyOrGirl::
    .string "Are you a boy?\\n"
    .string "Or are you a girl?$"''',
        '''gText_Birch_BoyOrGirl::
    .string "Who will be our ROCKSTAR?\\p"
    .string "LIL PEEP or TOO POOR?$"''',
        "Professor Ozzy choice question")
    speech.write_text(text)
    print("Character choice now shows LIL PEEP / TOO POOR with matching Ozzy dialogue and expanded menu width.")

if __name__ == "__main__":
    p=argparse.ArgumentParser()
    p.add_argument("engine",type=Path)
    apply(p.parse_args().engine)

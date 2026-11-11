#!/usr/bin/env python3
"""Rockstar polish: Ozzy speech, Rayquaza reveal, dark red menus and neon kaleidoscope.

Source-level GBA changes: no proprietary audio or downloaded ROMs.
"""
from pathlib import Path
import argparse

KALEIDO_MARKER = "/* ROCKSTAR KALEIDOSCOPIC INTRO */"

KALEIDO = r'''
/* ROCKSTAR KALEIDOSCOPIC INTRO */
/* Symmetric slowly turning jewel motifs; no hard strobe flashes. */
static void RockstarKaleidoJewels(u16 frames)
{
    s16 i, center, x, y, radius, dx, dy;
    u8 phase = (frames / 12) % 16;
    u16 rose = RGB(17 + (phase % 8), 4 + (phase / 4), 22);
    u16 blue = RGB(7, 14 + (phase % 7), 27);
    u16 lavender = RGB(19, 8, 24);
    for (center = 0; center < 2; center++)
    {
        s16 cx = center ? 209 : 30;
        s16 cy = center ? 101 : 101;
        for (i = 0; i < 6; i++)
        {
            radius = 7 + i * 4 + phase / 4;
            for (dx = -radius; dx <= radius; dx++)
            {
                dy = radius - (dx < 0 ? -dx : dx);
                x = cx + dx;
                y = cy + dy;
                RockstarPutRect(x, y, 1, 1, (i & 1) ? blue : rose);
                RockstarPutRect(x, cy - dy, 1, 1, (i & 1) ? blue : rose);
                if (i & 1)
                {
                    RockstarPutRect(cx + dy, cy + dx, 1, 1, lavender);
                    RockstarPutRect(cx - dy, cy + dx, 1, 1, lavender);
                }
            }
        }
    }
}
/* END ROCKSTAR KALEIDOSCOPIC INTRO */
'''

TEXT = r'''gText_Birch_Welcome::
    .string "The lights are calling you...\p"
    .string "Welcome to POKéMON ROCKSTAR!\p"
    .string "I'm PROF. OZZY.\p"
    .string "They say I know the secrets of\l"
    .string "the midnight POKéMON.\p"
    .string "$"

gText_Birch_Pokemon::
    .string "Meet RAYQUAZA, a legendary\l"
    .string "guardian of the skies!\p"
    .string "$"

gText_Birch_MainSpeech::
    .string "Twelve neon towns hold twelve\l"
    .string "notes from a lost melody.\p"
    .string "A mysterious signal has awakened\l"
    .string "the legendary POKéMON.\p"
    .string "Some seek their power. Others\l"
    .string "would silence every song.\p"
    .string "Your journey starts in\l"
    .string "ROCKSTAR TOWN.\p"
    .string "Find the NEON NOTES and bring\l"
    .string "the music back to this world!\p"
    .string "$"

gText_Birch_AndYouAre::
    .string "And you are?$"

gText_Birch_BoyOrGirl::
    .string "Are you a boy?\n"
    .string "Or are you a girl?$"

gText_Birch_WhatsYourName::
    .string "Tell me your name.$"

gText_Birch_SoItsPlayer::
    .string "So it's {PLAYER}{KUN}?$"

gText_Birch_YourePlayer::
    .string "Ah, {PLAYER}!\p"
    .string "You're moving to ROCKSTAR TOWN,\l"
    .string "where the first note awaits!\p"
    .string "$"

gText_Birch_AreYouReady::
    .string "Ready to follow the music?\p"
    .string "The rain falls pink over the\l"
    .string "midnight streets.\p"
    .string "Trust your POKéMON, face the\l"
    .string "darkness, and find your voice!\p"
    .string "I'll see you in my lab.\p"
    .string "$"
'''

def apply_palette(path: Path, colors: list[tuple[int,int,int]], preserve_first=False):
    rows = path.read_text().splitlines()
    if rows[:3] != ["JASC-PAL", "0100", "16"] or len(rows) != 19:
        raise RuntimeError(f"Unexpected palette data: {path}")
    original = [tuple(map(int,row.split())) for row in rows[3:]]
    if preserve_first:
        colors = [original[0], *colors[1:]]
    if len(colors) != 16:
        raise RuntimeError("Expected 16-color palette")
    path.write_text("\n".join(["JASC-PAL","0100","16"]+["%d %d %d"%rgb for rgb in colors])+"\n")

MAIN_BG = [
    (0,0,0), (255,255,255), (32,1,5), (81,3,13),
    (8,0,0), (115,8,22), (203,18,43), (156,13,34),
    (175,15,35), (42,0,6), (98,8,20), (49,1,10),
    (130,7,30), (187,12,38), (222,26,48), (255,52,83)
]
MAIN_TEXT = [
    (255,255,255), (255,255,255), (182,182,182), (237,237,237),
    (255,18,48), (255,138,146), (85,5,13), (206,68,73),
    (181,13,40), (241,118,126), (0,0,0), (0,0,0),
    (0,0,0), (0,0,0), (0,0,0), (0,0,0)
]
SPEECH_BG = [
    (0,0,0), (255,255,255), (244,207,217), (215,149,170),
    (186,101,128), (150,59,87), (110,28,47), (75,9,23),
    (48,4,13), (204,72,101), (180,41,73), (150,19,51),
    (120,10,40), (91,7,31), (61,4,20), (0,0,0)
]
SPEECH_GRAD = [
    (250,202,208), (234,159,171), (204,113,133), (171,72,98),
    (136,44,73), (102,25,50), (69,11,31), (35,4,13),
    (0,0,0), (0,0,0), (0,0,0), (0,0,0),
    (0,0,0), (0,0,0), (0,0,0), (0,0,0)
]

def apply(engine: Path):
    main = engine / "src" / "main_menu.c"
    intro = engine / "src" / "intro.c"
    dialogue = engine / "data" / "text" / "birch_speech.inc"
    if not (main.exists() and intro.exists() and dialogue.exists()):
        raise RuntimeError("Missing pinned Emerald new game / intro source")
    s = main.read_text()
    for old in ("SPECIES_LOTAD",):
        if s.count(old) != 2:
            raise RuntimeError(f"Expected 2 legendary-reveal species references, got {s.count(old)}")
        s = s.replace(old, "SPECIES_RAYQUAZA")
    # Dark, legible text on game introduction windows; main-menu palette assets
    # below supply red accents to the New Game / Continue / Options selection.
    main.write_text(s)
    original = dialogue.read_text()
    if not original.startswith("gText_Birch_Welcome::"):
        raise RuntimeError("Unexpected professor speech")
    dialogue.write_text(TEXT)
    palettes = engine / "graphics"
    apply_palette(palettes / "interface" / "main_menu_bg.pal", MAIN_BG)
    apply_palette(palettes / "interface" / "main_menu_text.pal", MAIN_TEXT)
    apply_palette(palettes / "birch_speech" / "bg0.pal", SPEECH_BG)
    apply_palette(palettes / "birch_speech" / "bg1.pal", SPEECH_BG)
    apply_palette(palettes / "birch_speech" / "bg2.pal", SPEECH_GRAD)
    code = intro.read_text()
    if "/* POKEMON ROCKSTAR GOTHIC OPENING */" not in code:
        raise RuntimeError("Apply Rockstar gothic opening before psychedelic effects")
    if KALEIDO_MARKER not in code:
        anchor = "static void Task_RockstarGothicMovie(u8 taskId)\n{"
        if code.count(anchor) != 1:
            raise RuntimeError("Missing native intro movie task")
        code = code.replace(anchor, KALEIDO + "\n" + anchor, 1)
        # Place the kaleidoscope away from center lettering and animate gently.
        needle = "    if (data[0]++ >= 340)"
        if code.count(needle) != 1:
            raise RuntimeError("Missing intro frame counter")
        code = code.replace(needle,
            "    if ((data[0] & 15) == 0 && data[0] < 340)\n"
            "        RockstarKaleidoJewels(data[0]);\n"
            + needle, 1)
        intro.write_text(code)
    print("Rockstar: Ozzy professor dialogue, legendary Rayquaza, red-black menus, kaleidoscopic film.")

if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("engine",type=Path)
    apply(parser.parse_args().engine)

#!/usr/bin/env python3
"""Replace Emerald's Rayquaza title screen and music with a native Rockstar screen.

The title artwork is rendered with direct 240x160 GBA pixels. Its logo shares
the refined custom font from the introductory movie; it is not a recolor of
the original Emerald title. The separate soundtrack is an original MIDI.
"""
from pathlib import Path
import argparse
import struct
from apply_intro import CINEMATIC, midi_track

MARKER = "/* POKEMON ROCKSTAR CUSTOM TITLE SCREEN */"

# Reuse the custom GBA pixel primitives and gothic skyline from the movie.
# Source ends before the intro-only task handler.
ART = CINEMATIC[CINEMATIC.index("static const u8 sRockstarFont"):CINEMATIC.index("static void Task_RockstarGothicMovie")]
TITLE = r'''
/* POKEMON ROCKSTAR CUSTOM TITLE SCREEN */
/* Original neon-gothic home screen, built for Mode 3 on actual GBA hardware. */
static void CB2_RockstarTitle(void)
{
    static u16 frame = 0;
    if (gMain.state == 0)
    {
        SetVBlankCallback(NULL);
        SetGpuReg(REG_OFFSET_DISPCNT, 0);
        SetGpuReg(REG_OFFSET_BLDCNT, 0);
        ResetTasks();
        ResetSpriteData();
        ResetPaletteFade();
        RockstarPaintScene(2);
        RockstarPutRect(39, 129, 162, 13, RGB(1, 1, 3));
        RockstarPutText(85, 131, 1, "PRESS START", RGB(17, 27, 30));
        SetGpuReg(REG_OFFSET_DISPCNT, DISPCNT_MODE_3 | DISPCNT_BG2_ON);
        m4aSongNumStart(MUS_TITLE); /* Replaced by original Rockstar title MIDI. */
        frame = 0;
        gMain.state = 1;
        return;
    }
    if (JOY_NEW(A_BUTTON) || JOY_NEW(START_BUTTON))
    {
        FadeOutBGM(4);
        SetMainCallback2(CB2_InitMainMenu);
        return;
    }
    if (JOY_HELD(CLEAR_SAVE_BUTTON_COMBO) == CLEAR_SAVE_BUTTON_COMBO)
    {
        SetMainCallback2(CB2_InitClearSaveDataScreen);
        return;
    }
    if (JOY_HELD(RESET_RTC_BUTTON_COMBO) == RESET_RTC_BUTTON_COMBO
      && CanResetRTC() == TRUE)
    {
        SetMainCallback2(CB2_InitResetRtcScreen);
        return;
    }
    if (JOY_HELD(BERRY_UPDATE_BUTTON_COMBO) == BERRY_UPDATE_BUTTON_COMBO)
    {
        SetMainCallback2(CB2_InitBerryFixProgram);
        return;
    }
    frame++;
    /* Neon cyan and rose shimmer around PRESS START. */
    if ((frame & 15) == 0)
    {
        u16 glow = (frame & 16) ? RGB(23, 7, 25) : RGB(5, 22, 27);
        RockstarPutRect(31, 144, 178, 1, glow);
        RockstarPutRect(31, 126, 178, 1, glow);
    }
    /* Sparse falling-rain particles, updated without interrupt callbacks. */
    if ((frame & 7) == 0)
    {
        s16 x = (frame * 37 / 8) % 238;
        s16 y = (frame * 11 / 8) % 56;
        RockstarPutRect(x, y, 1, 5, RGB(17, 5, 21));
    }
}
'''

def title_midi() -> bytes:
    """Original D-minor synth-metal title theme (no third-party recordings)."""
    conductor = [
        (0, 0, b"\xff\x51\x03\x07\x44\x1f"),  # 130 bpm
        (0, 1, b"\xff\x58\x04\x04\x02\x18\x08"),
    ]
    lead = [(0, 0, bytes([0xc0, 81]))]  # saw lead
    guitar = [(0, 0, bytes([0xc1, 30]))]  # distorted guitar
    bass = [(0, 0, bytes([0xc2, 33]))]
    drums = []
    ppq = 96

    def note(track, channel, pitch, pos, duration, velocity):
        track.append((pos, 2, bytes([0x90 | channel, pitch, velocity])))
        track.append((pos + duration, 1, bytes([0x80 | channel, pitch, 0])))

    # Hand-composed riff and counterline; not a sample or song transcription.
    melody = (
        (62, 65, 69, 72, 74, 72, 69, 65),
        (60, 62, 65, 69, 72, 69, 65, 62),
        (58, 62, 65, 69, 70, 69, 65, 62),
        (60, 64, 67, 69, 72, 69, 67, 64),
    )
    roots = (38, 34, 31, 36)  # Dm, Bb, Gm, C
    for repeat in range(3):
        for bar in range(4):
            t = (repeat * 4 + bar) * 384
            root = roots[bar]
            for beat in range(4):
                base = t + beat * 96
                note(bass, 2, root, base, 82, 88)
                note(guitar, 1, root + 12, base, 70, 71)
                note(guitar, 1, root + 19, base, 70, 66)
                note(drums, 9, 36 if beat in (0, 2) else 38, base, 14, 74)
                for half in (0, 48):
                    note(drums, 9, 42, base + half, 12, 42)
            for i, pitch in enumerate(melody[bar]):
                note(lead, 0, pitch, t + i * 48, 43, 76 if i % 2 == 0 else 62)
    tracks = [midi_track(t) for t in (conductor, lead, guitar, bass, drums)]
    return b"MThd" + struct.pack(">IHHH", 6, 1, len(tracks), ppq) + b"".join(tracks)


def apply(engine: Path) -> None:
    source = engine / "src" / "title_screen.c"
    if not source.is_file():
        raise RuntimeError("Expected Emerald title_screen.c was not found")
    code = source.read_text()
    anchor = "void CB2_InitTitleScreen(void)\n{"
    if code.count(anchor) != 1:
        raise RuntimeError("Unexpected Emerald title screen entry point")
    if MARKER not in code:
        # Save original functions for dependency compatibility. The title entry
        # now always runs our new callback and never initializes Rayquaza assets.
        code = code.replace(anchor,
            "static void CB2_RockstarTitle(void);\n"
            + ART + TITLE + "\n"
            + anchor.replace("{", "{\n    SetMainCallback2(CB2_RockstarTitle);\n    return;"),
            1)
        source.write_text(code)
    elif "SetMainCallback2(CB2_RockstarTitle);" not in code:
        raise RuntimeError("Incomplete custom Rockstar title patch")
    midi = engine / "sound" / "songs" / "midi" / "mus_title.mid"
    if not midi.is_file():
        raise RuntimeError("Expected original Emerald title song is missing")
    midi.write_bytes(title_midi())
    print("Installed custom Rockstar title screen and newly composed D-minor rock MIDI.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("engine", type=Path)
    args = parser.parse_args()
    apply(args.engine)

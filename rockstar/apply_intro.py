#!/usr/bin/env python3
"""Install original GBA-native Pokemon Rockstar animated intro and original MIDI theme.

Replaces the existing Game Freak introduction path (after copyright) with a
three-act Mode 3 pixel-art cinematic. No copyrighted song recordings included.
"""
from pathlib import Path
import argparse
import struct

MARKER = "/* POKEMON ROCKSTAR GOTHIC OPENING */"
CINEMATIC = r'''
/* POKEMON ROCKSTAR GOTHIC OPENING */
/* A native GBA Mode-3 cinematic: moon, rain, gothic skyline and neon wordmarks.
 * Original pixel art drawn by the game, not a video file or original Game Freak sequence.
 */
static const u8 sRockstarFont[26][5] = {
    {0x7E,0x11,0x11,0x11,0x7E}, {0x7F,0x49,0x49,0x49,0x36},
    {0x3E,0x41,0x41,0x41,0x22}, {0x7F,0x41,0x41,0x22,0x1C},
    {0x7F,0x49,0x49,0x49,0x41}, {0x7F,0x09,0x09,0x09,0x01},
    {0x3E,0x41,0x49,0x49,0x7A}, {0x7F,0x08,0x08,0x08,0x7F},
    {0x41,0x41,0x7F,0x41,0x41}, {0x20,0x40,0x41,0x3F,0x01},
    {0x7F,0x08,0x14,0x22,0x41}, {0x7F,0x40,0x40,0x40,0x40},
    {0x7F,0x02,0x0C,0x02,0x7F}, {0x7F,0x04,0x08,0x10,0x7F},
    {0x3E,0x41,0x41,0x41,0x3E}, {0x7F,0x09,0x09,0x09,0x06},
    {0x3E,0x41,0x51,0x21,0x5E}, {0x7F,0x09,0x19,0x29,0x46},
    {0x46,0x49,0x49,0x49,0x31}, {0x01,0x01,0x7F,0x01,0x01},
    {0x3F,0x40,0x40,0x40,0x3F}, {0x1F,0x20,0x40,0x20,0x1F},
    {0x7F,0x20,0x18,0x20,0x7F}, {0x63,0x14,0x08,0x14,0x63},
    {0x07,0x08,0x70,0x08,0x07}, {0x61,0x51,0x49,0x45,0x43}
};

static void RockstarPutRect(s16 x, s16 y, s16 w, s16 h, u16 color)
{
    s16 row, col;
    volatile u16 *pixels = (volatile u16 *)VRAM;
    for (row = y; row < y + h; row++)
    {
        if (row < 0 || row >= 160)
            continue;
        for (col = x; col < x + w; col++)
            if (col >= 0 && col < 240)
                pixels[row * 240 + col] = color;
    }
}

static void RockstarPutText(s16 x, s16 y, u8 scale, const char *message, u16 color)
{
    s16 start = x;
    u8 col, row, dx, dy;
    while (*message)
    {
        char letter = *message++;
        if (letter == ' ')
        {
            x += 6 * scale;
            continue;
        }
        if (letter < 'A' || letter > 'Z')
            continue;
        for (col = 0; col < 5; col++)
            for (row = 0; row < 7; row++)
                if ((sRockstarFont[letter - 'A'][col] & (1 << row)) != 0)
                    for (dx = 0; dx < scale; dx++)
                        for (dy = 0; dy < scale; dy++)
                            RockstarPutRect(x + col * scale + dx, y + row * scale + dy, 1, 1, color);
        x += 6 * scale;
        if (x > 240 - 5 * scale)
            x = start;  /* Avoid writing past video memory on malformed text. */
    }
}

static void RockstarPaintScene(u8 scene)
{
    s16 x, y, height, i;
    u16 color;
    u32 randomValue = 1700 + 3109 * scene;
    volatile u16 *pixels = (volatile u16 *)VRAM;
    for (y = 0; y < 160; y++)
    {
        u8 red = scene == 1 ? 2 : 1;
        u8 blue = scene == 1 ? 9 - y / 28 : 7 - y / 34;
        if (blue < 1)
            blue = 1;
        if (y < 72)
            red += (72 - y) / 28;
        color = RGB(red, 0, blue);
        for (x = 0; x < 240; x++)
            pixels[y * 240 + x] = color;
    }

    for (i = 0; i < 90; i++)
    {
        randomValue = randomValue * 1664525 + 1013904223;
        x = (randomValue >> 14) % 240;
        randomValue = randomValue * 1664525 + 1013904223;
        y = (randomValue >> 17) % 100;
        RockstarPutRect(x, y, 1, 1, RGB(15, 9, 25));
    }

    /* Rose-colored moon with a bright neon halo. */
    for (y = -19; y <= 19; y++)
        for (x = -19; x <= 19; x++)
            if (x * x + y * y < 361)
                RockstarPutRect(198 + x, 34 + y, 1, 1,
                    x * x + y * y < 240 ? RGB(28, 8, 18) : RGB(17, 3, 20));

    /* Gothic towers, glowing windows and rooftop spires. */
    for (i = 0; i < 14; i++)
    {
        height = 31 + (i * 37 + scene * 11) % 52;
        x = i * 19 - 4;
        RockstarPutRect(x, 133 - height, 17, height + 29, RGB(1, 1, 4));
        RockstarPutRect(x + 3, 139 - height, 2, 3, RGB(28, 3, 22));
        RockstarPutRect(x + 11, 149 - height, 2, 3, RGB(5, 20, 24));
        RockstarPutRect(x + 8, 122 - height, 1, 14, RGB(10, 2, 14));
        RockstarPutRect(x + 5, 125 - height, 7, 1, RGB(15, 3, 17));
    }
    RockstarPutRect(0, 140, 240, 20, RGB(1, 1, 3));
    RockstarPutRect(0, 139, 240, 1, RGB(22, 3, 19));
    /* Rose-tinted falling rain. */
    for (i = 0; i < 50; i++)
    {
        randomValue = randomValue * 1664525 + 1013904223;
        x = (randomValue >> 17) % 240;
        randomValue = randomValue * 1664525 + 1013904223;
        y = (randomValue >> 16) % 130;
        RockstarPutRect(x, y, 1, 5, RGB(21, 5, 22));
    }

    if (scene == 0)
    {
        RockstarPutRect(12, 49, 218, 2, RGB(27, 4, 21));
        RockstarPutText(78, 12, 2, "POKEMON", RGB(22, 14, 29));
        RockstarPutText(24, 61, 4, "ROCKSTAR", RGB(31, 6, 21));
        RockstarPutText(56, 110, 1, "THE SIGNAL AWAKENS", RGB(21, 20, 29));
    }
    else if (scene == 1)
    {
        RockstarPutRect(0, 51, 240, 2, RGB(5, 27, 29));
        RockstarPutText(23, 57, 2, "TWELVE NEON", RGB(25, 5, 25));
        RockstarPutText(75, 79, 2, "NOTES", RGB(29, 12, 24));
        RockstarPutText(38, 112, 1, "THE NIGHT HAS A VOICE", RGB(16, 28, 29));
    }
    else
    {
        RockstarPutRect(10, 47, 220, 2, RGB(26, 6, 26));
        RockstarPutText(78, 14, 2, "POKEMON", RGB(24, 12, 31));
        RockstarPutText(24, 57, 4, "ROCKSTAR", RGB(31, 7, 22));
        RockstarPutText(48, 112, 1, "YOUR LEGEND BEGINS", RGB(18, 27, 29));
    }
}

static void Task_RockstarGothicMovie(u8 taskId)
{
    s16 *data = gTasks[taskId].data;
    if (data[0] == 0)
    {
        SetVBlankCallback(NULL);
        IntroResetGpuRegs();
        SetGpuReg(REG_OFFSET_DISPCNT, DISPCNT_MODE_3 | DISPCNT_BG2_ON);
        RockstarPaintScene(0);
        m4aSongNumStart(MUS_INTRO);  /* Replaced by our original rock MIDI. */
        ResetSerial();
    }
    if (data[0] == 110)
        RockstarPaintScene(1);
    if (data[0] == 220)
        RockstarPaintScene(2);
    if (data[0]++ >= 340)
    {
        DestroyTask(taskId);
        SetMainCallback2(MainCB2_EndIntro);
    }
}
/* END POKEMON ROCKSTAR GOTHIC OPENING */
'''

def midi_vlq(value: int) -> bytes:
    seq = [value & 0x7f]
    value >>= 7
    while value:
        seq.insert(0, 0x80 | (value & 0x7f))
        value >>= 7
    return bytes(seq)


def midi_track(events: list[tuple[int, int, bytes]]) -> bytes:
    events = sorted(events, key=lambda e: (e[0], e[1]))
    prev = 0
    out = bytearray()
    for pos, _, msg in events:
        out.extend(midi_vlq(pos - prev))
        out.extend(msg)
        prev = pos
    out.extend(b"\x00\xff\x2f\x00")
    return b"MTrk" + struct.pack(">I", len(out)) + bytes(out)


def compose_intro() -> bytes:
    """Original E-minor gothic rock theme; original melodies and chord progression."""
    ppq = 96
    conductor = [
        (0, 0, b"\xff\x51\x03\x08\x97\x05"),  # ~140 BPM
        (0, 1, b"\xff\x58\x04\x04\x02\x18\x08"),
    ]
    melody = [(0, 0, bytes([0xc0, 48]))]  # ensemble strings
    guitar = [(0, 0, bytes([0xc1, 30]))]  # guitar-like synth patch
    bass = [(0, 0, bytes([0xc2, 32]))]
    drums = []

    def note(track, channel, pitch, at, dur, vel):
        track.append((at, 2, bytes([0x90 | channel, pitch, vel])))
        track.append((at + dur, 1, bytes([0x80 | channel, pitch, 0])))

    # Distinct, newly composed melody rather than a transcription.
    phrases = [
        [64, 67, 71, 74, 71, 67, 66, 64],
        [62, 64, 67, 71, 69, 67, 64, 62],
        [64, 67, 76, 74, 71, 67, 69, 71],
        [76, 74, 71, 69, 67, 66, 64, 64],
    ]
    roots = [40, 36, 43, 38]   # Em / C / G / D
    for rep in range(2):
        for bar, phrase in enumerate(phrases):
            base = (rep * 4 + bar) * 4 * ppq
            root = roots[bar]
            note(guitar, 1, root + 12, base, 4 * ppq - 12, 62)
            note(guitar, 1, root + 19, base, 4 * ppq - 12, 54)
            for beat in range(4):
                note(bass, 2, root, base + beat * ppq, 72, 77)
                note(drums, 9, 36 if beat in (0, 2) else 38, base + beat * ppq, 12, 65)
                for sub in (0, 48):
                    note(drums, 9, 42, base + beat * ppq + sub, 10, 38)
            for idx, pitch in enumerate(phrase):
                note(melody, 0, pitch, base + idx * 48, 42, 82 if idx % 2 == 0 else 67)
    tracks = [midi_track(t) for t in (conductor, melody, guitar, bass, drums)]
    head = b"MThd" + struct.pack(">IHHH", 6, 1, len(tracks), ppq)
    return head + b"".join(tracks)


def apply(engine: Path) -> None:
    file = engine / "src" / "intro.c"
    if not file.exists():
        raise RuntimeError("Expected Emerald intro source is missing")
    code = file.read_text()
    anchor = "static void MainCB2_EndIntro(void);"
    call = "CreateTask(Task_Scene1_Load, 0);"
    if MARKER not in code:
        if code.count(anchor) != 1 or code.count(call) != 1:
            raise RuntimeError("Unexpected original Emerald opening structure")
        code = code.replace(anchor, anchor + "\n" + CINEMATIC, 1)
        code = code.replace(call, "CreateTask(Task_RockstarGothicMovie, 0);", 1)
        file.write_text(code)
    elif "CreateTask(Task_RockstarGothicMovie, 0);" not in code:
        raise RuntimeError("Partial Rockstar intro patch detected")
    path = engine / "sound" / "songs" / "midi" / "mus_intro.mid"
    if not path.exists():
        raise RuntimeError("Expected Emerald intro MIDI is missing")
    path.write_bytes(compose_intro())
    print("Installed 3-act gothic Rockstar startup and original synth-rock opening music.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("engine", type=Path)
    args = parser.parse_args()
    apply(args.engine)

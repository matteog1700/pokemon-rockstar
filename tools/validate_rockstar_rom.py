#!/usr/bin/env python3
"""Reject baseline Emerald ROMs mislabeled as Pokémon Rockstar November 22.

This checks core encoded script markers and header integrity; it does NOT prove
that graphics, concert animation, map warps, or crash points work in an emulator.
"""
import argparse
import hashlib
from pathlib import Path

TEXT = {**{chr(65 + i): 0xBB + i for i in range(26)},
        **{chr(97 + i): 0xD5 + i for i in range(26)},
        " ": 0x00, "-": 0xAE, ".": 0xAD, "!": 0xAB}

MARKERS = {
    "concert dialogue": "LIL PEEP and TOO POOR take the stage",
    "professor Ozzy": "OZZY OSBOURNE",
    "Crystal Forest": "CRYSTAL FOREST",
    "Celestial Woods": "CELESTIAL WOODS",
    "Madness": "MADNESS",
}

def validate(rom: bytes) -> list[str]:
    errors = []
    if len(rom) not in (16 * 1024 * 1024, 32 * 1024 * 1024):
        errors.append(f"Unexpected size: {len(rom):,}")
    if len(rom) < 0xC0:
        return errors + ["GBA header absent"]
    if rom[0xB2] != 0x96:
        errors.append("GBA fixed header byte incorrect")
    checksum = (-sum(rom[0xA0:0xBD]) - 0x19) & 0xFF
    if rom[0xBD] != checksum:
        errors.append("GBA header checksum incorrect")
    for title, phrase in MARKERS.items():
        encoded = bytes(TEXT[c] for c in phrase)
        offset = rom.find(encoded)
        if offset == -1:
            errors.append(f"Missing Nov 22 Rockstar marker: {title}")
        else:
            print(f"PASS {title}: offset 0x{offset:08X}")
    return errors

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rom", type=Path)
    args = parser.parse_args()
    rom = args.rom.read_bytes()
    problems = validate(rom)
    print("SHA256: " + hashlib.sha256(rom).hexdigest())
    for problem in problems:
        print("FAIL: " + problem)
    if problems:
        print("NOT A VERIFIED NOVEMBER 22 ROCKSTAR ROM")
        raise SystemExit(1)
    print("PASS: November 22 script markers present; gameplay and visuals NOT yet verified.")

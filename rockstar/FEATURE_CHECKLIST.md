# Pokémon Rockstar — feature checklist

This is a development checklist, not a statement that every requested feature is playable. GitHub Actions success verifies **compilation**, not in-game rendering. Update progress only after evidence.

## Characters
- [ ] **Professor Ozzy**: Replace Birch's 64×64 introduction PNG with faithful long black hair, purple round sunglasses, gothic outfit and silver cross; replace relevant overworld art; emulator-test.
- [ ] **Lil Peep**: Faithful black-and-pink split hair, recognizable tattoos, jewelry and gothic clothing in intro portrait plus walking/running/bike/fishing/surfing/underwater and battle sprite sets; emulator-test.
- [ ] **Too Poor**: Faithful hair buns, tattoos, gothic jewelry and clothing in matching full sprite sets; emulator-test.
- [x] **Lil Peep / Too Poor selection wording**: Source patch authored in rockstar/apply_character_choice.py; swaps both professor's "boy/girl?" question and actual menu options. Save identifiers remain male/female for compatibility. Needs GBA and emulator verification.

## World and story
- [x] 12 musician-themed town names (including **LIL PEEP TOWN**), weather and neon palette changes. Compiled in prior ROM.
- [x] 12 Neon Note fetch missions/NPC or sign scripts authored and compiled; individually still need gameplay checks.
- [ ] Completely different town geography / map.bin layouts; new landmarks, safe route connections and warps. Still substantially Hoenn geography.
- [ ] 12 distinctive original building/landscape tilesets rather than just neon palettes.
- [ ] Full new story and branching side missions beyond Neon Note fetch quests.

## Gameplay and menus
- [x] Gothic custom title and original title/intro MIDI. Compiled.
- [x] Kaleidoscopic opening effect and black/red introductory/menu palettes. Compiled; visual test pending.
- [x] Intro Rayquaza species selection and Professor Ozzy dialogue. Compiled, but image of Professor still Birch until replaced.
- [x] Madness V1: temporary confusion-derived battle status on common status effects, 1.5x damage and decreased accuracy, new battle text/palette. Compiled; NOT a full original animation from The Edge of Allegoria or every possible ailment.
- [x] EV editor: Pokémon Summary > Skills > A, 510 total points, 252 maximum per stat, read-only IVs. Compiled; emulator and save/load test pending.
- [x] First-pass starter item/candy/ball additions. Compiled; verify in-game quantity.
- [ ] First-slot Pokémon follows trainer in overworld with party switches.
- [ ] Every obtainable/encountered Pokémon legendary (distinct from only showing Rayquaza in intro).
- [ ] Old-stat combined Attack + Sp. Atk / Defense + Sp. Def mode.
- [ ] Complete black-background, white-text treatment across menus and game dialogue.
- [ ] Full start-to-finish playable testing: Intro sprite, character sprites, legendary starter, all 12 towns/routes, Madness, EV editor, side missions, save/load.

## Verification
- Compiled source and source-authored art are NOT equivalent to emulator-tested playable assets.
- Keep the prior working ROM when iterating.
- Record each compile run and emulator outcomes before claiming a release is complete.
- Never call the trilogy/game complete until the full feature set has been implemented and tested.

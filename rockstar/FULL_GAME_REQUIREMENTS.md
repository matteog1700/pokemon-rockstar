# Pokémon Rockstar — complete native GBA game requirements

The canonical implementation checklist. A completed item must be integrated into buildable GBA source, not just described or illustrated.

## 12 neon towns — entirely new geography, not a recolored Hoenn
1. Rockstar Town — home town, dedicated tileset and Mega Stone shop, Professor Ozzy
2. Neon City — items, TMs, moves, Ability shop
3. Electric Forest Town
4. Cyberpunk City
5. Lava Rock City
6. Crystal Falls
7. Midnight Harbor
8. Phantom Town
9. Thunder Mountain
10. Starlight City
11. Rainbow Paradise
12. Legendary Kingdom

- [ ] Build each town's new tile map, terrain, collision, warps, tileset, palettes, events, NPCs, music and links.
- [ ] Replace Hoenn geography with the new region, vivid magenta/purple/cyan/orange/red/lavender.

## Character identities and visual continuity
- [ ] Lil Peep selectable male trainer with split black/pink hair, tattoos, black/pink jacket, crosses and jewelry. Full GBA overworld walking frames, trainer battle, dialogue portrait.
- [ ] Too Poor replaces May with black/pink hair buns, facial tattoos, chains and gothic clothing. Full battle/portrait/walking sprite set.
- [ ] Ozzy Osbourne as professor with long dark hair, purple glasses, jewelry, large cross, black clothes. Full professor dialogue/portrait and overworld graphics.
- [ ] Every ordinary NPC in gothic black clothing with chains and piercings. Shared recolored NPC palettes are only the first color pass; bespoke pixel detail still needed.
- [ ] Match the detailed user-selected reference art rather than generic recolors.

## Main story and side missions
- [ ] Entirely original underground-music mystery with Neon Notes, rebellious rivals, legendary powers, fame/identity/friendship, and Rockstar Festival restoration.
- [ ] Collect 12 Neon Notes across the region, culminating in the festival finale and legendary arc.
- [ ] Original characters/encounters: Ozzy Osbourne, Forest Ranger, Too Poor, DJ Voltage, Ashen Rider, Crystal Keeper, Harbor Captain, Phantom Singer, Storm Rider, Star Astronomer, Rainbow Guardian, Rockstar Champion.
- [ ] Redesigned gyms, trainers, randomized encounters where safe, optional missions, new plot events and story progression.
- [ ] Original Ozzy-inspired rock soundtrack, without copyrighted recordings.

## Gameplay systems and completion
- [ ] First party-slot Pokémon follows the player in the overworld.
- [ ] Start new game with 999 Rare Candies and 99 of each original Poké Ball (source patch currently added; verify with emulator).
- [ ] All 386 authentic Gen III Pokémon; official Legendary/Mythical options including Mew, Celebi, Jirachi, Raikou, Entei, Suicune, Lugia, Ho-Oh, Rayquaza, Groudon, Kyogre and Deoxys.
- [ ] Authentic shiny Pokémon and Shiny Charm from start.
- [ ] Mega Ring from start and Mega Stone shop in Rockstar Town (requires Mega Evolution support).
- [ ] Neon City items/TM/moves/Abilities shop.
- [ ] Optional combined Attack + Special Attack and Defense + Special Defense mode.
- [ ] New story missions, side missions, new landscape, puzzles, encounters and music.
- [ ] GBA compile must succeed, upload artifact, then verify boot and play through RetroArch.

## Verified versus provisional
- [x] Github branch and reproducible pinned Emerald source checkout workflow added.
- [x] Source patches for Rockstar Town intro, sign, 2 NPC dialogues, starter inventory and 4 shared NPC palette families added.
- [x] Contract tests included for patches.
- [ ] Nonempty patched .gba produced by a successful CI run.
- [ ] Custom characters and 12 new towns integrated and visually verified in-game.
- [ ] Full Pokémon Rockstar tested playable in RetroArch.

Earlier diagnostics described 19 Rockstar Town tileset assets, but those exact editable assets and prior source archive have not yet been recovered. Character concept sheets remain references, not compiled assets.

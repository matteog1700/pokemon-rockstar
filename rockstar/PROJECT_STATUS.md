# Pokémon Rockstar — project and build status

## Mission
Build a custom GBA adventure in a new neon region. An upstream Emerald baseline is not a finished Rockstar game.

## Preserve original trainer design references
- Lil Peep: split black/hot-pink hair, detailed facial and neck tattoos, gothic jacket, crosses and chains.
- Too Poor: black-and-pink hair buns, detailed face tattoos, gothic jewelry and clothing.
- Ozzy Osbourne: long dark hair, purple sunglasses, dark gothic outfit, rings and large cross.
- Each requires coherent walking frames, dialogue portrait and battle sprite. Existing sheets are concepts, not yet integrated GBA assets.

## Custom region and mechanics
- 12 distinct neon towns including Rockstar Town, dedicated tileset and new geography rather than Hoenn recolors.
- Original underground-music mystery, rival characters and side missions.
- First-party Pokemon following the trainer.
- x999 Rare Candies, x99 of every Poke Ball, and access to legendary Pokemon.
- Optional combined physical/special attack and physical/special defense battle rules.

## Baseline build
- Public source: https://github.com/pret/pokeemerald
- Pinned upstream revision: 731ad5bfd6e6f265508d0efcca0ba42f9dcf5881
- Workflow: .github/workflows/rockstar-foundation.yml
- This workflow downloads the public source for a temporary baseline build. It does NOT integrate Rockstar assets, nor make this repository an editable clone of the engine.

## Required validation
1. Compile the upstream baseline and confirm a nonempty GBA file.
2. Test launch in a GBA emulator.
3. Bring editable Emerald source into the project and integrate exact character concepts.
4. Add custom towns, maps, scripts, gameplay modifications and side missions.
5. Build and test the customized game, including save/load and battles.

No playable Pokemon Rockstar ROM is claimed complete.
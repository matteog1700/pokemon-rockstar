# Pokémon Rockstar — source integration audit (2026-11-11)

## Verified input
- Latest user-provided `PoKeMoN-RoCkStAr-LilPeep-TooPoor-Choice-GBA.zip` contains one `Pokemon Rockstar.gba` (a binary ROM, not source code).
- `Pokemon_Rockstar_Source_REUPLOAD_2026-11-11.zip` contains the `pokeemerald-expansion-master/` source tree, including `Makefile` and `config.mk`.
- `ROCKSTAR_INTEGRATION_STATUS.txt` inside the source explicitly states: walking sprites installed, source not compiled; running/biking/battle sprites, towns, story and ROM testing unfinished.
- `data/maps/LittlerootTown/map.json` still identifies `MAP_LITTLEROOT_TOWN` / `REGION_HOENN`, confirming original geography remains in this source snapshot.
- The Rockstar Town secondary tileset asset directory exists, but its presence alone does not establish engine registration or map assignment.

## Next implementation order
1. Import the full source archive into a build-accessible GitHub Release or checked-out `game/` directory; preserve original archive unchanged.
2. Obtain a successful baseline GitHub Actions compile; capture full job logs and SHA256 of output. A valid header in an existing ROM is **not** proof that this source compiled.
3. Integrate the Lil Peep / Too Poor selection names, trainer front/back portraits and all walking/running/biking sprites. Verify graphics pointers and palettes, not just image files.
4. Register Rockstar Town tileset, attach it to a map layout, update map connections, warps, and collision.
5. Implement remaining towns, story, following Pokémon, legendary availability, Madness effect, and EV customization in small, independently compiling changes.
6. Test a new save and transitions in a GBA emulator after each milestone.

## Build gate
Only label a new ROM as compiled when a GitHub Actions job has completed successfully, emitted a fresh `.gba`, and passed output checks. Playability requires additional emulator testing.

## Current blockers
The GitHub repo currently does not contain the source archive, and the available GitHub connector does not support uploading binary Release assets. The workflow can fetch the archive once it is attached to a Release.

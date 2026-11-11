# Pokémon Rockstar — Visual Fidelity Specification

## Source references
User-provided concept images in the conversation on 2026-11-11:
- `49882.jpg` — enchanted violet forest with cyan luminous hedges, pink/orange canopies, skulls, bridges, fences, mushrooms, deep ravines.
- `49881.jpg` — gothic graveyard settlement, cold cyan illumination, blue-violet masonry, gravestones, statues, dark red trees, character with Pokémon follower.
- `49880.jpg` — dense futuristic neon city, glowing storefronts, holographic signs, rooftops, street NPCs, pink/cyan/purple light.

These images are **visual targets only**, not existing compiled maps or GBA tilesets. Keep the original image files as references; do not present generated approximations as extracted game assets.

## GBA art constraints
- Native display: 240 × 160 pixels; design layouts and screenshots at this resolution first, then nearest-neighbor scale for review.
- Map tiles are 8 × 8 pixels; typical metatiles are 16 × 16. Build reusable, edge-consistent tile and metatile sets.
- Palette and VRAM constraints are real: glowing gradients and shadows from references must be translated into palette-controlled pixel clusters and carefully authored dithering, not full-screen photographic effects.
- Ensure path readability, solid collision, map connections, warps, and correct elevation/ledge behavior.
- Preserve unique silhouettes, readable characters, and Pokémon follower animation in every area.

## Art direction by biome
### Haunted Neon Forest
- Dominant violet/lavender soil; cyan luminous plants; pink/coral foliage; dark twisted trunks.
- Skull props, luminous mushrooms, ravines, rope/wood bridges, fences, layered tree canopies.
- Keep traversable paths clear and use static highlight tiles plus limited palette animation for shimmer.

### Gothic Cemetery Town
- Blue-violet stone walkways and buildings, cemetery walls, statues, gravestones, dark red foliage.
- Light sources at doors and lamps; graveyard and town should share consistent light direction.
- Keep buildings, entry points, collision, NPCs, and follower sprites readable against the background.

### Cyberpunk Rockstar City
- Packed architecture, purple/cyan/pink neon storefronts, dark sidewalks, rooftop signs, hologram-inspired pixel panels.
- Separate decorative signage from walkable paths and interactive entrances.
- Create reusable shop façades and signs; avoid text too small to read at 240×160.

## Acceptance criteria (required before calling a location complete)
1. Registered primary/secondary tilesets, palette data, map layout and map JSON in source.
2. No missing tiles, corrupt palettes, invisible walls, broken warps, or out-of-bounds movement.
3. Native-resolution emulator captures at day/night-equivalent scenes as supported by engine; compare against the user concept reference.
4. Player and Pokémon follower animate and remain visible in foreground/background layering.
5. Region map connections, music assignment, and scripted interactions tested.
6. GBA ROM compiled from the committed source, with build artifact and test evidence.

## Current status
Visual requirements documented. **No maps, sprites, lighting effects, or tilesets have been implemented or verified by this specification commit.** Source archive still must be available to the build workflow before compiling.

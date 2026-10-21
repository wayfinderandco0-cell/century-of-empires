# Octagon 001 — Art production checkpoint
Date: 2026-10-20. **Illustrative asset extracted; not georeferenced or production-approved.**

## Art candidate
A detailed Alpine landscape image previously approved by the user was isolated from a design board into an alpha-clipped terrain-art candidate. This is only a visual study; it is **not** the final registered tile, and its creative river alignment is inconsistent with the saved Fidlerbach route in part of the cell. Companion ChatGPT conversation artifacts: `century_octagon001_illustrative_cutout.png`, `century_octagon001_art_geography_review.png`, and `century_octagon001_alignment_debug.png`. These files are conversation artifacts, not yet committed GitHub game assets.

## Immutable source of truth
- `terrain-puzzle/BNR-O-0-0.json`: geographic boundary, eight structural portals.
- `terrain-puzzle/BNR-O-0-0-geographic-control.json`: source-stream intersections. Fidlerbach crosses roughly north-to-south; Navisbach reaches only the southern margin of the study octagon.
- `terrain-puzzle/BNR-O-0-0-hidden-routing.json`: 25 invisible candidate nodes and 23 edges, all disabled; no invented ford/bridge.
- `terrain-v97/brenner-data.json`: retained elevation spacing about 160–230m, so microterrain detail is illustrative, not measured.
- `terrain-v102/features.json`: modern natural stream geographic guides and illustrative pack trail; **not authenticated 1800 survey**.

## Production requirements
1. **North-up, geographic coordinates fixed.** Make a borderless full-bleed rectangular art asset, one 1000m octagon cell plus 60m overlap for seams; the engine must clip it after rendering. An octagon-shaped cropped concept is insufficient for neighboring cells.
2. **Art follows geography.** Align stream, ridges, passes and cliff transitions to atlas elevation/hydrography; do not move streams to fit scenic images. Treat village huts, forest details, pack trails, rocks and bridges as speculative illustrations pending historic evidence.
3. Never bake a visible octagon border, developer dots, path markers, numbers, compass or UI into terrain textures. Hidden route graph and gameplay ownership layer stay separate.
4. Four visual scales need appropriate resolution/LOD; cannot simply enlarge a 500px concept or an old V102 terrain image for full close zoom.
5. Verify with Octagon 002 and connector in portrait/landscape iPhone screenshots before merging. Do not alter playable game or save keys.

## Next milestone
Create a fully geographically aligned art-painting / material for the first **one kilometre** octagon with geographic feature controls, then use the 002 registered atlas basis to compare edge colors/feature continuation. The existing V106 geometric assembly proof remains separate from visual quality approval.

# Century of Empires V105 - geographically anchored forest canopy experiment

Status: prototype only, not approved for publication. Branch: `terrain-v105-canopy-bake`.

## Goal
Replace V103 repeated triangular tree glyphs and V104 still-cone-like 3D trees with continuous and spatially diverse forest material across the measured Alpine geography. The user explicitly prefers a natural geographic appearance, especially in the close view, and existing Atlas/Region relief is the best piece to preserve.

## Implementation
- Standalone `v105-brenner-visual-pilot.html`, `terrain-v105/pilot.js`, `terrain-v105/pilot.css`, and deterministic `terrain-v105/build_canopy.py`.
- The canopy baker samples the reused V97 woodland proxy and elevation, creates an irregular canopy with spatial shade and clearing patterns; it keeps stream-guide clearings. It reuses V102 base material, relief and stream source; no new terrain data or historically verified trees.
- No individual tree billboards; at close zoom the continuously baked canopy texture covers forest where the woodland proxy supports it. This is an **art experiment**, not yet a detailed 3D game forest.
- Transition from V102 broad geographic material to V105 detailed canopy based on camera span; atlas remains stable.
- Existing game, saves, V94, V100, V101, V102, V103 and rejected V104 stay untouched.

## QA
- GitHub Actions `.github/workflows/qa-v105-visual.yml` runs `build_canopy.py` before phone-size Chromium/WebKit checks and saves both portrait and close canopy screenshots. Review generated images; code checks alone do not establish artistic quality.
- Visual approval should precede all playable-game integration. If baked continuous canopy looks merely like camouflage, further refine using real tree-cluster art and shadows.

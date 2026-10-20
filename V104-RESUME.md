# Century of Empires — V104 forest-mesh checkpoint

Status: standalone graphics trial; physical iPhone evaluation still required.

## Why
The user's real V103 iPhone screenshots show that the repeated triangle trees are very obviously icons rather than realistic forests, especially in the final close zoom. Geographic Alpine ridges are much better than earlier versions. The main bottleneck is zoom LOD and vegetation art, not lack of additional world terrain.

## Implementation
- Branch `terrain-v104-forest-mesh`, based on production main, does not edit V94/V100/V101/V102/V103 or campaign saves.
- `v104-brenner-visual-pilot.html` with renderer `terrain-v104/pilot.js` and CSS `terrain-v104/pilot.css`.
- Reuses original V97-derived V102 geography and tree-position data. No new measured details claimed.
- Broad views use terrain material to represent forest masses. Detailed forests only come in closer than 4.3 km camera span.
- Replaces 57,159 repetitive 2D sprite symbols with dynamic, geographically positioned 3D layered canopy meshes for trees near the camera. World-space triangles taper organically in 3D with deterministic color and crown variations.
- Navigation may zoom closer to .85 km, although the underlying saved elevation samples are still roughly 160–230 metres apart; such small scale geography is illustrative and can appear simplified.
- V103 mesh-aligned mapped rivers and subdued illustrative pack trail retained.

## QA and approval
- GitHub Action file `.github/workflows/qa-v104-visual.yml`, Python `scripts/qa_v104_mobile.py`.
- Validate WebKit and Chromium portrait/landscape, source and campaign isolation, 3D forest geometry at close view, and iPhone-like screenshot inspection. Automation is not physical iPhone QA.
- Do not merge into the original gameplay. Visual standards remain unapproved until user evaluates a live Safari screenshot. If render looks too geometric or overdrawn, tune or switch technique before generalization.

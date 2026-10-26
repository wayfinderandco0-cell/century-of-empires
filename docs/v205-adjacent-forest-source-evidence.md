# V205 — native contiguous natural-cover source candidates (game still RED)

V204 proved that the existing V180 modern Matrei geographic anchor can produce three exact native adjacent 512×512 source panels, but **actual inspected aerial imagery is dominated by a paved highway, 2023 imprints, sports facilities and modern buildings**. It is not a defensible period-art replacement.

V205 builds on that *verified negative finding*, rather than pasting urban photography into the 1780 game. The source generator now supports two fixed, independently identified reference sites. The new **forest** reference is 11.43950°E, 47.10000°N, near the V197 western forest material study. This is an **approximate geographic reference vicinity**, not a claimed exact V197 crop center, original Matrei bridge, or V123 game cell.

The same 12 native zoom-18 EPSG:3857 source JPEGs are acquired at this forest site to form an L-shaped WEST / CENTER / SOUTH **modern reference mosaic** with exact adjacent footprints. Each source RGB pixel is preserved; source JPEG hashes, manifest identity, panel coordinates, source seams and contact-sheet pixels are checked. The southwest quadrant remains unfilled. No synthetic trees, noise, fake cartways, copied village, modern-feature inpainting, invented roads or bridge bank.

New `scripts/test_v205_adjacent_forest_materials.py` rejects source-site swaps, false game/historical approvals and modified image manifests. Existing V204 negative controls remain. Separate CI jobs verify source imagery and keep the inherited V203 real-browser photographic game-art gate **strictly enforced**, not lowered or allowed to confer approval.

**Limits:** even if forest reference pixels are natural and geographically contiguous, these panels are not V123 game octagons. Modern trails, date imprints, forestry operations or unmarked buildings may still be present. Historic vegetation, road, bridge, game-to-geography transform, four V100 zoom tiers and physical iPhone visual acceptance remain unverified. V121 photo and V123 route/army graph remain pinned and unchanged; no main/campaign/save/production changes or paid services.

**Next:** inspect the real V205 contact image, quarantine obvious modern features, identify verified natural-cover areas at each source panel and only then develop geographically supported **candidate** game art with independent source-to-V123 control points. Retain all game-art approval flags FALSE.

## Verification

[V205 run 40269057347](https://github.com/wayfinderandco0-cell/century-of-empires/actions/runs/40269057347): **contiguous-forest-source job SUCCESS**. Both V204 and V205 offline negative-control test suites passed; 12 real native JPEGs were acquired and independently re-verified. Actual [artifact 12627508315](https://github.com/wayfinderandco0-cell/century-of-empires/actions/runs/40269057347/artifacts/12627508315) was downloaded and its contact image opened for visual review.

**Actual source visual finding:** all three panels contain genuinely detailed Alpine conifer canopy and terrain shadows, substantially more natural than the game's painted oval trees. However, the WEST reference visibly contains a wide pale modern track, the SOUTH reference has multiple hairpin roads, and all panels have embedded 2023 date imprints. This **disqualifies the raw mosaic from historical game placement**; natural forest pixels are potential materials only after audited exclusions. The panels are geographically adjacent to each other, NOT registered to the V121 original Matrei painting or V123 playable cells.

Native zoom-18 source origins: WEST [139398,92095,18], CENTER [139400,92095,18], SOUTH [139400,92097,18]. No-data/near-white fraction = **0** in all three panels. Source-edge diagnostic mean RGB deltas: WEST→CENTER **8.1947**, CENTER→SOUTH **8.0208**; these are not V123 game border seam measurements.

The second V205 workflow job independently enforces the unchanged V203 strict game-art screenshot gate; it must remain RED until the playable WEST/SOUTH images genuinely improve. **No approval flags were changed.**

**Next code task:** source-native, manually auditable exclusion masks for the visible modern tracks and date stamps; harvest only clean natural-cover RGB patches, retain their real coordinates and source hashes, and never inpaint or assign them false V123 positions.

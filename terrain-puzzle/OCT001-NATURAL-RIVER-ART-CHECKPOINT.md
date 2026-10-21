# Octagon 001 — First geography-locked natural river art study

Date: 2026-10-20. **Visual candidate only; not a verified historical game tile**.

## What was actually built
A fresh full-bleed 1600×1600 illustrative Alpine scene for x/y = −560m to +560m around the canonical Octagon 001 geographic origin. Unlike the earlier bright cyan graphic stripe, the first river revision now uses photorealistic rocky-bank, riffle and water detail sampled from the user-approved Alpine **style reference** and warped to the 68 preserved V102 Fidlerbach points. The resampled river spine is mathematically coincident with the source centerline in the current monotonic-Y model (max measured interpolation displacement: 0 screen pixels at these 68 points).

**The warped photo texture is illustrative**, not a measured stream width, contour shape or period-1800 bank survey. The surrounding forest/cliff painting is still not geographically registered to the retained DEM; this cannot be treated as certified passable terrain. The normal player-facing version shows no octagon or route markers.

A diagnostic version displays the same underlying art plus:
- the exact Octagon 001 outline;
- 25 existing unapproved bank/valley graph candidate nodes and 23 links;
- 13 candidate links only in faint trail color;
- nine steep-screening failures and one unverified water crossing in red;
- a faint Fidlerbach centerline reference. All gameplay edges **remain disabled**.

## Outputs in ChatGPT conversation (not GitHub binary blobs)
- `century_oct001_vnext_natural_river_clean.jpg` (full-bleed 1600px review)
- `century_oct001_vnext_natural_river_debug.jpg` (identical scene + hidden developer controls)
- `century_oct001_vnext_natural_river_comparison.jpg` (phone-friendly side-by-side)
- `century_oct001_vnext_natural_river_validation.json` (validation report)
- `build_oct001_natural_river_vnext.py` (reproducible local Python/PIL/OpenCV photo-bank texture warp)

Source visual reference: `a_high_resolution_realistic_top_down_isometric_l.png`; source clean landscape: `top_down_aerial_orthographic_landscape_scene_a_hi.png`, both conversation images, not game data.

## Critical unfinished items
1. **Actual geographic landform registration:** source landscape photo is not measured terrain. Do not state cliffs/meadows represent the physical valley correctly.
2. **Art-first route redesign:** the candidate bank corridor still runs across major depicted cliff areas; it must be redrawn along plausible benches and then checked against better terrain data. **Do not generate approved new nodes from the legacy graph**.
3. **Historical crossings:** the approved-style image has a pretty bridge, but none has been authenticated here. Do not reproduce as a traversable bridge without explicit historical/scenario provenance.
4. **River finish:** photographic texture warp is dramatically less artificial than a solid line, but river widths, rocky banks and foam should be reviewed on physical iPhone for authenticity. The stream centerline is map-locked; its microdetail is invented.
5. **Neighbor seam:** 001's east edge / southeast connector and 002's material blend still require QA.
6. **Publication:** do not merge images, sources or candidate routing into production game, v106 preview, or saves before the user approves them.

## Next build gate
Review side-by-side clean and developer images; improve the geometry of the route **against the visual and a higher resolution DEM**, then generate nodes from the final accepted path and test seam across Octagon 002. Keep the normal player view dot-free and the debug overlay separate.

Existing branch requirements remain authoritative:
`terrain-puzzle/OCT001-VNEXT-ART-ROUTE-MASTER-SPEC.md` and `OCT001-VNEXT-CONTRACT.json`.

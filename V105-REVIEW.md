# V105 independent visual review — October 20, 2026

## Decision
**Do not publish V105 or merge into main yet.** Keep it as a reproducible graphics experiment, and preserve V103 as the public visual comparison baseline.

## Verified
- GitHub Actions run 39511761939 succeeded.
- Chromium and WebKit phone-size simulations passed, including load, four zoom modes, landscape, pointer interactions and zero JavaScript errors.
- V105 `terrain-v105/navis-canopy.webp` generated from the V97 woodland/elevation proxy and V102 existing material. Deterministic 2048x2048. No new measured geography and no historical woodland survey.
- No repeated triangles, tree sprites or individual conical tree glyphs rendered.
- Screenshot evidence in `terrain-v105/chromium-portrait.png`, `chromium-canopy-detail.png`, `webkit-canopy-detail.png`, and matching landscape shots.

## Screenshot inspection
- **Positive:** at landscape/medium terrain scale the shaded geographic forest is more coherent than V103/V104 icons, and the mountain terrain remains legible. Header collapses at close zoom.
- **Remaining failure:** at closest zoom, forest is predominantly broad smooth camouflage-like shading and lacks recognizable volumetric tree canopy, believable ground texture and sharp transitions. The source is 2048px for an approximately 15-by-13 km local map, so magnification cannot create convincing individual tree details.
- No physical iPhone Safari test completed for this experimental branch; no professional visual quality claim.

## Next highest-value step
Stop endless low-detail procedural-noise variants. Build a limited high-resolution **reference-quality art tile** for a single 0.5–1 km forested valley segment, with visible canopy, irregular gaps, understory, cliffs, boulders and path/river alignment; compare it to historical-grand-strategy visual references at the intended **screen pixels per meter**. Design *explicit forest LOD* (continuous mass at overview; authored canopy clusters in local; textured 2.5D/tree silhouettes at actual close zoom) and performance budget for the iPhone. Only when the still reference looks right should it be incorporated as a camera-anchored renderer. Geographic source cannot support sub-160m measured features; any added microdetail must be labelled illustrative.

## Safety/continuity
Keep v94.html, V100, V101, V102, V103, V104 and campaign saves untouched. V105 is on `terrain-v105-canopy-bake`; the full game and main branch were not changed.

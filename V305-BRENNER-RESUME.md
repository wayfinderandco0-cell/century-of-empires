# V305 — Brenner regional geography in the original campaign UI

## Implemented
- Original campaign includes a Brenner terrain control and an EPSG:4326-positioned Brenner pin. Either opens a detailed regional geographic lens.
- The regional view displays existing high-resolution V97 Copernicus DEM-derived shaded relief for 11.26–11.80 E, 46.80–47.42 N instead of random recycled octagons.
- V99 OpenStreetMap local streams use the same geographic coordinate transform; only the original sampled area is represented.
- Historic settlement markers: Innsbruck, Matrei, Steinach, Gries, Brenner Pass and Sterzing, with approximate contemporary town-center coordinates.
- Brown dashed line is explicitly *approximate corridor context*, NOT a verified carriage-road centerline or crossing. It changes interpretation after the Wilten–Schönberg road-building period ending in 1845; this visual change is not a gameplay rule.
- Existing V121 Matrei art is in a reference overlay; V267 West/South are marked unapproved review textures, not geographic production assets.
- Touch and pinch zoom on iPhone and close/return function; the real campaign year is passed read-only from the existing clock.
- Browser QA in WebKit and Chromium tests original campaign UI, loading terrain and streams, geographic math, screenshots, and unchanged saves.

## What this does NOT claim
- It is not 50 completed octagon assets, a new 3D engine, a certified historical road survey, a historically verified bridge map, or a replacement movement graph.
- The original game's provinces do not have independent Matrei/Steinach gameplay IDs, so the close-up is an art/geography lens, not a second source of army commands or army movement.
- The game rules, unit sprites, selection, orders, campaigns, battle/production, ticking and saves are unchanged.

## Future work
1. Inspect mobile screenshot artifacts and ensure the new art has no visible breakage.
2. Extract exact pre-1845 period road and bridge alignments from authenticated historical maps; validate and georeference before changing the dashed graphic to a solid historical road.
3. Add photographic/painted valley detail based on actual terrain and the V121 accepted art style, not unapproved clones across unrelated scenes.
4. Link actual existing army unit IDs and march geometry to those geographically verified routes once supported by the original game. Do not invent a Matrei province, order types, or capture behavior.
5. Run iPhone unit-on-road and road-seam verification, then seek user visual acceptance.

## Historical references
- University of Innsbruck Brennerpass: https://orawww.uibk.ac.at/apex/uprod/f?p=LLW:3:0::NO::P3_ID:1179
- OSM local-stream data and © OpenStreetMap contributors, ODbL 1.0: terrain-v99/brenner-streams.json
- Copernicus DEM GLO-30 / ESA WorldCover source and bounds: terrain-v97/manifest.json
- Saved settlement-anchor data: terrain-grid/brenner-historical-anchors.json

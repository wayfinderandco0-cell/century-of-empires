# V304 — Georeferenced continental relief, original campaign preserved

## What this branch changes
- Adds \`terrain-v94/map-lod.js\` to the **existing \`index.html\` campaign map** as a rendering-only SVG image layer.
- Uses exactly the \`proj(lon,lat)\` map projection and geographic bounds already in the original project: lon -14..49, lat 26..75.
- Draws the V94 overview under political borders, city/army sprites, orders, and the existing route layer.
- At close zoom, loads only the V94 4×3 high-resolution terrain tiles intersecting the iPhone viewport. Distant views keep a single lightweight overview, protecting mobile memory. No roads or unit movement are inferred from imagery.
- Reattaches art after the historical geometry loader rebuilds its \`terrainVisual\` group, and updates on pinch/pan/zoom.
- Leaves existing campaign state, province IDs, battle logic, 1780–1880 clock, order handling, UI IDs, and save data unchanged. Original \`index.html\` remains the actual campaign, not the separate V303 or 12-province demos.
- Adds Chromium and WebKit mobile-size QA and screenshots in \`scripts/qa_v304_geography.py\`.

## Geography and historical confidence
- Source is the existing V94 physical atlas: Mapzen/AWS Terrarium z8 measured relief and Natural Earth physical data.
- Vegetation is idealized pre-modern, **not** a verified 1780–1880 forest survey.
- Roads, bridges, military routes and historic town placements in the original game remain approximate. Political borders are a separately sourced 1783 reconstruction, asynchronously loaded.
- The source atlas is continent-wide raster relief. It is **not** the three user-approved local Alpine art scenes, nor a completed 3D/WebGL terrain renderer. Do not claim art acceptance from these changes.

## Remaining work, in order
1. Review V304 iPhone screenshots and CI. If map visual layering covers political or unit information, adjust only opacity/LOD; do not replace original mechanics.
2. Recover the exact three approved local source textures and their coordinates from V121/V123 and the terrain-grid art. Reconcile seam issues against shared world-space registration, not just 57 schematic joins.
3. Author a **geographically anchored** Brenner / Wipptal detail layer: terrain relief, watercourses, roads, bridges and correct historical towns for an explicitly selected campaign start. Use sourced geodata and identify uncertain historical road alignment.
4. Connect those graphic coordinates to the *existing* army sprite, select-destination-Execute behavior and saved order positions without importing V303's or the 12-province demo's standalone movement, turn, or capture rules.
5. Verify iPhone pinch zoom, pan, world-coordinate alignment, road following and visual seams in WebKit.

## Guardrails
See \`AGENTS.md\`: graphics are not mechanics; octagon boundaries are art chunks, not command regions, order requirements, or new provinces. Do not clone full Alpine scenes at random and describe the result as historically accurate.

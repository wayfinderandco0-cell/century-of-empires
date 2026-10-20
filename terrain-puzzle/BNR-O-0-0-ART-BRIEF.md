# Octagon 001 — First Artwork Direction and Acceptance

State: **ART STYLE CONCEPT ONLY; NO PRODUCTION TILE APPROVED**. Artwork must not become a terrain texture until source-controlled alignment checks pass.

## What the player should see
A single **unbroken** Alpine valley scene as part of the overall historical atlas, with varied dense conifers and irregular meadow clearings, weathered rock and scree on steeper ground, physically plausible shadows, and 1780–1880-era illustrative pack paths. No geometric outline, repeating sprites, modern asphalt, pylons, contemporary houses, or decorative labels baked into the art. Make it enjoyable from both portrait and landscape iPhone views.

### Study frame
- Cell `BNR:O:0:0`, octagon pitch 1km, geographic origin 11.520°E, 47.130°N (pilot local coordinates).
- Primary octagon has eight exact boundary sides. The little diamond/square gaps belong to auto-generated connector cells. 60m external bleed supplies blend data.
- **Topological constraint:** the first illustration concepts showing a main river running through the middle under the name "Navisbach" are artistically inspiring but geographically incorrect for this footprint. According to saved V102 / V99 mapped water guides, **Fidlerbach** runs through this octagon; Navisbach appears along its **southern edge**, the latter reaching only about 158m inside under the present clipping approach. The mapped stream crossings and the *illustrative* trail crossings are in `BNR-O-0-0-geographic-control.json`.
- Water coordinates are geographic guides based on modern mapped natural streams, not authenticated 1800 hydrology. The prior V97 elevation grid is ~160–230m between retained samples. Do not hallucinate precision; any trees, rocks, huts, bridges or paths are illustrations, and buildings must not be represented as historical evidence.

## Artist reference — user approval required
The first generated boards in the October 20 ChatGPT continuation are **mood boards only**: they show the ambition for tree depth, stone slopes, believable canopy mass, warm meadows, and one continuous atlas. They also show visible octagon boundaries, portal labels, speculative buildings and incorrectly placed river courses, none of which are final game artwork.

Final art should be built with the correct north-up base; preserve one canonical style/material palette across adjacent pieces. The primary art should extend as full-bleed rectangular imagery **under** the octagon clip rather than baking golden octagon lines into its pixels; the octagon mask, hidden nodes and portals are independent engine data.

## Production test before building a second octagon
1. Create a clean north-up, full-bleed square painting/material for **exactly** the geographically controlled 1km pitch area plus 60m overlap. Do not overlay labels or borders. Keep a Photoshop-like editable/layered source if available; a flattened raster alone makes later seam repair expensive.
2. Overlay the saved control SVG and place Fidlerbach and Navisbach at the correct relative positions. Trace the shared stream/ridge/forest boundaries along all eight sides, marking any speculative details.
3. Prepare an additional adjacent **east-side** atlas-based frame. Its shared edge must use exactly the same feature positions and forest/material palette as the first piece; small connector squares fill the diagonal gaps.
4. Produce separate screenshots at Atlas, Region, Local and Terrain zoom levels, in portrait and landscape. Compare to the earlier user-approved zoom target and get explicit user visual approval.
5. Only after that integrate into the terrain renderer and map routing. Never modify existing campaign game or saved state during this art study.

## Visual acceptance
- Distinct realistic conifer clusters at intended close scale, not dark triangles or smooth camouflage.
- Mountains read as true landforms, not photo pasted onto a flat board.
- Stream, valley and slopes follow control geometry; historical pack paths are restrained illustrations.
- No tile seams or repeating bitmap edges; no noticeable material mismatch when next cell is placed.
- Coast, borders and cities remain controlled by the future common historical atlas rather than cell-local guesses.

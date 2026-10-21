# Octagon 001 — Meadow trail candidates generated from artwork (v1)

**Decision:** preserve the realistic rocky-bank Fidlerbach style and abandon the old nearly straight 32m bank-offset path as a proposed final route. It crosses visually implausible cliff sections. The new **two art-guided trail proposals** follow clearer meadow or terrace areas visible in the scene, but are strictly *illustrative* until a georeferenced higher-resolution DEM and historical route evidence support them.

## What exists
- Separate north/central **west meadow terrace candidate** (~714m, 24 hidden nodes), and **east-bank northern approach** (~287m, 10 hidden nodes).
- Both trail strokes and node coordinates derive from the same smoothed canonical polylines, with measured maximum node-to-displayed-polyline error under **0.001 metre in the prototype geometry**. No independent sprite-dot offsets.
- Two visually separated fragments: **NO bridge, NO ford, NO connection across the rocky gap.**
- Route centerlines stay more than 70m from the V102 Fidlerbach source line in this art study. This is visual gap distance only; not measured bank width or safe crossing clearance.
- Real stream visual remains art-illustrated around the measured Fidlerbach centerline. Forests/rocks are artist-designed **not physically surveyed**.
- Every graph candidate stays **disabled** and no army movement mechanics or campaign saves were modified.

## Visual review artifacts (ChatGPT conversation files, NOT GitHub binaries)
- `century_oct001_artguided_comparison.jpg` — before/after split.
- `century_oct001_artguided_corridor_clean.jpg` — player-facing art proposal.
- `century_oct001_artguided_corridor_debug.jpg` — identical art plus candidate route dots and stop markers.
- `century_oct001_artguided_corridors.json` and `century_oct001_artguided_QA.json` — prototype line and validation evidence.
- `build_oct001_art_guided_corridors.py` — reproducible tool in conversation workspace.

The coordinate control anchors, PCHIP generation rule, and validation results are archived in `OCT001-ARTGUIDED-PROPOSAL-v1.json` in this folder. No production raster was committed to GitHub.

## Next *required* gate
1. Compare screenshot visually on a real iPhone. The edit is a **candidate visual direction**, not an approved map tile.
2. Obtain finer geographic terrain along the proposed terraces to check cliffs/grade; do not infer passability from attractive raster pixels. Keep impassable or unknown sections disconnected.
3. Align selected route corridor to *mapped geography* without changing the Fidlerbach control line or canonical octagon edges; certify crossings separately.
4. Only after this convert path to node graph for historical troop movement; stitch against Octagon 002 and the southeast connector.
5. Preserve Octagon 001 concept as the first art piece, V106 main preview and all original gameplay/saved campaigns unchanged.

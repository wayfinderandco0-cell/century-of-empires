# Octagon 001 — Route/river correction v2

**Development decision:** stop painting continuous roads across unverified or blocked terrain. The previous image showed a nearly continuous trail along Fidlerbach even where coarse DEM screening found severe grades. That visual implication was incorrect.

The revised study uses the same registered route and water coordinates as the hidden movement graph, but **shows only 13 preliminary candidate links as faint trail fragments**. It leaves **nine steep-slope links and one unverified water crossing** without a continuous visible trail. The developer image reveals these ten blocked links with red markers. The full 25-node graph and all 23 links remain **disabled in gameplay**.

**What is still unresolved:** The landscape illustration's rock cliffs and forest arrangement are not georeferenced to V97 measured relief. The retained ~160–230m DEM spacing is not enough to certify a real footpath, much less artillery access. The mapped waterways reflect modern natural-course guides, not independently verified 1800 positions. No bridge, ford or period road has been validated.

**Visual construction rule:** the landscape needs correct physical geography first; geographic streams and trail vectors then govern where river and trail art may be placed. Nodes follow those same candidate route centerlines. Do not independently invent a second visual trail. Tile borders and debug dots must remain invisible in the player view. An artistic backdrop cannot substitute for the missing terrain validation.

**Review artifacts (conversation files, not GitHub blobs):** century_oct001_screened_clean.jpg, century_oct001_screened_debug.jpg, century_oct001_screened_comparison.jpg, century_oct001_screened_QA.json, and build_oct001_screened_corridors.py.

**Next:** secure higher-resolution georeferenced Alpine terrain and authenticated passage information; create a full-bleed 1km piece with 60m bleed; validate exact water/path/rock positions and the eastern seam against Octagon 002; inspect iPhone portrait/landscape. Preserve V106 and original campaign saves.

# V235: correct false roadbed passes over sunlit tree canopy (ART RED)

October 27, 2026. Isolated development branch based on V234. No modifications to main, Matrei, V94 campaign/saves, V121/V123 road/bridge geometry, sprites or mechanics.

## Inspected actual CI evidence before changing code

V234 run 40467585495 completed its native source search and uploaded artifact 12717600769. Both crops *numerically passed* the old V232/V234 open-ground test: WEST 0.78333 open-roadbed and 8px obstruction; SOUTH 0.96107 open-roadbed and 0px obstruction. **These are false assurances.** Actual SOUTH screenshot shows the entire green V123 road painted over treetops, with blue lake visible behind. WEST screenshot shows a grassy slope and scattered trees, but no actual road or verified cartway/bridge. Neither photograph is Matrei, geographically registered, nor 1780 road evidence. V234's HSV mask admitted bright, low-saturation conifer foliage as open ground.

## Real code change

`scripts/v235_canopy_aware_native_art.py` replaces the full-original-photo crop selection's open-ground heuristic with a conservative sunlit-meadow mask. It excludes cool/low-saturation canopy and grey/dark non-ground, while retaining original unaltered photo pixels and exact pinned V123 routes. The same mask is applied during the full-photo search and final 25px road-shoulder inspection. Existing V234 crop code, SHA256/source attribution, original-pixel outputs, and source-graph pin remain intact. No artificial roadbed, pixel painting, scene warping, clone patches, new bridge or topology changes.

This is a **necessary conservative image preflight**, not validated semantic segmentation; it may reject legitimate brown-soil cartways and cannot prove navigability, historical geography, route registration, bridge banks, matching Matrei art, or period authenticity. V235 does not claim the color heuristic alone solves the actual landscape art requirement.

The new tests exercise a bright-conifer false positive that V234 accepted, positive meadow, original-source tampering, two-source distinctness and explicit RED approval. CI additionally downloads the **actual V234 candidate images** and checks the previous-vs-corrected classifications before searching both full original CC0 photos. Source authors/license and original hashes are carried forward from V234 (Stijn te Strake and Volker Schnäbele, CC0 1.0). The resulting screenshots and JSON are retained for human inspection.

## Remaining acceptance requirements

If SOUTH is rejected, do not try additional cosmetic crop adjustments on these photographs. Seek or compose a genuinely traversable and coherent source-proven landscape for SOUTH and WEST with distinct terrain, meaningful visible cartways and verified bridge approaches. Independently establish V209 natural geographic tiepoints or label the result fictional; do not call modern photography historical evidence. Only then integrate an isolated playable candidate, test the unchanged V203 strict 0.70/0.70 thresholds, four Chromium/WebKit portrait/landscape configurations, real iPhone review and explicit user approval. **Production approval stays false.**

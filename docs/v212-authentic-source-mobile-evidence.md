# V212 — authentic native Alpine source in real four-layout phone screenshots

Date: 2026-10-26. Isolated development branch from final V211 head `60d718dc`. No merge, deployment, payment, source-to-game warp, art modification, road/bridge/army movement change or saved-game change.

## Read before implementation

- GitHub issue #9 through V211 final comment 6413143894, V211 branch head and CI 40302601505. Source and V210 mobile-review UI tests passed, but inherited V203 strict photographic-detail gate failed 4/4 as required.
- Opened the **actual V211 WebKit portrait WEST/MATREI/SOUTH review screenshot**. The left panels show the genuine V192 game renderer (Western Pass and Southern Valley remain artificial). The right panels were explicitly synthetic CI placeholders, **not real Alpine pixels**. This meant the prior UI test could not prove the actual basemap source looked correct in a phone review.
- Inspected V204 original EPSG:3857 native XYZ downloader/sha manifest, V205 forest source plan, V208 frame mismatch and V209 evidence intake. Forest imagery is modern and approximately 3.578 km from the separate Matrei reference, and it is **NOT** registered to the original V121/V123 game frame.

## New code

`scripts/qa_v212_authentic_source_mobile.py` reuses the existing V204/V205 source downloader and SHA-256 verification to acquire the **12 original basemap.at JPEGs** (256×256 pixels, zoom 18), verifies the three contiguous native 512px source panels, then serves the exact original JPEG bytes to the unchanged V210 review UI in Chromium and WebKit, portrait and landscape. No synthesized tile pixels or JPEG transcoding. It captures the actual original V192 camera next to actual **modern** Alpine aerial source, checks all 12 exact XYZ URLs and all original image dimensions, and writes screenshots, source bytes, hashes, and a machine-readable report.

The new `.github/workflows/qa-v212-authentic-source-mobile.yml` preserves V204–V209 source/geographic gates, V121/V123 road/bridge and camera tests, and the independent V203 photographic-detail failure gate. The overall workflow is expected to remain **RED** until Western Pass/Southern Valley artwork genuinely improves.

## Critical limitations

The modern forest panels are **geographically separate reference imagery**, not registered game terrain. The modern tracks, forestry roads and date marks may remain. A genuine screenshot proves only the real source is visible in the review UI; it does **not** verify natural landmark matches, historical roads, 1780 vegetation, bridge-bank continuity, photo alignment or user acceptance. All approval flags remain false. This branch must never be merged into main or called production-ready without actual art replacement and user visual review.

## Verification

Initial CI: https://github.com/wayfinderandco0-cell/century-of-empires/actions/runs/40306833328 — **pending at authoring time**. Do not infer a pass. Inspect actual authentic-source screenshots and final job conclusions before claiming a verified milestone.

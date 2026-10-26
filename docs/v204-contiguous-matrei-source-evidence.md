# V204 — real contiguous Matrei-area orthophoto SOURCE grid (GAME ART UNAPPROVED)

Date: 2026-10-25 local / 2026-10-26 UTC.

## Why this branch exists

V203 actual WebKit/Chromium phone-layout screenshots show the WEST and SOUTH game art still has soft synthetic tree shapes, smooth fields and overly regular cartways. The stricter V203 photographic microstructure gate fails 4/4 browser/orientation configurations, with neighboring detail roughly 50–55% of the original Matrei photo. Passing route and camera tests does not change this finding.

V197/V199 authentic high-resolution reference samples were 5.8–10.8 km apart and are **not** adjacent game cells. V200 explicitly showed that this prevents claiming a seamless geographic continuation. V204 supplies a new, independently checkable **contiguous modern source reference** around the already identified V180 Matrei geographic anchor. It does **not** move the V121 original photograph, change the V123 route graph, or place modern aerial photography into 1780 game terrain.

## Actual source acquisition code

- Branch: `terrain-v204-contiguous-matrei-source-grid-20261025`, based on V203.
- `scripts/v204_contiguous_matrei_sources.py` builds three 512×512 native EPSG:3857 zoom-18 basemap.at source panels from **12 distinct real 256×256 JPEG tiles** around V180's independent modern Matrei-area anchor (11.45306°E, 47.13083°N).
- Reference panels share exact geographic borders: WEST → MATREI horizontally; MATREI → SOUTH vertically. The southwest quadrant is deliberately **unfilled**, not fabricated. The native geographic footprint, XYZ tile identity, JPEG hash and decoded RGB pixels are independently verified. No resampling, photo duplication, inpainting, invented roads or procedural trees.
- The L-shaped contact sheet includes required **Datenquelle: basemap.at** attribution and **CC BY 4.0** license. Modern buildings, highways, tracks, date imprints and other non-period features may remain; **none** is certified as period-safe artwork.
- `scripts/test_v204_contiguous_matrei_sources.py` includes synthetic negative controls for false period/game approvals, wrong EPSG, altered tile identities, modified native JPEGs, altered contact pixels, and source/atlas frame drift.
- `.github/workflows/qa-v204-contiguous-matrei-sources.yml` has separate source-acquisition and unchanged-game-visual jobs. The V203 screenshot structure gate remains **enforced and expected to fail** until real game art changes. A green source acquisition job must not be interpreted as a green game-art result.

## Non-negotiable limits

The three geographic reference panels are **not the V123 WEST/MATREI/SOUTH game octagon centers**; no game-to-real-world control points or source-to-photo homography have been established. The exact modern anchor is a source reference only. V97 DEM grid (~157×230 m), V102 modern material and V94 Europe atlas do not verify a historical bridge bank, road alignment, woodland in 1780 or road destination. Native modern imagery is not an authenticated 1780 reconstruction.

Immutable V121 original painting and V123 road/bridge/army geometry remain pinned by Git blob SHA; main, V94 campaign/saves, production and original preview are untouched. No paid service, merge or deployment.

**Acceptance flags:** sourcePanelsAreGameOctagons=false; v121PhotoGeoregistered=false; v123RoadsGeoregistered=false; modernFeaturesFullyExcluded=false; periodSafe=false; historicRoadsVerified=false; bridgeBanksVerified=false; gameArtApproved=false; physicalIPhoneApproved=false; productionApproved=false.

**Next:** inspect actual V204 source artifact and CI. Use the geographically contiguous source proof to plan period-safe natural-cover extraction and independently surveyed control points before any isolated playable art integration. Keep V203 visual gate RED until WEST/SOUTH genuinely improve and the user approves the actual phone visuals.

## CI and visual inspection

[Run 40268827843](https://github.com/wayfinderandco0-cell/century-of-empires/actions/runs/40268827843): **source-native-geometry job SUCCESS**; all four offline positive/negative unit tests passed, 12 actual native JPEGs downloaded and re-verified, artifact **12626758814** produced. The full workflow also contains a separate existing-game-visual-gate job; do not mistake source success for game-art approval.

Downloaded and opened the actual 1024×1086 source contact image from artifact 12626758814, not merely its manifest. The geographically contiguous Matrei anchor is **visibly unsuitable for direct historical game artwork**: the WEST source panel contains a major paved highway and 2023 date imprint; MATREI and SOUTH panels contain extensive modern buildings, a sports field/courts and urban streets. This is a useful **source exclusion finding**, not a playable terrain improvement. No inpainting or imaginary 1780 infrastructure was performed. Original RGB panels remain intact.

Manifest verification: WEST origin XYZ [139408,92062,18], MATREI [139410,92062,18], SOUTH [139410,92064,18]. All three real source footprints share exact edges; near-white fractions are 0.00012, 0.00055 and 0.00110. Source-edge RGB seam diagnostics are 7.9089 (west→center) and 4.6582 (center→south); these do **not** validate the original Matrei painting/game road seams. All geographic, period, historic-road, user-art and production approval flags remain FALSE.

**Next source decision (not user approval request):** exclude this built-up reference from candidate game terrain. Acquire an equally contiguous natural-cover reference around an already verified V197 forest source site, and independently survey actual game-to-geography tie points before any historical integration.

## Final V204 CI outcome
[Run 40268827843](https://github.com/wayfinderandco0-cell/century-of-empires/actions/runs/40268827843) completed with overall **FAILURE AS REQUIRED**: the modern geographic source job succeeded; the unchanged playable game job passed inherited V194 road-pixel, V202 bridge/road-tap and V192 screenshot-detail checks, then the **V203 strict photographic microstructure gate failed**, correctly rejecting WEST/SOUTH art. The failed job is not an error in the source mosaic. Source artifact 12626758814 was downloaded and visually inspected above. Source acquisition success does not override the red visual game gate.

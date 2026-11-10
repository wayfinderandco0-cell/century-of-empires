# Century of Empires — Geography-first redesign (ISOLATED EXPERIMENT)

**Branch:** map-geographic-redesign-matrei-20261110
**Started:** 2026-11-10
**Live game:** UNMODIFIED. **Old octagon approach:** REJECTED.
**Historical cartway:** PROVISIONAL. **Campaign integration:** NOT YET COMPLETE.
**Physical iPhone Safari:** NOT YET TESTED. **Public deployment:** VERIFIED hosted Chromium browser QA on 2026-11-10 (GitHub Pages).

## Verified isolated public demonstration

- Hosted page: https://wayfinderandco0-cell.github.io/century-of-empires/geo-preview/index.html
- GitHub Pages build: https://github.com/wayfinderandco0-cell/century-of-empires/actions/runs/42891898927 (success).
- External HTTPS and local browser QA: https://github.com/wayfinderandco0-cell/century-of-empires/actions/runs/42892291685 (success, latest tested branch source).
- Browser at 390x844: Chromium and WebKit render geography and terrain; selected test army marched on shown road; panning and zoom; two-contact simulated pinch raised zoom from about 10.6 to about 12.1. Real physical iPhone Safari STILL NOT tested.
- Separate main/geo-preview/ standalone three-file copy serves the experiment publicly; no saved campaign, production homepage or game rules were replaced. Dev branch and draft PR #27 remain isolated and unmerged.

## Decision

Adopt **MapLibre GL JS**, vector source/style from **OpenFreeMap**, and **Mapterhorn georeferenced DEM relief** for the narrow Wipptal/Brenner proof. The standalone index.html is a geography-first renderer and a navigation/selection demonstrator; it is NOT the production game renderer or an approved historical map.

Why:
- Visual terrain comes from one geographic coordinate system; invisible internal map tiles are not collage artwork.
- Elevation and mapped landcover persist across continuous camera zoom.
- Gold cartway and pathfinding/march interpolation share exactly the same WGS84 source vertices (corridor-data.js, road-graph.js).
- Geographic data can expand to European vector tiles and historically verified GIS without octagon seam logic.
- Browser rendering is MapLibre WebGL, with flat basemap as fallback if 3D terrain fails.

Alternatives evaluated:
- **Leaflet**: excellent low-footprint 2D and mobile gestures; less suitable for later DEM/pitched detail and extensive styled vector layers without plugins.
- **Custom canvas / three.js**: maximum control but requires rebuilding projection, streaming, labels, camera and terrain handling; high engineering cost.
- **Historical scanned map overlay**: useful as a cross-check and eventual period layer but sheets need dated provenance, georeferencing and image licensing.
- **Raw DEM Canvas**: a source layer, not a complete mapping camera/feature engine.

## Current demonstrator (NOT the saved campaign)

- corridor-data.js: real settlement locations and historically relevant north-south corridor with explicitly UNVERIFIED sketch vertices.
- road-graph.js: WGS84 road graph, shortest paths, nearest-segment snapping, arbitrary road point destinations, disconnection checks and interpolation.
- index.html: georeferenced OpenFreeMap style with modern road/label layers suppressed, DEM hillshade and optional terrain, the same road graph rendered on top, place markers, selected test army, touch destination, Execute, Halt, Reset, pan and pinch.
- test-road-graph.cjs: geometry and route regression assertions.
- browser_qa.py: automated Chromium and WebKit 390x844 iPhone-sized viewport smoke checks and screenshots.
- .github/workflows/qa-geographic-redesign.yml: isolated GitHub Actions regression and visual artifacts.

This demonstrator does NOT import saved-campaign armies, apply campaign access/war restrictions or preserve campaign game speed inside the test clock. The accelerated march is QA visualization only, not a change to the live game.

## Data provenance and limitations

1. MapLibre: https://maplibre.org/maplibre-gl-js/docs/ — open WebGL map/style layers.
2. OpenFreeMap: https://openfreemap.org/quick_start/ — modern OSM-derived geographic landscape. Current roads and labels are hidden; still not an 1780 reconstruction.
3. Mapterhorn: https://mapterhorn.com/data-access/ and https://mapterhorn.com/attribution — georeferenced DEM. Review source attribution and hosted service terms before production or redistribution.
4. Matrei corridor history: https://www.wipptal.at/en/your-wipptal/the-wipptal-valley/matrei-am-brenner — Matreium is documented on Roman north–south route; this does NOT verify our centerline.
5. Gazetteers: https://www.geonames.org/2781423/brenner-pass.html ; https://www.geonames.org/2764557/steinach-am-brenner.html ; https://www.geonames.org/2765715/schoenberg-im-stubaital.html ; https://en.wikipedia.org/wiki/Matrei_am_Brenner — locality positions, NOT 1780 road surveys.

No claims of verified period cartway path, bridges, historical settlement extents or borders. Some straight stretches may cut across implausible terrain. Before historical certification: locate dated archives, georeference the period roads, add accurate vertices and bridge locations, verify each crossing against DEM and published historic maps, mark every segment with provenance.

## Existing game preservation

Current main index.html uses saved-state and orders (save, restore, routeLength), with nation/province campaign systems. v94.html and v94-geographic-engine.js hold an alternative full-European map and geographical engine. Prior map-reset/road-engine.js uses tile-local pixel coordinates and is not copied to the new geographic engine. No existing game files have been modified.

The production adapter must:
- Map existing province and town IDs onto authoritative coordinate records without changing IDs.
- Replace only renderer and georeferenced road geometry, leaving existing game commands and mechanics authoritative.
- Delegate selection, movement rules, ETA, combat and economy to the established game; do not carry over this QA animation clock.
- Preserve save shapes and progression. Run saved-game regressions.
- Reuse existing army sprites and controls rather than the test marker.

## Acceptance gates

1. Node geographic graph tests AND browser iPhone-sized visual QA with screenshots.
2. Physical iPhone Safari pan, pinch, WebGL/DEM and performance review.
3. Independently hosted HTTPS preview, URL actually loaded and movement actually verified.
4. Historically sourced, audited cartway/bridge alignment for period and pass.
5. Existing saved campaign and unit integrations, save and mechanics regression, and user visual approval.

Do not merge until approved. No more octagon fixes, photo stitching or unrelated map experiments. Do not expand to Europe before the narrow prototype is a genuine integrated playable slice.

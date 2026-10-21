# Century of Empires — V116 Hour 7 road-graph checkpoint (2026-10-21)

**Safe working branch:** \`terrain-v116-hour7-roadgraph-proof\`, forked from \`terrain-v116-hour6-route-art-integrity\` at \`785e41cbe467c2bbe444a0aa1e193f7181c1d6bc\`.
**Main/live game and existing saves:** untouched. This is a proof, not a finished playable octagon or production deployment.

## Accomplished
1. \`scripts/v116_road_graph.js\`: reusable source-pixel road graph with a common approach, one fork, south branch, and bridge branch. Movement is constant physical art-pixel distance per second, independent of branch length. Switching before the fork preserves world position; after the fork it is blocked. Motion clamps at each visible terminal rather than silently returning to route start. Candidate geometry cannot grant conquest/traversability.
2. \`v116-shared-roadgraph-army-proof.html\`: self-contained original V115 painting, existing seam-safe renderer, latest candidate centerline (yellow), discarded bridge detour for visual comparison (cyan), road-bound unit, March/Halt, explicit Reset, route selection and four close-art inspections. Interactive iPhone-style dock is a single row with hidden Options. Bridge camera is clamped to source artwork; no artificial off-image band is permitted in its focus preset.
3. \`scripts/build_v116_candidate_tile_index.js\` / \`terrain-grid/v116-candidate-route-tiles.json\`: re-derived 48 local-tile corridor coverage from the corrected bridge graph. The obsolete bridge-detour-only tile \`local-r05-c02\` is no longer marked as bridge-route candidate. All 48 remain non-traversable, non-conquerable, not deep-zoom eligible. Original source image pixel crops, V94 world mapping and terrain map remain unchanged.
4. \`tests/test_v116_road_graph.js\` and \`tests/test_v116_route_tile_coverage.js\`: regression suites for shared fork, geometry, stationary selection, terminal stops, artifact/index consistency and nonproduction safety.
5. \`scripts/qa_v116_road_graph_browser.py\` and \`.github/workflows/qa-v116-roadgraph.yml\`: real browser automation against the actual embedded JPEG (NOT synthetic test art).

## Validation evidence
- GitHub Actions **passed**: https://github.com/wayfinderandco0-cell/century-of-empires/actions/runs/39625771119
- Node road-graph, candidate tile-coverage and earlier renderer tests passed on hosted CI.
- Chromium AND WebKit tests passed at **390×844 portrait** and **844×390 landscape**, no JavaScript errors. Four screenshots plus machine-readable report were uploaded in the Actions artifact.
- Tested route button selection, fork-lock rejection, unchanged world position during pan, compact controls, bridge focus camera fully within actual painting, renderer coordinates and 48 local tiles.
- Earlier independent real-photo landmark measurement: five *manually chosen artwork* references yielded revised mean 0.88 px vs old mean 20.84 px. This is visual candidate evidence, **not** GIS/historical road certification.
- Chromium/WebKit emulation is NOT a physical iPhone Safari test. Screenshots prove framing/rendering but do not independently validate geographic history.

## Not done — DO NOT DECLARE FIRST OCTAGON COMPLETE
- The painted bridge stops on the visible far bank at V115 art pixel \`[699,799]\`. Beyond-bank road, terrain continuation, valid movement to next strategic cell, and historical route evidence are all **unverified**. Never invent road or draw an unsupported continuation.
- South branch is not independently validated against visible cart track.
- One original 1100×842 illustration and its 48 **subdivisions** are not 48 unique high-resolution terrain scenes; 432 parent Europe cells are an index only, not completed polygon/octagon artwork or traversable strategic provinces.
- No production units, combat penalties, occupation, game state, or save migration were changed.
- Four interactive artwork inspection presets are not yet all four geographically continuous Europe→region→pass→town game zoom levels.
- No user physical iPhone review, production merge, deployment or playable strategically connected route yet.

## Required next work
1. Obtain geographically supportable, visually continuous road approaches **on both sides** of the Brenner-region bridge; build/verify the missing far-bank portion as source art + graph together. Do not fabricate history.
2. Prove visible uninterrupted route from the northern approach, through town and stone bridge, **past the far bank to a real accessible terrain exit**. Validate pixel-level centerline, source-world registration and progression across neighboring eligible child/parent cells.
3. Test the finished passage on a physical iPhone and across the true four levels, including UI and army unit tracking, before approving one octagon for reuse.
4. Only after that, reuse this tested architecture for other **eligible** road cells. Scenic villages are not conquest targets, wilderness cells not automatically traversable.

**Access**: Source page \`v116-shared-roadgraph-army-proof.html\` on this branch; latest QA workflow packages the single self-contained HTML in its screenshot artifact for offline testing.

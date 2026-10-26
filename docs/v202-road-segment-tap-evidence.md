# V202 — closest painted-segment road taps (isolated, not approved)

Date: 2026-10-25 (America/Chicago; CI 2026-10-26 UTC)

## Starting evidence
- Read issue #9 through V201, including V200 geographic-registration blockers.
- Inspected V201 CI run 40253898958, four successful mobile-browser configurations, and downloaded actual artifact 12622145798.
- Opened the WebKit portrait WEST/MATREI/SOUTH screenshots. WEST/SOUTH still show artificial conifer blobs and regular cartways; Matrei is substantially more photographic.
- Read original V123 graph, V152 terminal-survey guard, V97 Copernicus and V102 material manifests, and V201 gesture/cache QA. V94 is geographically registered for its own atlas, **not** a proven V123 painting-to-EPSG transform.
- Verified V201 isolated head 2aeec2b8; main/live, V94 saves/campaign, V121 painting and V123 atlas were not changed.

## Actual code
- New isolated branch `terrain-v202-road-segment-tap-safety-20261025`, based on V201.
- Updated `v192-weathered-cartways-graphics-test.html`: tapping a visible road now finds the closest **painted segment**, then routes to an original V123 endpoint of that segment. The previous global nearest-vertex search could choose a vertex belonging to a different painted road near the Matrei bridge. No new roads, nodes, bridge crossings, extensions, or historical claims.
- Independent geometric scan of the actual V121/V123 coordinates found at least **9** sampled locations within 40 world units where the old global nearest vertex differed from the closest-segment endpoint. Two concrete bridge-neighborhood examples are world `[2072,496]` (correct original bridge vertex `[2054,519]`, old selection `[2052,491]`) and `[2080,488]` (correct `[2102,508]`, old `[2052,491]`). These are preview-world coordinates, not geographic coordinates.
- Added `scripts/qa_v202_road_segment_taps.py`: independently reconstructs V123 roads from immutable V121 controls, tests 24 exact painted-segment taps per phone configuration, checks the two bridge-neighborhood counterexamples, rejects taps beyond both unsurveyed outer termini, tests mid-edge halt/reorder and road coincidence, locks original V121/V123 Git blob SHAs, and saves WebKit/Chromium screenshots.
- Added `.github/workflows/qa-v202-road-segment-taps.yml`: retains inherited road-pixel, route/halt, strict 3-center image detail, camera/pinch, static cache and touch cache checks; adds V202 test in all four phone-layout browser configurations.

## Verification
- First V202 CI run [40258722069](https://github.com/wayfinderandco0-cell/century-of-empires/actions/runs/40258722069) **PASSED** all inherited QA and 24 road-tap samples in each of four Chromium/WebKit × portrait/landscape configurations. Downloaded artifact 12624250308; opened actual new WebKit West/South screenshots. Road movement is preserved, but neighbor art still looks synthetic.
- Follow-up code commit adds two explicit bridge-neighborhood regressions. Final run [40258788180](https://github.com/wayfinderandco0-cell/century-of-empires/actions/runs/40258788180) is **pending at the time of this note**; do not report it as passed without checking.
- Passing headless phone-layout tests are not physical iPhone acceptance.

## Remaining blockers
`gameArtApproved=false`, `historicalRoadsVerified=false`, `physicalIPhoneApproved=false`, `productionApproved=false`.

WEST/SOUTH still require authentic geographically coherent, period-safe visual material; Matrei photo seam, bridge banks and outward destinations remain unverified; no exact 1780 geography or 4-tier V100 art approval is claimed. Keep source-derived modern aerial crops out of invented V123 positions until independent registration. Do not merge/deploy to main.

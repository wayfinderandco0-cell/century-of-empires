# V213 — native geographic coordinates for authentic modern Alpine source (NOT game registration)

Date: 2026-10-26 UTC. Isolated branch `terrain-v213-native-source-geodesy-20261026` based on V212 `a5a4924b`. No main merge, deployment, paid source, save/campaign modification, V121 original Matrei photo change, V123 road/bridge/army graph change or production edit.

## Verified baseline before code

Read GitHub issue #9 through V212, current V200–V212 branches, V212 CI run 40306875018 and its three jobs and source/art artifacts. Opened the actual V212 WebKit portrait WEST/MATREI/SOUTH contact screenshot: the left panel shows the real game renderer with visibly artificial West/South terrain; the right panel shows authentic modern 2023 basemap.at forest tiles, which are geographically separate and contain modern tracks. Source and mobile capture jobs were green; inherited road/camera tests green; the strict V203 photographic-detail gate remains RED 4/4. Reviewed V94 geographic atlas, V97 Copernicus/ESA manifest, V102 Navis material manifest, V123 original geometry, V204/205 native XYZ origins and V209 independent landmark intake.

## New engineering deliverable

- `terrain-grid/v213-source-geodesy.js`: deterministic native zoom-18 EPSG:3857 XYZ pixel to WGS84 longitude/latitude converter. It preserves native 256-pixel tile identity and rejects nonfinite coordinates, points outside the actual 512-pixel source panel and unknown cells. The three panels remain an L-shaped **modern reference**; coordinates never claim V121/V123 geographic registration.
- `v213-landmark-geographic-review.html`: separate mobile review copy of the actual V210/V211 interface, still rendering the original V192 camera and the 12 unchanged modern native source JPEGs. Shows a clearly labeled modern source WGS84 center, and records WGS84 + native XYZ with each **UNVERIFIED** visual candidate. It never treats a tap or visual resemblance as an independently surveyed landmark or an authenticated 1780 feature.
- `scripts/test_v213_source_geodesy.js`: independent center-coordinate fixtures, native tile identities, both source-panel geographic seams, invalid input and unapproved-state guards.
- `scripts/qa_v213_geo_review_ui.py`: four Chromium/WebKit phone layouts, labeled SYNTHETIC source tiles only for UI negative controls; verifies real game camera and exact quantized touch mapping.
- `scripts/qa_v213_authentic_geo_mobile.py`: four phone layouts with 12 ORIGINAL SHA-256-audited native modern source JPEGs; exercises geographic readout and clears the artificial QA gesture before saving genuine aerial-source screenshots.
- `.github/workflows/qa-v213-native-source-geodesy.yml`: retains all V204–V209 evidence tests, original V192/V194/V201/V202 road/bridge/camera tests, and fail-closed strict V203 photographic art gate. The latter must remain RED until real West/South artwork improves.

## Independently checkable source-panel centers

Coordinates below are **modern source** WGS84, not game locations:

| Panel | Source center longitude E | Latitude N | Native XYZ |
| --- | ---: | ---: | --- |
| WEST | 11.4353942871 | 47.1000446940 | 139399 / 92096 / 18 |
| MATREI reference | 11.4381408691 | 47.1000446940 | 139401 / 92096 / 18 |
| SOUTH | 11.4381408691 | 47.0981750071 | 139401 / 92098 / 18 |

Adjacent source edges are contiguous by native XYZ coordinates. This does **not** imply adjacent game-art seams, historical road continuations, exact 1780 geography or any correspondence between source and painted Matrei.

## Acceptance and next work

The independent V209 manifest remains empty: `BLOCKED_MISSING_REAL_TIEPOINTS`. Real natural landmark matches with independent source/game evidence and held-out validation are still required. The forest source remains about 3.578 km from the independent modern Matrei reference. Do not insert these modern forest panels into playable West/South, distort them, paint imaginary road endpoints, or waive strict photo QA.

`sourceRegisteredToV123=false; historicalRoadsVerified=false; bridgeBanksVerified=false; gameArtApproved=false; physicalIPhoneApproved=false; productionApproved=false`.

**CI result:** check the new branch's V213 workflow; this document does not preclaim passing browser/art tests. Next unblocked work is independently identifying stable natural landmarks or proving that the original painted Matrei cannot be registered to source imagery; only then plan geographically defensible period-safe terrain placement.

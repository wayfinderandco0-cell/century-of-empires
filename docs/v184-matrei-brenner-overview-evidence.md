# V184 — native Matrei–Brenner modern overview, coverage NOT approved

**2026-10-25.** Source geography advanced; historical GAME art and physical iPhone acceptance remain RED.

## Evidence inspected before coding
Read [issue #9](https://github.com/wayfinderandco0-cell/century-of-empires/issues/9) through V183 and successful [V183 CI 40188840123](https://github.com/wayfinderandco0-cell/century-of-empires/actions/runs/40188840123). Downloaded and opened actual [V171 WebKit portrait GAME screenshot](https://github.com/wayfinderandco0-cell/century-of-empires/actions/runs/40142947845/artifacts/12578863866): only the Matrei island is detailed; neighbors synthetic and road ends unverified. Downloaded/opened actual [V183 Brenner source image](https://github.com/wayfinderandco0-cell/century-of-empires/actions/runs/40188840123/artifacts/12596622517): modern railway yard, roads, buildings and 2023 labels, not period game art.

## New isolated development
[Branch terrain-v184-matrei-brenner-overview-20261025](https://github.com/wayfinderandco0-cell/century-of-empires/tree/terrain-v184-matrei-brenner-overview-20261025).

- [Source generator](../scripts/v184_matrei_brenner_overview.py): deterministic native EPSG:3857 zoom-14 rectangle with one-tile padding around independent V179 Matrei and Brenner anchors. **5 columns × 12 rows = 60 distinct basemap.at JPEGs**, 256 native pixels each; **1280 × 3072** source image. Bounds **11.425781–11.535645 E, 46.980252–47.159840 N**. Modern regional SOURCE only, not surveyed historic road or close-up game art.
- [Eleven synthetic fail-closed tests](../scripts/test_v184_matrei_brenner_overview.py): anchor coverage, 60 unique tile positions, 103 neighboring seams, source JPEG/composite integrity, missing/tampered source, forged historic roads, bridges, GAME approval and false geographic coverage.
- [Dedicated CI](../.github/workflows/qa-v184-matrei-brenner-overview.yml) preserves V172/V178/V179/V180/V183 regression suites. First run 40193345580 failed on a transient provider socket timeout after 55 downloads; source downloader now retries network timeouts. [Final Actions run 40193742019](https://github.com/wayfinderandco0-cell/century-of-empires/actions/runs/40193742019) **SUCCESS**, 11/11 new tests, 60 actual source downloads, pixel/hash validation and strict non-approval assertions.
- Downloaded and opened the [actual 60-tile final artifact 12598932191](https://github.com/wayfinderandco0-cell/century-of-empires/actions/runs/40193742019/artifacts/12598932191). All **60 source JPEG SHA256 values distinct**. **48 horizontal + 55 vertical source tile pairs**; mean native-edge RGB differences **11.7568 / 12.3411**. Source adjacency is NOT GAME seam acceptance.

## Crucial image finding — incomplete provider coverage
The actual overview has a **large irregular near-white wedge at the southern end**, visually resembling missing provider imagery. An audit found **754 / 1280** south-border pixels and **8673 / 49280** sampled southern-fifth pixels near white. The detector flags suspected provider no-data, but does NOT assert a definitive classification of snow versus provider no-data, erase pixels, or invent replacement landscape. All 60 JPEG files exist, but usable modern source coverage remains **UNAPPROVED**. Manifest requires source coverage approval FALSE and visual review TRUE; this prevents a technically complete tile download from being mistaken for complete geographic artwork.

## Next action and hard limits
Independently obtain and review a licensed alternative natural-terrain source for the suspected southern no-data wedge. Do not copy/repeat neighboring terrain. Separately establish three intended GAME octagon footprints and period-specific historic road/bridge-bank control points; modern imagery cannot certify 1780–1880 roads. Then register imagery and create credible historical art, rerun unchanged V140/V171 four-browser GAME detail/seam/route/army/pinch tests, and require actual user iPhone visual approval.

**No main/live/V94 saves/V121 original painting/V123 graph edits, no merge/deploy or expenses.** All historic, route, bridge, GAME, physical-iPhone and production approvals remain false. Attribution: **Datenquelle: basemap.at**, CC BY 4.0.

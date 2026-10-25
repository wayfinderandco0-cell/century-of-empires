# V183 — Brenner Pass native geographic source study (2026-10-25)

**Branch:** `terrain-v183-brenner-pass-source-20261025` (isolated from production). No changes to `main`, V94 campaigns/saves, V121 original painted terrain, or V123 road/bridge control points.

## Reason for this step

V178–V182 established that the Navis source L (about 1.25 × 0.83 km) is not a credible substitute for the separate Matrei/Western Pass/Southern Valley GAME cells. V180 acquired an independent 18-JPEG modern Matrei-area orthophoto; V181/V182 conservatively masked some contemporary infrastructure and source date stamps without reconstructing the landscape. The Southern Valley and Western Pass GAME geographic footprints remain **unresolved**. V171 GAME screenshot acceptance remains **0/4**, not superseded by successful source tests.

V183 acquires a **separate modern Brenner Pass geographic reference**, using the independent V179 saddle anchor (11.50750 E, 47.00333 N). It composes nine unique native basemap.at zoom-17 256px JPEGs into a 768 × 768 pixel source study, preserving geographic coordinates and original pixels. This does **not** create or claim a southern GAME octagon, a Matrei-to-pass contiguous art corridor, or a historic road. The V183 source lies many kilometres from Matrei; any geographic gap remains unacquired.

## Period context and strict limits

- The Habsburg historical resource [*Through the Monarchy by mail coach — Improvements to the road network*](https://www.habsburger.net/en/chapter/through-monarchy-mail-coach-improvements-road-network) describes Brenner Pass road improvements around the turn of the 18th/19th centuries and considerable trade traffic by 1800. It supports **a period-era transit corridor**, not a surveyed polyline, exact bridges, or V123 game geometry.
- A [2018 regional account of historian Hubert Held's Brenner routes lecture](https://www.meinbezirk.at/stubai-wipptal/c-freizeit/verkehrswege-ueber-den-brenner-eine-zeitreise-von-innsbruck-und-hall-ueber-den-brenner_a2438419) describes a 1777 improvement under Maria Theresa, while warning that earlier routes are only partially historically established. This also **cannot** establish exact road alignment or a specific bridge.
- The independent modern pass anchor comes from V179 and is not a 1780 road control point. Modern source roads, rails, roofs and border infrastructure are **not approved** as historic game features.

Source: [basemap.at orthophoto](https://basemap.at/orthofoto/), CC BY 4.0; required credit: **Datenquelle: basemap.at**. The source tiles are modern reference material, not production artwork.

## Engineering checks

- `scripts/v183_brenner_pass_source.py`: native XYZ tile origin, 9 source hashes, exact source-image recomposition, four adjacent boundary diagnostics, source attribution and false approval fields.
- `scripts/test_v183_brenner_pass_source.py`: eight synthetic tests reject changed anchor, reused Matrei location, fake historic polyline, missing/modified JPEGs, modified mosaic and forged approvals.
- `.github/workflows/qa-v183-brenner-pass-source.yml`: preserves V172/V178/V179/V180 regression suites, runs eight V183 tests, acquires nine real tiles and uploads the inspectable SOURCE-only image. A green CI run proves source acquisition integrity only.

**Local validation:** eight V183 synthetic tests passed (2026-10-25). CI must independently confirm live source acquisition; no CI claim before observing its result.

## Acceptance status and next step

`sourceSectorsAreGameOctagons=false`, `v121ToGeographyRegistered=false`, `v123RoadsGeoregistered=false`, `historicalRoadsVerified=false`, `bridgeBanksVerified=false`, `historic1780Certified=false`, `periodArtComplete=false`, `physicalIPhoneApproved=false`, `productionApproved=false`.

**Next:** inspect actual Brenner source CI image for provider coverage/modern infrastructure; independently locate the intended three GAME cell footprints and historic road/bridge bank tie points. Do not stretch nine source tiles to fill a missing 13+ km corridor. Only after source and period alignment should connected GAME art and original four-browser visual/movement gates be rerun. No release without user approval.

## Verified GitHub Actions and actual image review

- [V183 run 40188840123](https://github.com/wayfinderandco0-cell/century-of-empires/actions/runs/40188840123) **SUCCESS** at code/workflow commit `b01ba050`: preserved V172/V178/V179/V180 regressions, all eight V183 tests, real nine-JPEG acquisition, exact PNG verification and approval safeguards.
- Downloaded and opened the **actual** [source artifact 12596622517](https://github.com/wayfinderandco0-cell/century-of-empires/actions/runs/40188840123/artifacts/12596622517). All nine native JPEG hashes are unique; the 768×768 mosaic hash matches the manifest. Geographic bounds are **11.502686–11.510925 E, 47.000861–47.006480 N**; the independent Matrei anchor is **14.765 km** away in a straight line. Four measured native source boundaries have mean RGB differences **14.4605, 12.1571, 8.7370, 8.6441**. These are source-image seam diagnostics, NOT GAME seam acceptance.
- **Actual visual finding:** This Brenner Pass tile study is dominated by a large modern railway yard, platforms, roads and interchange, buildings and visible “2023” imagery stamps. Authentic surrounding forest is present, but this particular image cannot be painted directly as 1780–1880 GAME art. Do not mask away most of the image and pretend the resulting gaps are finished terrain.
- Also downloaded/opened the rejected [V171 WebKit portrait whole-crossing GAME screenshot artifact 12578863866](https://github.com/wayfinderandco0-cell/century-of-empires/actions/runs/40142947845/artifacts/12578863866). The central Matrei photo remains a small detailed island; Western Pass and Southern Valley remain stylized/synthetic, with question-mark road ends. V183 source integrity does not repair that screenshot or change the unchanged V171 0/4 GAME visual acceptance.

**Updated next action:** Research a period-specific Brenner road map or surveyed alignment with bridge banks; identify historic natural terrain/landmarks and source images outside the contemporary railway footprint. Independently locate all three GAME cells and acquire the *continuous* actual terrain footprint before any V121/V123 geographic registration. No invented route connection or premature GAME approval.

# V227 — Full-cell original artwork import, isolated development only (2026-10-26)

**Status: engineering experiment. No new WEST/SOUTH artwork has been approved, and production remains RED.**

## What changed in executable code
- `terrain-grid/v227-art-ingest.js` accepts **two distinct, local, native 1536×1024 PNG/JPEG/WebP images**, independently for WEST and SOUTH. It validates file type/size, SHA-256 when an expected digest is supplied, original V226/V123 route-point hashes (all interior points), tile origin and canvas size. Image bytes never leave the iPhone/browser; there is no upload, purchase or production state mutation.
- `v227-original-artwork-import-study.html` is an **opt-in iPhone-openable game workbench** built on V226, with load/reset controls. The imported images replace only the two neighboring **art layers**; original Matrei, graph-locked cartways, army sprites, movement, saved campaigns and the V226 art-clearance guide remain intact.
- `scripts/test_v227_art_ingest.js` includes negative controls for forged approval, changed road interior, wrong dimensions, source SHA mismatch, wrong format and invalid cell. The importer rejects source files that do not meet the native-size contract.
- `scripts/qa_v227_art_ingest.py` runs **Chromium/WebKit × portrait/landscape**, imports two *synthetic test-only* image fixtures, captures actual rendered before/after screenshots, checks Matrei center preservation and verifies original road/army geometry. Test fixtures are **not game artwork** and must not be shipped.
- `.github/workflows/qa-v227-art-ingest.yml` retains inherited V137/V202 tests, original strict V203 thresholds on rejected V225 game art, and an intentionally failing human/production approval job.

## Why this is not a finished landscape
V226 proved a wide road shoulder cannot disguise false road-over-canopy rendering. No complete source-backed, Matrei-compatible original WEST and SOUTH paintings have yet been authored or verified. Importing arbitrary images does not solve perspective, bridges, real cartway grounding, natural bank transitions or source/game tiepoints.

The importer **never** infers licenses from image filenames and sets `licenseVerified=false` for all local files. `sourceRegisteredToV123`, `historicalRoadsVerified`, `roadClearanceVerified`, `bridgeBanksVerified`, `periodSafe`, `humanVisualApproval`, `physicalIPhoneApproved`, and `productionApproved` all remain **false**. The default diagnostic V224 Kosovo photographs are still rejected, and must not be mistaken for 1780 Austria.

## Correct next integration step
Produce two **original, independently sourced or authored** full-cell 1536×1024 landscapes with consistent Matrei oblique camera, source attribution/license records, and visible **physical cartways grounded on the exact V123 path**, plus believable bridge banks. Import both in the V227 workbench and review actual phone screenshots before accepting them. Independently reconcile V209 natural tiepoints; if impossible, keep terrain illustrative and historical registration blocked. Only after four-browser road/army, strict V203, seam and human visual tests pass should user approval be requested. Never infer user acceptance from automated thresholds.

**Preserved:** V121 Matrei original painting, V123 graph, V94 campaign, saved games, original army sprites, main, production. No deployment or merge. No paid services.

`sourceRegisteredToV123=false; historicalRoadsVerified=false; licenseVerified=false; bridgeBanksVerified=false; roadClearanceVerified=false; periodSafe=false; gameArtApproved=false; physicalIPhoneApproved=false; productionApproved=false`

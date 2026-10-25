# V198 — transparent quarantine of modern-source marks (25 October 2026)

**Status: source-reference preparation only. Not GAME art, not period-safe, not three approved octagons.**

## Evidence inspected before editing
- Issue #9 through V197 and latest V197 source CI [40235172113](https://github.com/wayfinderandco0-cell/century-of-empires/actions/runs/40235172113).
- Downloaded/opened real V196 WebKit portrait WEST, MATREI and SOUTH game close-up screenshots from [artifact 12612664822](https://github.com/wayfinderandco0-cell/century-of-empires/actions/runs/40230561361/artifacts/12612664822). WEST/SOUTH are still synthetic soft-tree surfaces beside the detailed original Matrei painting. The outer road endpoints remain unsurveyed.
- Opened real V197 1536×554 modern-source contact image. Its three independent 512px areas contain recognizable **year stamps**, one bright track at the western edge and two bright tracks in the southern reference patch. These are *not* V123 game octagon centers.
- Verified V197 original source and attribution: **Datenquelle: basemap.at, CC BY 4.0**.

## Implemented in isolated V198 branch
- `scripts/v198_period_exclusion_masks.py`: explicit conservative pixel-coordinate polygons/rectangles quarantine the visible date imprints and **suspected** modern tracks. Track classification is intentionally uncertain: absence from an 1780 route map is **not** inferred.
- Every 512×512 source pixel retains its exact original RGB value. Suspect pixels are given **alpha=0** (no inpainting, color replacement, or fabricated forest). The separate contact preview colors quarantined regions red for inspection.
- Every source JPEG/PNG, V197 manifest, new mask, transparent image, and review contact is hash-checked and independently re-rendered. Metadata refuses period/game/route/bridge/physical-iPhone/production approval.
- Nine fail-closed tests cover bounds, masks, RGB preservation, provenance, forged approvals, corrupted originals, tampered transparency/masks/contact and overbroad blanketing.
- After inspecting the *actual first-run artifact*, expanded two conservative track polygons to cover remaining visible white edges, then locked two boundary pixels in regression tests.

## Final CI and actual artifact
- [Final V198 run 40240240317](https://github.com/wayfinderandco0-cell/century-of-empires/actions/runs/40240240317) **PASS**: 8 inherited V197 tests + **9 V198 tests**; 12 authentic JPEG downloads, full original verification, exclusion rendering and exact pixel/hash verification.
- [Artifact 12616931804](https://github.com/wayfinderandco0-cell/century-of-empires/actions/runs/40240240317/artifacts/12616931804) downloaded and its final 1536px red exclusion contact opened/inspected.
- West **6,029** pixels quarantined (**2.30%**); East **1,291** (**0.49%**); South **7,097** (**2.71%**). Remaining source pixels are unmodified, not certified historical.
- Branch source commit [4d87f40c](https://github.com/wayfinderandco0-cell/century-of-empires/commit/4d87f40cc282c6c64cba0151e3c8ad1554c4c07a). No production merge, deployment, V121 original painting edit, V123 route/crossing edit or V94 campaign/save edit.

## Still blocking GAME art acceptance
These quarantined images **contain transparent holes** and potentially other unreviewed modern traces. They are not playable terrain and must never be directly pasted over Matrei. To progress: (1) source-supported historical/land-cover reconstruction for holes, **without inventing roads**; (2) independent georegistration of the actual three V123 game footprints and bridge banks; (3) render source-derived west/south art into an isolated V196-derived game trial; (4) run strict V189/V171 image parity and 4-browser movement/route gates; (5) inspect all iPhone screenshots and obtain user visual approval. Do not lower thresholds or confuse source reference with 1780 geography.

`gameArtApproved=false; gameOctagonsGeoregistered=false; historicalRoadsVerified=false; bridgeBanksVerified=false; physicalIPhoneApproved=false; productionApproved=false`.

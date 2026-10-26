# V201 — real iPhone-style pan/pinch static-terrain cache repair (2026-10-25)

**Status:** isolated development branch only; mobile-browser technical QA PASS; GAME ART and historic geography NOT approved.

## Prior evidence inspected

- Issue #9 through V200; V196 source and V196 CI run 40230561361.
- Downloaded and inspected actual V196 WebKit portrait/landscape WEST, MATREI, SOUTH game screenshots (artifact 12612664822). Matrei's sharp original photo contrasts with blurry repeated West/South conifers and overly uniform roads. The three GAME octagons remain visually rejected.
- V200 geographic SOURCE work (run 40249255793) places authentic modern Alpine source crops kilometers apart; none is registered to the V123 game cells. No image substitution was attempted.
- The V196 static terrain snapshot is rebuilt by zoomTo/inspect, but the canvas's **real pointermove handlers changed the camera/scale without setting staticDirty**. Previous QA tested scripted zoomTo, not actual touch pointermove cache invalidation. On a real gesture, army/UI could update while the underlying landscape remained frozen.

## Implemented

- [V201 code commit b3148284](https://github.com/wayfinderandco0-cell/century-of-empires/commit/b314828413123e84cf0752d37660a50490dbd46f) invalidates the static terrain cache during one-finger pan and two-finger pinch. The cached static layer still remains reusable during army-only motion.
- [V201 four-browser QA commit d6636b9e](https://github.com/wayfinderandco0-cell/century-of-empires/commit/d6636b9ea4433dd2f2c614ba81ec2eada262d1d7) dispatches actual PointerEvent sequences, captures BEFORE/AFTER screenshot pairs, verifies landscape pixel changes, anchored pinch, camera clipping, unchanged V123 road alignment and army-only cache reuse.
- [V201 CI commit 671cc5c7](https://github.com/wayfinderandco0-cell/century-of-empires/commit/671cc5c78be145dc6cb9ff0fce54283a0f5c79e9) runs inherited road-pixel, crossing/march, three-center image detail, camera bounds and V196 cache gates before V201.

## Verified CI and screenshots

[GitHub Actions run 40253898958](https://github.com/wayfinderandco0-cell/century-of-empires/actions/runs/40253898958): **SUCCESS** in all four browser/orientation combinations (Chromium/WebKit × 390×844 portrait and 844×390 landscape, DPR 2).

[Actual screenshot and JSON artifact 12622145798](https://github.com/wayfinderandco0-cell/century-of-empires/actions/runs/40253898958/artifacts/12622145798) was downloaded and inspected. In the test's header/footer-excluded terrain region, a real simulated pan changed 86.99–92.00% of pixels; pinch changed 87.11–91.92%. The static cache rebuild counter increased after both gestures in **4/4** cases; the zoom anchor remained centered and army motion still reused the cache while staying on V123 road polylines. These are browser screenshot differences, not proof of geographic fidelity or improved graphics.

Original Git blob hashes remained:
- V121 painted 1536×1024 photo: 4c6aa5cda9e7c359b6d2a49d5b5fe8a597346382
- V123 atlas and road/bridge graph: 09f04b4062e24fbacbb645307462cdddce2b2aa3

**No main/live/campaign/save edits, no deployment, no source-geometry modifications and no external cost.**

## Still blocked / next

- WEST and SOUTH artwork remains visibly synthetic next to the preserved Matrei photograph; passing screenshot-change and numeric detail tests does not equal visual acceptance.
- The original V121 photo is not independently registered to modern geography. V200 modern source sites are not V123 GAME octagon centers. No false 1780 roads, bridges, settlements, or source imagery have been inserted.
- Western/Southern road termini are still unsurveyed; do not invent continuation. Verify geological tie points and historically supported bank/road destinations before rendering new close-up geographic art. Four V100 LOD tiers and actual physical iPhone visual acceptance are still outstanding.

Flags: gameArtApproved=false; historicRouteVerified=false; bridgeBanksVerified=false; physicalIPhoneApproved=false; productionApproved=false.

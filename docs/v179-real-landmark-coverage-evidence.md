# V179 — real landmark coverage audit (2026-10-25)

**STATUS: geographic references only; THREE GAME OCTAGONS STILL VISUALLY REJECTED.**

Branch `terrain-v179-real-landmark-coverage-20261025` is isolated from main. V94 campaign/saves, V121 painting and V123 road/bridge controls were not edited.

## Evidence inspected first

- Issue #9 through V178; V178 verified coordinate CI [40169070892](https://github.com/wayfinderandco0-cell/century-of-empires/actions/runs/40169070892) and actual source coordinate manifest.
- Original V171 GAME WebKit phone screenshot artifact [12578863866](https://github.com/wayfinderandco0-cell/century-of-empires/actions/runs/40142947845/artifacts/12578863866): west/south still synthetic and comparatively low detail, Matrei is a detailed photo island, and road ends are survey-limited. Original strict game-art gate remains 0/4.
- Matrei modern geographic reference: https://en.wikipedia.org/wiki/Matrei_am_Brenner (approx. 11.45306 E, 47.13083 N).
- Brenner Pass modern geographic saddle reference: https://en.wikipedia.org/wiki/Brenner_Pass (approx. 11.50750 E, 47.00333 N). **This is not evidence of the intended Western Pass or Southern Valley GAME-cell identity.**

## Actual implementation and findings

`terrain-grid/v179-real-landmark-coverage.js` and `scripts/test_v179_real_landmark_coverage.js` check independently sourced modern place coordinates against the *exact* V178 observed V168 SOURCE L footprint, V97 broad relief and V102 narrow Navis relief. Geographic proximity is measured with a haversine distance to the nearest **observed** source sector, not the unacquired southwest quadrant. Every return explicitly forbids painted V121/V123 registration, historical roads, bridge-bank approval, game deep zoom or production approval.

- **Matrei**: V97 and V102 relief cover its modern reference coordinate, but the actual 2023 V168 photo L does **not**. Nearest observed source is **4.170 km** away.
- **Brenner Pass**: V97 relief covers its modern reference coordinate, but V102 and the V168 photo L do **not**. Nearest observed photo source is **13.681 km** away.
- V168 SOURCE center is observed, but this does not certify a historic route or playable game cell. Unacquired southwest stays unknown.
- **No independent geographic anchors yet define Western Pass or Southern Valley as GAME octagons.** These modern places are not V121 painting tie points and do not justify a game-art transform.

## Verification

[GitHub Actions run 40172504160](https://github.com/wayfinderandco0-cell/century-of-empires/actions/runs/40172504160) **SUCCESS**: V172 registration checks, V178 source crosswalk checks, **10 V179 tests** and exported [source-coverage manifest](https://github.com/wayfinderandco0-cell/century-of-empires/actions/runs/40172504160/artifacts/12591300715) passed. The manifest was downloaded and independently inspected, confirming 4.170 / 13.681 km and all false approval flags. CI validates geography/coverage, not visual acceptance.

**Next highest-impact:** Determine evidence-backed boundaries for the three intended GAME octagons in a real geographic coordinate system. The Western Pass and Southern Valley labels are still game design names, not surveyed locations. Only after that should permitted high-resolution imagery be obtained for each real footprint; use V97 relief for broad geography, never stretch the tiny Navis L across valleys. Historical road/bridge-bank controls require separate period evidence. Then author art, run unchanged V140/V171 four-browser game-art gates, and request physical iPhone visual approval. No merge/deploy/costs.

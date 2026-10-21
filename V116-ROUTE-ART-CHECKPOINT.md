# V116 terrain development checkpoint — 2026-10-21

Development branch: `terrain-v116-hour6-route-art-integrity`. Source commit: `5cf2124e14c3651a04c89d70e6e065c1f5332d89`.
10 tested source/test files were recovered from the prior local patch and committed without touching main.

## Local test evidence
- 19 Python corridor/child-tile tests passed.
- 10 Node renderer tests passed.
- Chromium synthetic-art pixel comparison: portrait 390x844 and landscape 844x390, zero differing pixels of 329,160 in each, one draw call, no JS errors.
- The source image was synthetic; this does not certify alignment against the actual V115 painting or historic road geometry.

## Unverified
- The V115 bridge far-bank continuation, rendered road/polygon alignment, playable corridors, and iPhone Safari behavior are NOT verified.
- All 48 child tiles remain non-playable; new close-up artwork count is zero.
- Issue #9 comment/update attempts were rejected by the connector's safety checks. This checkpoint is saved on the isolated branch instead.

## Next action
Build an isolated V116 proof-of-concept loading the actual V115 artwork and this renderer. Overlay the existing candidate route in the shared world/art coordinate system and measure drift across four zoom levels. Never invent a bridge continuation, road or conquest target. Preserve V94 atlas, V97/V102 terrain, main and saves.

## Follow-up: embedded actual-art audit proof — 2026-10-21
- New standalone `v116-actual-art-route-audit.html` committed to this **isolated branch**, source commit `b830686315309baf18c2bdb41cc01ca3a048973b`; no gameplay/main/saves changed.
- Reuses the exact V115 embedded 1100×842 JPEG (source blob SHA `9a8f44120c2f220abf434bed384f230cf6483296`), exact unverified V115 route arrays, V116 indexed 48 child tiles, and the existing seam-safe V116 renderer.
- Four navigation/inspection presets: whole painting, village, fork, bridge. Candidate south/bridge paths and unit demo use the same source-art-to-V94-world transform as the painted image.
- Provides a tap-to-annotate road tool. Each *human-selected actual-road* pixel is measured against the closest candidate route segment and may be exported as JSON. Zero independent annotations have been entered, so **real road deviation remains unmeasured**.
- GitHub read-back and `new Function` syntax compilation of both script blocks passed. Synthetic DOM/canvas smoke test: image loaded, 48 child tiles, one renderer draw per each of five inspected views, world/screen coordinate roundtrip maximum ~1.7e-10 source-art pixels across all four presets. Those are **mathematical alignment checks**, not proof of painted road or iPhone Safari accuracy.
- Unfinished: run in a real browser / iPhone and visually annotate the painted cart road and bridge approaches; replace wrong route data only after independently comparing to artwork; commission/verify separate far-bank road geometry and passable target before marking traversable/conquerable or scaling more octagons.
- **Publishing:** this page lives only on the V116 branch and is not a verified live GitHub Pages build. Do not claim an iPhone preview is available until explicitly published and tested. The route and army preview remain candidate/prototype-only.

## Follow-up: shared road and two branches actually painted — 2026-10-21
- Inspected exact source JPEG decoded into real image pixels with enlarged before/after overlays, not synthetic testing. The initial road data visibly deviated from painted cart roads and routed the bridge army below the bridge.
- Corrected, **provisional** single graph saved as `terrain-grid/v116-painted-road-network-candidate.json`: 40 shared approach points, common fork source-art pixel `[503,760]`, 46-point south road to visible painting edge `[394,842]`, 50-point bridge road to visible far bank `[699,799]`. No invented continuation on either branch.
- Structural regression suite `tests/test_v116_road_network.js` passed **8 checks** in local JS harness: exact shared prefix, correct fork, no backward bridge detour, five-figure to one-figure pixel drift improvements at manually identified painted reference points, art bounds, parent cell `r10-c09`, four zoom levels with both phone orientations and army/world coordinates. Geometric error remains effectively zero.
- Analyst-selected artwork reference points (not independent surveyed cartography) show **south median original ~50px to candidate ~1px**, **bridge mean original ~20.8px to candidate ~1.1px**. These are comparative visual alignment checks; do not represent meter-accurate georegistration.
- Browser-ready proof `v116-bridge-road-centerline-candidate.html` deployed as a **new standalone file** on main, commit `90e5acdf2d298fc2948da951ef96327c5215814b` (main game, V115 and browser saves unchanged). Opens by default on bridge with broken cyan and replacement yellow routes; switch to south shows broken red and replacement green route.
- GitHub Actions browser QA `.github/workflows/qa-v116-road-network.yml` launched on this branch and tests real image in Chromium + WebKit at portrait and landscape iPhone viewports, with screenshots. At time of note **running, not yet declared passed**. Physical iPhone Safari still needs review.
- Proof URL (GitHub Pages propagation and physical iPhone operation still separately unverified): https://wayfinderandco0-cell.github.io/century-of-empires/v116-bridge-road-centerline-candidate.html
- **Next gating tasks**: review browser test result and rendered screenshots; user physical iPhone road/army check; enforce a persisted, versioned road graph and collision tests in the production engine only after geometry is approved; build genuinely geography-grounded continuation/next octagon; connect terrain multipliers/combat traversal without changing existing game campaigns prematurely.
- **Not yet complete**: a fully playable historically accurate octagon; source image is oblique artist rendering georegistered by a single approximate anchor; no historical GIS confirmation, deep zoom playable child tiles, production unit movement, or additional octagon art.

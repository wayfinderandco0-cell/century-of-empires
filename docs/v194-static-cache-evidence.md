# V194 — camera-stable terrain cache for iPhone route movement (2026-10-25)

**Status:** isolated prototype optimization; **not** game-art approval, source-registered terrain, physical iPhone FPS approval, or production readiness.

## Baseline inspected before coding
- Issue #9 through V193 and existing V193 mobile CI run 40220846883 (4/4 pass).
- Downloaded and opened actual V193 WebKit phone-layout screenshots and V192 three-center screenshots. Matrei is a sharply detailed photographic island; Western Pass and Southern Valley remain soft, synthetic conifer/ground art. The straight, regular cartway appearance and unverified outer road termini remain rejected.
- V193 parent commit `6155bb849846c611ee37da9ba2def71e9e591530`. V121 painted-road image and V123 graph are immutable under the inherited V193 SHA checks.

## Actual code change
- `v192-weathered-cartways-graphics-test.html`: cache only the static rendered viewport (terrain, Matrei photograph, paths and source-limit markers) into a viewport-sized canvas. Dynamic army marker and active route remain separate and are repainted over that snapshot.
- The static cache invalidates when the camera pans/zooms, viewport changes, debug overlay changes, or asynchronous landscape boot completes. Route orders and movement do **not** invalidate terrain.
- Read-only `V192.renderStats` exposes static scene rebuilds, cache hits, dynamic frames, estimated snapshot bytes, and browser render p95. The snapshot is at most one additional device-pixel viewport; it does not duplicate the full geographic atlas.
- `scripts/qa_v194_static_cache.py` checks four real headless mobile-layout browser configurations: Chromium/WebKit × 390×844 and 844×390 at DPR2. It captures three centers per configuration, confirms static rebuilds do not occur during four progress updates, checks army positions remain on the original polyline, and checks zoom/debug correctly invalidate the snapshot. Its browser render timing is **not** a physical iPhone FPS measurement.
- The isolated V194 CI workflow runs inherited V193 camera/gesture/source-blob checks **before** V194 cache checks. Strict GAME art gates and the physical iPhone visual rejection are not relaxed or reclassified.

## Evidence and remaining work
- Development branch: `terrain-v194-static-frame-cache-20261025`.
- Workflow: `qa-v194-static-cache.yml`; **PASS** [Actions run 40225890166](https://github.com/wayfinderandco0-cell/century-of-empires/actions/runs/40225890166). Both inherited V193 camera/source checks and V194 cache checks passed in Chromium/WebKit portrait and landscape (4/4). Actual [artifact 12611427034](https://github.com/wayfinderandco0-cell/century-of-empires/actions/runs/40225890166/artifacts/12611427034) downloaded, opened and inspected.
- Each of four configurations kept **static scene builds constant during army progress** (6→6 Chromium portrait/landscape, 7→7 WebKit portrait, 6→6 WebKit landscape), with **10–12 cache hits** and 2 correct rebuilds after zoom/debug changes. Cached framebuffer: **5,266,560 bytes** per DPR2 viewport.
- Headless browser render-p95 sample values: **11.0–17.2 ms** across the four runs. These are render-call measurements from CI, not end-to-end frame times or a physical iPhone benchmark; no iPhone FPS claim.
- Independent inspection compared all **12 V192 vs V194 screenshot pairs** (three centers × portrait/landscape × Chromium/WebKit) pixel-for-pixel. All **12 were exactly identical**. This confirms the optimization has not improved or degraded the still-rejected artwork.
- **Still rejected:** WEST/SOUTH source-registered period-safe artwork, believable period roads, surveyed bridge banks and endpoints, photographic seam, four-level gameplay, and physical iPhone performance/visual approval.
- **No production changes:** `main`, V94 campaign/saves, V121 painted road source, and V123 route graph are untouched. No merge, deployment, or paid services.

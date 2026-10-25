# V196 — combined weathered cartways and static terrain cache (2026-10-25)

**Status: technical integration only; game art, historical route, bridge-bank, physical iPhone and production approvals all remain FALSE.** Three connected Alpine game octagons are not visually complete.

## Baseline inspected BEFORE coding

- Read issue #9 through the V194 cache report and the latest independent V195 Matrei-seam cartway work. Inspected active branches, CI runs [40225890166](https://github.com/wayfinderandco0-cell/century-of-empires/actions/runs/40225890166) and [40227034854](https://github.com/wayfinderandco0-cell/century-of-empires/actions/runs/40227034854), and downloaded and opened actual WebKit portrait/landscape WEST, MATREI and SOUTH screenshots from both artifacts.
- Existing cartway branch `terrain-v194-weathered-cartway-verges-20261025` at `5350204f8ccfbf99a0507a807d1b4636a533dccd` contained narrower, weathered V123-aligned road pigment and harmonized Matrei border-exit colors, but no static terrain cache.
- Independent cache branch `terrain-v194-static-frame-cache-20261025` at `42e3e01b23c5367cd8aceeac44820a780414c242` avoided rebuilding static terrain during army motion, but did not include the later road pigment changes.
- Real screenshots still show Matrei as a sharply detailed photo/painted island while WEST/SOUTH show soft synthetic trees and regular road geometry. No geographic or 1780-era source registration is established for the outer octagons. Numerical image-gradient tests alone do not make the art acceptable.

## Implemented on a NEW isolated branch

Branch: [terrain-v196-cartway-cache-integration-20261025](https://github.com/wayfinderandco0-cell/century-of-empires/tree/terrain-v196-cartway-cache-integration-20261025). Based only on V195's existing isolated cartway head; no main merge/deploy.

- [f1976176](https://github.com/wayfinderandco0-cell/century-of-empires/commit/f1976176929556eb946e82508731b947e2375f26): integrated the tested static-scene cache and read-only performance counters with the **unchanged latest V195** `paintTrack` and `paintNaturalTrailFinish` functions. V123 road nodes and polylines, route orders, bridge graph and V121 photo are untouched.
- [9b147b8e](https://github.com/wayfinderandco0-cell/century-of-empires/commit/9b147b8efc0d1e5a6a27c6683ef24130e2b93a16): ported four-browser cached-frame/army-route/camera-invalidation regression as `scripts/qa_v196_integrated_cache.py`.
- [3b91ff08](https://github.com/wayfinderandco0-cell/century-of-empires/commit/3b91ff088784f202defd51053fc1136a12e5065b): branch-only CI runs V194 independent painted-pixel road test, V192 route/halt test, V192 three-center detail gate, V193 camera/pinch/source-lock test and V196 cache test. All capture screenshot evidence; no thresholds were lowered and no approval flags set.

## Verified results

[Actions run 40230561361](https://github.com/wayfinderandco0-cell/century-of-empires/actions/runs/40230561361) **SUCCESS**. Downloaded and inspected the actual [artifact 12612664822](https://github.com/wayfinderandco0-cell/century-of-empires/actions/runs/40230561361/artifacts/12612664822), including its four browser reports and screenshots.

- Chromium and WebKit × portrait and landscape: **4/4 PASS** in each of the five QA phases. Independent painted road pixels cover **514/514** sampled V123 road positions in the baseline pigment test; both Matrei exit-pigment seams pass.
- During army progress, static terrain rebuilds remained **6→6** in all four configurations, with **10–11 cache hits** and two expected invalidations after zoom/debug; one DPR2 viewport snapshot = **5,266,560 bytes**. Headless browser render-call p95 was **14.0–16.7 ms**, **not** physical iPhone FPS.
- Independently decoded and compared **12 V195 vs V196 three-center screenshot pairs** with Pillow `ImageChops.difference`: **12/12 pixel-identical**. The cache does not change existing road or terrain appearance.
- Verified V121 photo source blob `4c6aa5cda9e7c359b6d2a49d5b5fe8a597346382` and V123 atlas blob `09f04b4062e24fbacbb645307462cdddce2b2aa3` are identical between `main` and V196. Original V137/V140 strict-gate branches and their screenshots remain untouched.

## Hard blockers / next useful work

1. **Visual quality rejected.** Actual V196 WebKit WEST/SOUTH images still show procedurally repeated soft conifers and visibly artificial, nearly uniform cartways. The Matrei source is much sharper. Passing the V192 gradient floor is only a numeric regression check, not authentic imagery or human acceptance.
2. Build distinct **licensed, high-resolution, geographically registered and period-safe** WEST and SOUTH landscape artwork using vetted geographic reference materials; explicitly exclude modern highways, railways and structures. Never reuse the single Matrei photo elsewhere or add false roads to pass metrics.
3. Independently survey V121/V123 road/bridge-bank tie points and meaningful destinations before allowing any new route edges. Both outer endpoints remain **unsurveyed**. Preserve all V100 zoom tiers and compare real phone screenshots at each center and whole crossing.
4. Obtain user visual acceptance and physical iPhone performance evidence before any merge, deployment, Europe-map expansion or claim of three complete octagons.

**Flags:** `gameArtApproved=false`, `historicRoadVerified=false`, `physicalIPhoneApproved=false`, `productionApproved=false`. No paid services, main campaign or saved games changed.

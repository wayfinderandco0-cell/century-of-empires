# V211 — mobile landmark-review initialization race and fail-closed diagnostics

Date: 2026-10-26. Isolated branch based on V210. No merge, deployment, payment, or production change.

## Evidence read before implementation

- GitHub issue #9 through V210; V210 final CI run 40294316306 and job 121476542676. Source/landmark invariants were green; inherited V121/V123 painted-road, bridge, touch and three-center capture tests were green. V210's mobile review step timed out after 150 seconds waiting for `window.V210 && V210.ready`, preventing the later strict V203 gate from executing in that run.
- Inspected the actual V210 WebKit portrait WEST/MATREI/SOUTH rendered screenshot artifact: WEST/SOUTH still show artificial vegetation and simplified roads; Matrei's original central image is visually richer. These are automated phone-layout captures, **not physical iPhone approval**.
- V210's review starts `boot()` only from the iframe `load` listener. The listener is installed after the iframe markup, so an already-loaded frame can miss it. **The initial V211 diagnostic run 40301156199 then established the deeper blocker:** WebKit portrait loaded all four synthetic modern source tiles, but V192 `ready=false` and the iframe was still at `Drawing continuous ridges and forest texture…` after 45 seconds, with no page errors. V192 has six groups of `setTimeout(0)` cooperative yields in its full deterministic terrain builder; an offscreen iframe may clamp each of these timer yields, delaying completion by minutes.

## Isolated changes

1. `v210-landmark-visual-review.html`: start the iframe readiness probe immediately as well as on `load`, with one shared promise to prevent duplicate initialization. Expose read-only status, tile and embedded-frame diagnostics; no coordinate, photo, terrain, army, road, bridge or approval mutation.
2. `v192-weathered-cartways-graphics-test.html`: add a read-only `snapshotForReview()` hook invoking the **existing** V192 renderer synchronously. The iframe is positioned far offscreen; WebKit and Chromium can throttle its `requestAnimationFrame` indefinitely. The new `?reviewCapture=1` mode changes only the six cooperative `setTimeout(0)` yields to microtask yields during the offscreen capture, leaving the exact deterministic pixel math, all 104,000 procedural tree samples and original normal interactive preview unchanged. The V210 review no longer waits for two offscreen animation frames. This is a real game-camera rendering path, not synthetic art or a changed movement graph.
3. `scripts/qa_v210_landmark_review_ui.py`: intercept modern imagery only by exact host, returning explicitly **SYNTHETIC TEST TILES**; on startup failure, write the browser screenshot and diagnostic JSON and fail the run. Preserve all four Chromium/WebKit × portrait/landscape checks and V121/V123 blob SHA pins.
4. `.github/workflows/qa-v211-landmark-review.yml`: preserve V204–V209 source audits, V121/V123 route/bridge and mobile camera checks, three-center real game screenshot QA, and strict V203 photographic-detail gate. The latter **must remain red until actual West/South art improves**.

## Boundaries and outstanding blockers

The modern V205 source is not registered to V123 playable cells. No independently validated natural landmarks, 1780 geography, west/south bridge-bank continuations, historical roads or user visual approval have been established. The V203 real screenshot detail gate previously failed in all four layouts. The V210 review UI uses modern imagery for comparison only; the QA stubs are not real terrain. No art is pasted into the game.

`sourceRegisteredToV123=false; historicalRoadsVerified=false; bridgeBanksVerified=false; gameArtApproved=false; physicalIPhoneApproved=false; productionApproved=false`.

CI: Initial diagnostic run [40301156199](https://github.com/wayfinderandco0-cell/century-of-empires/actions/runs/40301156199) confirmed the blocked V192 terrain build (source integrity GREEN, mobile review RED with captured diagnostics). Later runs include the synchronous snapshot and the offscreen-yield scheduling fix. Do not infer a pass until the final run completes and actual screenshots are inspected.


## Final V211 CI verification and actual image inspection

- **Final full workflow:** [40302601505](https://github.com/wayfinderandco0-cell/century-of-empires/actions/runs/40302601505) on implementation commit `6c5bf66e`. Source/landmark invariant job **SUCCESS**; original V121/V123 road, bridge, camera, and screenshot capture stages **SUCCESS**.
- **V211 mobile review QA: SUCCESS 4/4**: Chromium portrait and landscape, WebKit portrait and landscape; all three real game camera centers, clipped-octagon checks, source coordinate mapping, and no-approval assertions. The WebKit synthetic `MouseEvent` rounds CSS client coordinates to integers; QA now validates the exact actual dispatched event against native XYZ coordinates rather than falsely assuming a fractional ideal center. No geographic threshold or art QA loosened.
- **Strict V203 real artwork QA: FAILED 4/4 as required.** WEST relative fine-luminance 0.533–0.553; SOUTH 0.504–0.528 vs Matrei and 0.70 floor. This is the remaining real visual defect, not a V211 regression.
- Downloaded actual [CI screenshot artifact 12641501516](https://github.com/wayfinderandco0-cell/century-of-empires/actions/runs/40302601505/artifacts/12641501516) and opened all three **WebKit portrait** review captures. The game panel shows actual WEST/MATREI/SOUTH V192 rendering; the source panel visibly says **SYNTHETIC TEST TILE / NOT REAL ALPINE SOURCE** and is never presented as real aerial imagery. WEST/SOUTH still look visibly simplified compared with original Matrei.
- The overall workflow status is **RED intentionally**, because the unchanged strict art-quality gate fails after all functional QA succeeds. The review tool is functional, not a completed geographic registration or artwork approval.

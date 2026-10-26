# V211 — mobile landmark-review initialization race and fail-closed diagnostics

Date: 2026-10-26. Isolated branch based on V210. No merge, deployment, payment, or production change.

## Evidence read before implementation

- GitHub issue #9 through V210; V210 final CI run 40294316306 and job 121476542676. Source/landmark invariants were green; inherited V121/V123 painted-road, bridge, touch and three-center capture tests were green. V210's mobile review step timed out after 150 seconds waiting for `window.V210 && V210.ready`, preventing the later strict V203 gate from executing in that run.
- Inspected the actual V210 WebKit portrait WEST/MATREI/SOUTH rendered screenshot artifact: WEST/SOUTH still show artificial vegetation and simplified roads; Matrei's original central image is visually richer. These are automated phone-layout captures, **not physical iPhone approval**.
- V210's review starts `boot()` only from the iframe `load` listener. The listener is installed after the iframe markup, so an already-loaded frame can miss it. That is a credible race, not yet established as the sole CI failure.

## Isolated changes

1. `v210-landmark-visual-review.html`: start the iframe readiness probe immediately as well as on `load`, with one shared promise to prevent duplicate initialization. Expose read-only status, tile and embedded-frame diagnostics; no coordinate, photo, terrain, army, road, bridge or approval mutation.
2. `scripts/qa_v210_landmark_review_ui.py`: intercept modern imagery only by exact host, returning explicitly **SYNTHETIC TEST TILES**; on startup failure, write the browser screenshot and diagnostic JSON and fail the run. Preserve all four Chromium/WebKit × portrait/landscape checks and V121/V123 blob SHA pins.
3. `.github/workflows/qa-v211-landmark-review.yml`: preserve V204–V209 source audits, V121/V123 route/bridge and mobile camera checks, three-center real game screenshot QA, and strict V203 photographic-detail gate. The latter **must remain red until actual West/South art improves**.

## Boundaries and outstanding blockers

The modern V205 source is not registered to V123 playable cells. No independently validated natural landmarks, 1780 geography, west/south bridge-bank continuations, historical roads or user visual approval have been established. The V203 real screenshot detail gate previously failed in all four layouts. The V210 review UI uses modern imagery for comparison only; the QA stubs are not real terrain. No art is pasted into the game.

`sourceRegisteredToV123=false; historicalRoadsVerified=false; bridgeBanksVerified=false; gameArtApproved=false; physicalIPhoneApproved=false; productionApproved=false`.

CI: V211 run 40301156199 triggered; results pending when this document was authored.

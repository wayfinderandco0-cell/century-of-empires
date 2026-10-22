# V116 hour 24 — half-open candidate route coverage

Date: 2026-10-22 (America/Chicago)
Branch: `terrain-v116-hour24-halfopen-route-coverage`

## Completed
- Candidate corridor tile coverage now uses the existing V116 route-to-tile seam tracer, not inclusive segment/rectangle contact. This prevents phantom candidate cells at corner-only touches and makes exact-border ownership match army positions.
- Added `tests/test_v116_halfopen_coverage.js` with four cases: corner, exact vertical border, reverse travel, and mismatched tile index.
- Extended `.github/workflows/qa-v116-geometry-integrity.yml` to test the new branch and include route-tracing regressions.

## Verified
- Code commit: `c095b0534a85a57ca3a9e94d3087f60612a0fd3a`.
- Test/workflow commit: `8eeb4fcd2f63f68dfe8894693e5c0a35a05d36d4`.
- Hosted CI: https://github.com/wayfinderandco0-cell/century-of-empires/actions/runs/39740465449 — **42 Node tests passed, zero failures**.
- The index regenerated with **zero git diff**. Existing 48 child-tile candidates unchanged. All remain non-playable and non-conquerable.
- Source artwork, V94 geography, candidate bridge terminal, main, deployed game and saves unchanged.

## Outstanding
- The painted south route is not independently measured. The candidate bridge ends at the visible far bank, with no verified historical or painted onward road.
- Neither a 432-cell index nor 48 subdivisions of one illustration is finished terrain artwork.
- GitHub issue #9 comment write was rejected by connector safety checks; this branch checkpoint preserves evidence.

## Next
Compare independently traced painted-road points against the existing source-pixel graph, then establish sourced far-bank terrain and crossing continuity. Do not grant traversal, deep zoom or conquest until proven.

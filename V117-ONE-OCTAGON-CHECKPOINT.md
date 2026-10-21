# Century of Empires — V117 road/art contract checkpoint
Date: 2026-10-21. Branch: `terrain-v117-road-art-contract`.
**Main, published game, existing saves and historical gameplay are untouched.**

## User-defined milestone
Complete ONE convincing, reusable Brenner-region terrain/octagon with an actual passable road, village, bridge, and road continuing to a neighboring section. An infantry formation must visually remain on the painted road at all four game zoom levels on iPhone. Do not begin scaling to 432 Europe cells until one section is truly finished.

## V117 implemented
- `scripts/v117_road_art_contract.js`: a cart-track paint layer whose centerline is **read directly from the V116 army road graph**. The approach, south branch, and bridge branch share a fork. Width, shoulders and paired wagon-wheel ruts are drawn procedurally from the same source-pixel geometry. There is no separately guessed "visible centerline".
- `v117-coupled-cart-road-proof.html`: standalone self-contained original 1100x842 Alpine painting with a candidate cart-track overlay enabled and movement on the corresponding route; compact controls, optional debug guides, branch choice, march/halt, reset, and a cart-track ON/OFF switch inside Options. Uses the exact V115 JPEG and V116 tested camera/road graph.
- `tests/test_v117_road_art_contract.js`: 7 Node tests to protect centerline correspondence, shared fork, termination, projection/zoom, mutation fail-closed behavior, and refusal of production/historical claims.
- `scripts/qa_v117_road_art_browser.py` and `.github/workflows/qa-v117-coupled-road.yml`: Chromium and WebKit iPhone-sized mobile browser checks and screenshot workflow.
- Manual in-process JavaScript check: sample-to-painted-centerline maximum ~1.2e-13 source pixels across 300 sampled unit positions, 10 canvas track strokes, mutation guard rejects independent geometry edits.

## This DOES NOT mean the first octagon works
The cart track is a *new candidate visual overlay* laid on the original painting. The underlying pre-existing painted route is not independently confirmed to coincide with it; in places it may still disagree. The road is not survey-grade historical geography. No approved far-bank route extends past the bridge point [699,799]. The south branch remains independent-art unverified. There is no connected next artwork/strategic cell yet. 48 crop tiles remain non-playable, and 432 parent Europe cells are not complete. No actual physical iPhone Safari approval. This is **not production-ready** and must not be merged into main merely because the code tests pass.

## Next acceptance gate
1. Inspect automated Chromium/WebKit screenshots of the actual V117 image and compare original painting against cart track and moving formation. Reject visibly doubled, muddy or disconnected tracks.
2. Reauthor the terrain/road scene and route **together** where necessary; do not layer cosmetic fixes indefinitely. A coherent exit across the far bank must be painted and modeled with a true next-section connection, not assumed from the candidate endpoint.
3. Integrate with all four *real* geographical game zoom levels (not four inspector presets) and verify playable marching/stop/turn, terrain effects, and camera on a physical iPhone before calling ONE octagon completed.
4. Only after one full passage is approved, formalize reuse across neighboring legitimate cells.

**Honest status:** V117 is a structural synchronization proof and visual diagnostic, not an integrated finished game terrain cell.

# V116 Hour 10 — candidate route seam regression checkpoint

Date: 2026-10-21. Branch: `terrain-v116-hour10-trace-ci`, forked from Hour 9 commit `92f02abfa954bddc569281bbcbc7556965f3384c`.

## Verified change
- New regression suite `tests/test_v116_trace_backtracking.js`, commit `1852544cfbc264066c0bb851335993c467141856`.
- GitHub file and branch-head readback verified. Tests cover: (1) ordered reverse seam traversal and cumulative arclength, (2) deterministic ownership along an exact vertical tile edge, (3) full-width crossing of multiple child-tile seams, (4) no phantom tiles at right/bottom artwork boundaries, and (5) rejection of prematurely traversable candidate tiles.
- Five Node 22 tests passed locally using offline copies of the checked-in `v116_route_tile_trace.js` and its actual renderer `validate()` logic. Hosted GitHub CI has **not** run these new tests.
- Attempt to create `.github/workflows/qa-v116-seam-trace.yml` was blocked by connector safety checks. Issue #9 comment also blocked. This checkpoint records the verified change instead.

## Unchanged constraints
- These tests are candidate-only geometry checks, not certification of painted roads or historical geography.
- Bridge stops at painted far-bank candidate `[699,799]`. No proven road beyond it, and south-road art alignment remains unverified.
- All 48 local child tiles remain non-traversable, non-conquerable, not deep-zoom eligible. The 432 Europe octagons are an index, not completed close-up terrain.
- No modifications to main, production, saves, fog-of-war or combat systems.

## Next highest-impact action
1. Run the new suite and existing V116 seam/road tests in hosted CI on this isolated branch if workflow permissions allow.
2. Obtain independent source-art and historical road evidence for a real far-bank continuation. Do not invent a route to satisfy the graph.
3. Integrate validated corridor geometry into the actual four-level game only after the source-art continuity is established.

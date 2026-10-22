# V116 Hour 20 — Candidate index provenance enforced

Date: 2026-10-21 (America/Chicago). Isolated branch: `terrain-v116-hour20-index-builder-guard`.
Code/test commit: `c6c0d4b61f7c4f362a620d2e6572d084de657c94`.

## Actual change
- `scripts/build_v116_candidate_tile_index.js` now invokes `buildSafe` from the pinned candidate graph guard before computing tile coverage, instead of directly accepting the mutable candidate centerline. Optional source/candidate arguments permit negative-case testing without changing production data.
- `tests/test_v116_index_provenance_gate.js` checks byte-equivalent baseline JSON, 48 candidate-only tiles, eight deliberate provenance/authorization tamper cases, and no input mutation.
- The original 432 Europe logical cells and 48 local image subdivisions remain indexes only; no historical roads or bridge extensions were added.

## Validation evidence and limits
- A 9-check V8 integration harness evaluated the actual GitHub-fetched builder, guard, road graph, and JSON fixtures. All checks passed, including exact JSON equality with `terrain-grid/v116-candidate-route-tiles.json`.
- `node --check` passed for the new Node test file. **Full Node test execution and hosted CI are not yet verified.**
- GitHub branch head and both committed blobs were read back and matched the expected SHAs.
- No cell was granted traversal, deep zoom or conquest; the far-bank road continuation remains **unverified**.
- GitHub issue #9 comment attempt was blocked by connector safety checks; this checkpoint records the evidence until issue updates work.

## Next single task
Run `node --test tests/test_v116_index_provenance_gate.js tests/test_v116_route_tile_coverage.js tests/test_v116_candidate_graph_guard.js` in an actual checkout/CI. Then collect independent painted-road and historically supportable bridge-continuation evidence before enabling route movement. Do not invent far-bank geometry or claim the first octagon is finished.

Main branch, live game, saves, and deployment were untouched.

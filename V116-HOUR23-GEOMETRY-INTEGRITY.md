# V116 geometry integrity checkpoint — 2026-10-22

Branch: `terrain-v116-hour23-geometry-integrity` (from `terrain-v116-hour22-full-path-pin`, `ac97f74517aed6e69ed886468fa3782513b11aed`).

## Change
- The candidate graph guard now pins the **entire** existing south and provisional painted-bridge centerlines plus fork index 36, not only the source blob and terminal [699,799]. Unreviewed edits to interior points must fail closed.
- Existing guard tests now use the actual checked-in V115 source/candidate fixtures and road graph, rather than a synthetic three-point geometry that could not satisfy full-route integrity checks.
- Added regressions for altered bridge interior points, altered source approach points, coordinated approach edits and coordinated fork-index changes, plus input immutability.
- Added a branch-scoped Node 22 CI workflow for guard/index/coverage/road-graph tests and deterministic index regeneration.

## Evidence and limits
- A V8 execution harness loaded the actual GitHub-fetched road graph, new guard, source/candidate fixtures and rewritten tests; **9 tests passed**. This is not a substitute for Node or hosted CI. Verify GitHub Actions result separately.
- Route index, geometry, artwork, and production permissions remain unchanged. The candidate bridge stops at the visible far bank; its historic accuracy and continuation are **not verified**. All 48 local tiles remain non-playable, and none is a conquest objective.
- No production/main/live/save changes.

## Next
Collect hosted Node test result, then compare painted-road landmarks against actual art; only independently verified road/bridge approaches can authorize any movement. Do not infer far-bank continuation from the candidate route.

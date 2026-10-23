# V123 experimental octagon-overlap seam guard — October 22, 2026

Development branch: `terrain-v123-hour9-overlap-seam-guard-20261022`. This is a source-only safety checkpoint, not a gameplay integration.

## Defect confirmed
The V122 seam validator checks matching road endpoints and collinear shared boundaries. When two octagon tiles occupy the same geographic footprint, those checks can succeed even though the tiles are stacked rather than neighboring. The original validator passes the synthetic stacked-tile regression fixture.

## Committed work
- `terrain-grid/v123-safe-seam-engine.js` is an experimental adapter around V122. A separating-axis test checks convex octagon interiors. It disables a seam before graph construction if tile interiors overlap; the resulting seam is marked `tile_interiors_overlap`.
- `scripts/test_v123_safe_seams.js` verifies a stacked-tile crossing is blocked, its route is unavailable, and ordinary horizontal and angled shared-edge neighbors remain connected.

## Validation
Local Node test: PASS (four checks: original false positive reproduced, stacked route blocked, side adjacency accepted, diagonal adjacency accepted). Local test used a source-equivalent copy of V122 fetched from GitHub. No GitHub Actions execution has been recorded for these new files.

## Blockers
Existing-file updates through GitHub were denied, as were creation of a new GitHub Actions workflow and posting an issue #9 comment. Therefore the adapter is not yet wired into V123 and its test is not yet in CI. Do not represent this as a fixed V123 gameplay seam.

## Next action
Integrate the adapter in the isolated V123 preview, run original V123 browser tests and the overlap regression in GitHub Actions, then resume evidence-based road/art review. No historical road placement, neighbor art or physical iPhone validation was completed here. Main, live game and saves remain untouched.

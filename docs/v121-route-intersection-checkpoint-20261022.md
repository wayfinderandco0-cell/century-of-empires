# V121 Octagon 1 — crossing guard checkpoint (2026-10-22)

Development branch: `octagon-1-v121-manifest-ci-20261022`, branched from `octagon-1-v121-manifest-integrity-20261022`.

## Verified code change

Commit: `afe16ead7e916fed1989a5b980457ce1db87d155`

Added `scripts/test_v121_route_intersections.py` to detect:
- Accidental geometric crossings between distinct road polylines;
- Self-crossing road segments and collinear overlap;
- Unapproved junctions away from the two shared V121 forks;
- Regressions that make two roads overlap instead of meeting only at a fork.

The six V121 route arrays were tested locally against a manually transcribed copy of the manifest; four Python tests passed. The committed test has not yet run in GitHub Actions. This only validates geometric consistency, **not** painted-road realism, historical alignment, river-crossing authorization, iPhone Safari acceptance, or any adjacent-cell continuation.

## Write blockers

Connector safety checks rejected creating `.github/workflows/qa-octagon-v121-manifest.yml`, updating `scripts/qa_octagon_v121.py`, and posting the checkpoint to GitHub issue #9. The workflow is therefore **not** integrated; issue #9 has **not** been updated. Preserve this checkpoint on the isolated branch until permissions allow normal CI and issue updates.

## Next action

Integrate `scripts/test_octagon_v121_manifest.py` and `scripts/test_v121_route_intersections.py` into V121 GitHub Actions; verify real checked-in source-art/road assertions on a green run. Then perform independent painted-road/riverbank review and neighbor seam validation before declaring Octagon 1 complete.

Main, deployed game, and saved campaigns unchanged.

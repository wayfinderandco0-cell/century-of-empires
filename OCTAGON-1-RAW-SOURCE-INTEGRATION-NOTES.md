# Octagon 1 raw-source audit integration — 2026-10-22

Branch: `octagon-1-raw-source-integration-20261022`.
Base: `octagon-1-source-identity-guard-20261022`.
Do not merge/deploy until artwork and physical iPhone review are approved.

## Changed
- `tests/test_octagon_1_audit_integration.py` exercises real embedded JPEG across V115/V119/editor, both audit scripts, source-only crop pixel identity, output JSON and fail-closed readiness.
- `.github/workflows/qa-octagon-1-raw-art.yml` now runs those tests and both raw-JPEG/edge extraction scripts when relevant files change on the isolated raw-source branch.

## Validation
GitHub Actions run: https://github.com/wayfinderandco0-cell/century-of-empires/actions/runs/39794744845
At authoring time, the run was queued. Verify final conclusion before marking tests passed.
This is source-integrity validation, not an approval of a painted road or a verified historical crossing.

## Outstanding
- Source JPEG does not establish a continuous visible cartway over the candidate east-bank route.
- East boundary [1100,704] is not an image pixel and neighboring terrain remains missing.
- No historical road or valid crossing is certified; productionReady must remain false.
- GitHub issue #9 comment attempt was blocked; keep this branch note as the checkpoint.

## Next action
Inspect generated unpainted source crops, locate actual road surfaces in the artwork, and revise terrain/art together with route control points. Merge only the reviewed evidence-gate work from the parallel `octagon-1-fail-closed-gate-20261022` branch into a future isolated integration branch, never main.

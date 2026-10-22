# Octagon 1 low-contrast source-art diagnostics — 2026-10-22

Development branch: `octagon-1-hour12-low-contrast-spans-20261022`
Code commit: `f2bfa76512513c1458b1646a1f7dff9538ce7f17`

## Verified changes
- Added `scripts/qa_octagon_1_diagnostic_spans.py` to report contiguous original-JPEG low-contrast sample ranges with exact source-image start/end coordinates and sample indexes.
- Integrated diagnostic ranges into the existing four-section report in `scripts/qa_octagon_1_full_corridor.py`.
- Added five synthetic tests (5/5 passed locally) and new integration assertions in `scripts/test_qa_octagon_1_full_corridor.py`.
- Verified the GitHub branch head and readback of all four changed files after committing.
- A missing/out-of-bounds contrast breaks a run. Low contrast does **not** prove absence of a road; no result grants playable access, road approval, or historical verification.

## Limitations
- Full-corridor integration tests and original pinned JPEG sampling have **not** been run on the committed branch in CI; no CI status exists for this commit.
- The bridge approaches, painted road surfaces, neighbor seam, historical road evidence, and far-bank continuation remain unverified.
- Issue #9 comment attempt was blocked by GitHub connector safety checks. This file is the durable fallback record.
- Main, live game, V94/V97/V102 atlas, and campaign saves were not changed.

## Next action
Run `python scripts/test_qa_octagon_1_diagnostic_spans.py`, `python scripts/test_qa_octagon_1_full_corridor.py`, and `python scripts/qa_octagon_1_full_corridor.py` against the pinned source JPEG in a checked-out repo or CI. Review the four corridor sections' exact low-contrast spans against unaltered source artwork, then repair and independently verify a visibly connected bridge road without guessing historical continuity.

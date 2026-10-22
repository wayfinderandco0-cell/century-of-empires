# Octagon 1 source-image sampling gaps — October 22, 2026

Development branch: `octagon-1-hour13-full-corridor-ci-20261022`
Code commit: `5e8137ad6bc3eebd47c2ba3864d06ef0e8513194`

## Verified
- Added `scripts/qa_octagon_1_unobservable_spans.py` to report exact index and source XY spans where center/perpendicular pixel probes cannot be read from the original image (often at image boundaries).
- Integrated gap counts and per-section gap spans into the four-section raw-art report, without granting any playable-road or crossing approval.
- Added five synthetic regression tests; **5/5 passed locally** using Python's unittest.
- GitHub readback confirmed all four changed source/test files and the isolated branch head.

## Limitations
- Existing full-corridor integration tests and the pinned original 1100x842 JPEG were **not executed** on this branch; no GitHub Actions run was observed. Creating a dedicated workflow was blocked by connector safety checks.
- The original JPEG was visually inspected: it contains baked-in location banners, and the proposed eastern continuation is not established as a painted continuous road. This is a visual observation, not historical-route verification.
- A GitHub issue #9 comment attempt was blocked; this file is the durable branch record.
- The far-bank bridge exit, historical road evidence, next-cell art, and terrain continuity remain unverified.
- Main, live game, V94/V97/V102 terrain, and campaign saves were not modified.

## Next action
Execute `python scripts/test_qa_octagon_1_unobservable_spans.py`,
`python scripts/test_qa_octagon_1_full_corridor.py` and
`python scripts/qa_octagon_1_full_corridor.py` against the pinned source JPEG
in a checked-out repository or approved CI. Inspect the reported missing-sample
ranges and actual source artwork. Then author and independently verify a
physically continuous bridge approach and far-bank cartway; do not assume the
east-edge candidate connects to a playable neighbor.

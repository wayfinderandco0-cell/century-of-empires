# Octagon 1 candidate-army frame coverage — October 22, 2026

Development branch: `octagon-1-hour16-frame-source-coverage-20261022`.

## Change
- Source-only army-position contact sheets now measure the fraction of each crop that contains actual pinned JPEG pixels. Out-of-image padding is flagged with a red border and a PARTIAL label.
- The JSON report records per-frame `source_pixel_coverage_fraction`, `source_padding_present`, and `candidate_center_in_source`, plus counts of partial frames and unobservable candidate centers.
- Candidate endpoints at x=1100 and y=842 lie on the exclusive right/bottom source boundary; they cannot be treated as observed terrain pixels.
- Existing original JPEG, candidate route arrays, source SHA pin, game mechanics, main branch, and saves are unchanged.

## Validation
- `python -m unittest -v test_qa_octagon_1_raw_unit_frames.py`: **6/6 passed locally** with Pillow 12.3.0 on synthetic 1100x842 imagery.
- Coverage checks include complete/partial/empty crops, invalid inputs, and visible warning borders.
- The pinned original JPEG was not executed in this local test environment; no CI run is claimed for this branch.

## Remaining
- This prevents cropped-out padding from masquerading as terrain, **not** a painted-road repair.
- Road surface, bridge approach/exit, historical corridor, adjacent-cell seam, and four-zoom movement remain unverified.
- Next: run the source-pinned full-corridor and contact-sheet diagnostics in CI or a checked-out repository, then independently author/verify a visually continuous road surface and valid bridge crossing.

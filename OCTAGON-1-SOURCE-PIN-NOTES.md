# Octagon 1 original-JPEG integrity checkpoint — 2026-10-22

Development branch: `octagon-1-hour9-raw-source-pin-20261022` (forked from `octagon-1-hour8-raw-road-evidence-20261022`).

## Implemented

- `scripts/qa_octagon_1_raw_road.py`: before inspecting any route pixels, calculate the actual Git blob SHA-1 from the original JPEG bytes and reject source drift. The approved baseline for **identity only** is `96c5eeee5afafa20c5442da42c9a1caedd4b00ad`, which matches the repository's GitHub contents metadata and the editor's `sourceBlobSha`.
- Diagnostic JSON now records `source_git_blob_sha` and `source_identity_verified: true` **only after** the byte identity check. These fields do not certify any road, terrain access, river crossing, or neighbor.
- `scripts/test_octagon_1_source_pin.py`: checks the checked-in JPEG against the pin, editor pin consistency, rejection of another valid 1100×842 JPEG, and rejection of non-byte inputs.
- No source image, movement engine, art, main branch, live game, or saves changed.

## Validation and limitations

- A local isolated reproduction of the new SHA-1 helper and mutation cases passed 3/3 Python tests.
- The new GitHub test file and modified script were read back successfully.
- **No CI run on this branch has been verified.** Updating the existing GitHub Actions workflow and creating a new workflow were both rejected by connector safety checks. The existing workflow only runs automatically on the previous branch, so its earlier success does not validate these changes.
- An attempted issue #9 comment was rejected by connector safety checks. This branch note is the fallback durable checkpoint.
- This is a provenance guard, not a visual road fix. Candidate road paint, baked-in labels, south branch, bridge continuation, and neighboring artwork remain unresolved.

## Next action

Run `python scripts/test_octagon_1_source_pin.py`, `python scripts/test_qa_octagon_1_raw_road.py`, and `python scripts/qa_octagon_1_raw_road.py` in CI when workflow modification is allowed. Then use the pinned original-art crops to author one credible, historically plausible cartway in the terrain itself and independently verify both bridge approaches. Do not authorize cross-cell marching until reviewed neighbor/river evidence exists.

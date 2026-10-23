# V121 Octagon 1 — manifest integrity checkpoint (2026-10-22)

**Isolated branch:** `octagon-1-v121-manifest-integrity-20261022`
**Code commit:** `985e779aaae9adbce50232df9ddd221ce9c80a93`
**Main/live/saves:** untouched.

Added `scripts/test_octagon_v121_manifest.py`, a six-test fail-closed Python regression suite checking the six road polylines and two bridge endpoints against the prototype, connectivity and declared 73 graph nodes, image bounds, identical embedded and reusable WebP art, pinned Git blob SHA, non-authorized adjacent-cell exits, and the unapproved historical/mobile/production gates. Negative tests reject modified art, forged neighbor connectivity, premature approval, road-coordinate drift, and bridge-coordinate drift.

**Executed evidence:** all 6 Python tests passed on a generated synthetic fixture; syntax compilation passed. Separately, connector-side assertions against the **actual** V121 GitHub HTML, manifest and WebP passed: 6 roads, 73 connected nodes, exact road and bridge coordinate equality, identical embedded/external WebP after removing GitHub's base64 line breaks, SHA `c4b81d2a168700bed66c05f8cfe3dc3d39ac3c3e`, all three neighbors unbuilt and approval gates false. The new Python suite has **not** been run against the actual repository in CI yet.

**Blocker:** GitHub `update_file` for the existing V121 QA script and workflow and `add_comment_to_issue` for issue #9 were rejected by tool safety checks. Do not claim the new suite is wired into CI or that issue #9 was updated. This branch note preserves the evidence until writes can be completed.

**Next safe task:** integrate the new suite into `scripts/qa_octagon_v121.py` or `.github/workflows/qa-octagon-v121.yml`, then verify a green GitHub Actions run on the real art. Do not mistake this static contract for independent proof that all road pixels follow historically plausible terrain, for neighboring seams, or for physical iPhone acceptance. PR #14 remains a standalone proof, not production.

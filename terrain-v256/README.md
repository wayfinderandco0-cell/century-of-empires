# V256 — Correct the source-road evidence before accepting artwork

**WEST REJECTED (necessary geometry fails); SOUTH STILL UNAPPROVED; production RED.**
This branch adds isolated code, seven tests, CI and documentation. No changes to Matrei, V94, saves, army sprites, core mechanics, or immutable V121/V123 road/bridge graph.

## Evidence examined first

Read issue #9 through V255 and the V255 branch/Actions run 40632912707 (functional success, deliberate production failure). Downloaded **actual** V253 WebKit gameplay artifact 12787641727 (run 40621246002) and opened its real WebKit portrait screenshot: the old WEST/SOUTH licensed fixture photos have dashed V123 roads crossing trees. This is a genuine browser screenshot, not an AI-generated QA dashboard. Inspected actual V255 source-pixel overlays and the original 1536x1024 WEST and SOUTH fictional images. Some V255 hand-selected road anchors were in grass **below** the physical dirt road, so subpixel mathematical anchor errors were misleading.

## Actual isolated source-image correction

scripts/v256_real_cartway.py traces **18 WEST / 20 SOUTH** original-image cartway landmarks, matches them to unchanged V123 by normalized arc distance, and moves **existing image pixels and ground** together. Source PNG SHA256 pins and the V123 Git blob hash are checked. Only review JPEGs show red V123 and green manually traced guides. Original image sources are distinct OpenAI-generated **fictional** 1536x1024 project studies, not historical 1780 Austrian routes, independently georegistered orthophotos, or verified natural V209 tiepoints. Their use rights/provenance must be recorded before public distribution.

**Local actual-PNG processing, not four-browser gameplay:**

- WEST SHA256 7326e88c778ed4a0018c241156e701690e95deb1feeb8fa13a298c0f0c74505e: corrected physically observed road trace requires **160.15px** maximum displacement, exceeding the existing **155px** limit; min sampled Jacobian **0.3626**, source coverage **99.8345%**, no sampled folds. **Necessary geometry FAIL.** The previous V255 ~149px PASS relied on misplaced source anchors. Do not relax the threshold or claim WEST repaired.
- SOUTH SHA256 034246c5d9471cd6d87673daa48fb1a014dab38d414626677f6148ce8c7d08f3: maximum displacement **66.42px**, min sampled Jacobian **0.6999**, source coverage **99.8427%**, no sampled folds. Necessary transform geometry PASS, but the physical road still drifts from V123 at part of the middle bend. **Not approved.**
- DirtLikeFraction is an explicitly nonauthoritative color proxy. It is not a measure of physical road-centerline accuracy, geodesy, V203 quality, or visual approval.
- Seven local tests passed, including **explicit rejection of WEST** under unchanged 155px, source SHA mismatch rejection, V123 Git blob hash, and synthetic source-pixel transport. CI has only synthetic pixels, not original images.

Reproduce with the original pinned PNGs (not committed):
python scripts/v256_real_cartway.py --west ORIGINAL_WEST.png --south ORIGINAL_SOUTH.png --atlas terrain-grid/v123-atlas.js --out v256-unapproved

## Critical blockers and next action

1. **Replace WEST** with a better physically roaded landscape instead of distorting this source beyond the existing gate or mis-sighting anchors.
2. Improve SOUTH physical mid-bend contact and independently confirm endpoint termination. Its hut is scenic, never conquerable.
3. Independently establish geographic source/game tiepoints (V209 remains unverified), or retain explicit fictional geography. Verify Matrei border seams and both physical bridge banks.
4. Make the exact original pair available to four iPhone Chromium/WebKit configurations and run unchanged strict V203 plus human screenshot review. Neither new original image is currently GitHub-hosted, so no four-browser new-art pass is claimed.
5. Obtain **user visual approval** before any production promotion. productionApproved=false; three octagons unfinished.

# V260 — SOUTH single-pass original-pixel reconstruction (2026-10-28)

**Status: UNAPPROVED; production gate deliberately RED.** No source-proven 1780 geography, independent V209 natural tiepoints, WEST bridge-bank evidence, strict V203 pass, exact V260 WebKit run, or user visual acceptance.

## Actual change

V259 SOUTH was built by first warping the original fictional 1536×1024 image into V258, then interpolating the V258 pixels again for the V259 cartway correction. That double interpolation discards source detail along the physically embedded dirt road. V260 composes the two existing, manually observed source-to-game coordinate maps **before** sampling the original lossless PNG once. This is an image-quality change to the existing physical road and adjacent landscape, not added noise, painted cartway, modified army route or altered historical map.

Original SOUTH source SHA256: `034246c5d9471cd6d87673daa48fb1a014dab38d414626677f6148ce8c7d08f3`. Local V260 output SHA256: `d63f5f056a682f976bafff95f04b2b71e0bb4077f34f18e9a95b32cd72fb5ccb`. WEST unchanged from V259. These are **OpenAI-generated fictional studies**, not georeferenced orthophotos or verified historical roads; original PNG is not checked into GitHub.

## Real local image results, not browser acceptance

Ran the actual original PNG through the committed single-pass algorithm, inspected full-resolution output and an actual-pixel 2× road-bend comparison against V259. Recreated the exact V259 reference PNG from the original and verified its SHA256 `bf672a417f763cd38355396e5e9b2c83083dae2dcdcf164e7de6a8663c475ed4` before comparison.

* On the same road-bend crop (x460–1100, y280–600), mean absolute grayscale Laplacian increases **33.235 → 35.731 (+7.51%)**. Forest crop +1.18%; river crop +2.92%; entire image +3.41%. This is a local high-frequency preservation diagnostic, **NOT** a V203 score, human realism judgment or proof of route contact.
* Mean absolute grayscale pixel difference between V259 and V260 on road bend is 2.10; full image 1.02, showing the scene is preserved rather than replaced with synthetic texture.
* Native-source composed mapping min sampled Jacobian **0.5861**, zero sampled folds, source coverage **99.973%**. All are necessary diagnostics only.
* Local tests **6/6 passed with exact original PNG and V259 reference**. CI runs synthetic tests, with the original-only test explicitly skipped if original assets are absent.

## Integrity and blockers

No existing game files, V94 campaign, user saves, sprites, Matrei, core mechanics, V121/V123 road/bridge graph or V259 artwork were changed. New files are additive on an isolated branch. V259 already proved actual original-art Chromium portrait/landscape rendering; **V260 has not been tested in a real browser** and no exact-art WebKit test is claimed. V259 SOUTH landscape V203 fine-luma/area **0.638/0.637**, below 0.70, remains the last measured strict result. Re-run unchanged strict V203 on exact V260 gameplay screenshots before claiming any progress on that threshold.

**Next:** provide the exact original-art pair to an authorized four-browser environment, inspect real Chromium/WebKit portrait/landscape screenshots and V203; independently reconcile Matrei seams and WEST bridge approaches. If historic tiepoints cannot be verified, keep the fictional alternative explicitly isolated. Do not promote until user visual approval.

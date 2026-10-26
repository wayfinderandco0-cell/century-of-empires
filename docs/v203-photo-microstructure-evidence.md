# V203 — photograph-vs-neighbor fine-structure audit (fail-closed; art NOT approved)

Date: 2026-10-25 America/Chicago (CI 2026-10-26 UTC).

## Starting evidence inspected
- Read issue #9 through V202; inspected V202 source, V121/V123 immutable road controls, V152 unsurveyed termini, and inherited V192/V201 camera/road/visual QA.
- Confirmed the final V202 bridge-regression run [40258788180](https://github.com/wayfinderandco0-cell/century-of-empires/actions/runs/40258788180) **SUCCESS** (all inherited checks and both explicit bridge regressions).
- Downloaded actual V202 final screenshot artifact **12623469383** and opened real Chromium/WebKit portrait/landscape West, Matrei and South close-up images. These are headless phone-layout screenshots, NOT a physical iPhone test.
- Human visual inspection: WEST/SOUTH have large soft conifer blobs and flat regular cartways; original MATREI photo has substantially richer individual foliage/rock/water/bridge microstructure. The existing V192 one-pixel gradient gate passes but does not adequately capture this mismatch.

## Code
- New isolated branch terrain-v203-photo-microstructure-gate-20261025, based on V202. No game HTML, original V121 Matrei painting, V123 crossing/road/army geometry, main, live game, or saved campaign files changed.
- New scripts/qa_v203_canopy_structure.py measures **native screenshot luminance microstructure** in the same 22–80% × 22–78% central region of all 12 existing V192 three-center close-up frames. It subtracts a Gaussian-blurred (radius 3 native pixels) grayscale image from the original, measuring both mean high-frequency luminance and the fraction of pixels with residual >12. West and South must each reach **at least 0.70 of Matrei** on both metrics in **all four Chromium/WebKit × portrait/landscape configurations**.
- The new gate is **stricter**, not a lowered or tuned-to-pass V140/V171/V192 threshold. It is a necessary image diagnostic only. Noise could still fool a metric; it never confers geographic registration, historic authenticity, natural canopy form, bridge-bank verification, or user artwork approval.
- Original V121/V123 Git blob SHAs are pinned and checked before screenshot analysis. Missing screenshot frames fail closed.
- New scripts/test_v203_canopy_structure.py independently verifies that missing frames fail, blurred neighbors fail, and even identical synthetic pictures **never** set human/source/production approvals true.
- New .github/workflows/qa-v203-photo-microstructure.yml runs all inherited V202 road-pixel, route, old detail, camera, touch, cache, bridge/tap regressions, then V203 unit tests and the new stricter screenshot gate; uploads all actual frames and a visual high-frequency residual contact sheet even if the new gate rejects art.

## Independent local audit of actual V202 CI screenshots (not a CI claim)
- Chromium portrait: WEST fine-luma **0.5527**, fine-area **0.5847**; SOUTH **0.5278**, **0.5421** relative to Matrei.
- Chromium landscape: WEST **0.5328**, **0.5165**; SOUTH **0.5046**, **0.4723**.
- WebKit portrait: WEST **0.5524**, **0.5810**; SOUTH **0.5280**, **0.5391**.
- WebKit landscape: WEST **0.5326**, **0.5151**; SOUTH **0.5043**, **0.4702**.
- **All 4/4 configurations reject WEST/SOUTH** under the new 0.70 necessary-structure gate. Local unit tests passed 3/3; local enforce mode exited nonzero as designed. These numbers reflect screenshots, not an assertion that 0.70 guarantees natural artwork.

## Remaining RED blockers
WEST/SOUTH source-derived geographically coherent, period-safe high-resolution game art; V121-to-real-world registration; bridge banks and onward destinations; seamless photo/terrain transition; four V100 zoom tiers; physical iPhone visual approval. Modern V199/V200 source crops are **not registered to V123 game-world cells** and are not silently pasted in.

gameArtApproved=false, geographicRegistrationVerified=false, historicalRoadsVerified=false, physicalIPhoneApproved=false, productionApproved=false.

No merge/deploy or paid service. Next productive step is authentic geographically justified artwork, not adding artificial noise to pass this new diagnostic.

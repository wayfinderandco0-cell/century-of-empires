# V257 — original WEST replacement with physically drawn cartway and small bridge (NOT APPROVED)

Date: 2026-10-28. **No production promotion, no historical/geographic verification.**

## Pre-change evidence

Read GitHub issue #9 through V256, checked newest branches and Actions (V256 final run 40638168780), downloaded genuine V253 Actions artifact 12787641727 and **opened the actual WebKit portrait three-octagon gameplay screenshot**. WEST/SOUTH in that browser screenshot still show the rejected licensed Kosovo photographs, with the V123 route crossing forest rather than a physical road. This is real browser evidence, not an AI-generated QA board. Also inspected V256's original image pixels and source-road overlay. V256's corrected WEST source needs **160.15px** deformation (> immutable 155px limit), so it must be replaced.

## Substantive original image replacement

Selected a DIFFERENT original fictional 1536×1024 WEST oblique-aerial landscape: `winding_track_through_alpine_valley.png`, SHA256 `2f7b6171c8fa479a61d372a7027e98aa0296ece92e38fc8908bbf65c4d7300fa`. It depicts a continuous, physically embedded two-rut cartway, rocky termination at the western endpoint, an existing small stone bridge over a tributary, and varied river/forest terrain. No new road stripes are painted by the processing code: road **pixels and surrounding terrain move together**. This is **OpenAI-generated fictional project artwork**, not licensed Austrian orthophoto evidence, a source-backed 1780 road, independent natural tiepoints, or user-approved art. Do not label the bridge or banks historically verified. The original PNG remains a local study artifact, NOT in GitHub or deployed; rights/provenance must be checked before public distribution.

SOUTH remains the distinct V254 fictional hut-ending source SHA256 `034246c5d9471cd6d87673daa48fb1a014dab38d414626677f6148ce8c7d08f3`; its prior 20-point physical trace is unchanged. Both original PNGs and processed images were inspected locally at native 1536×1024. The unchanged V123 Git blob hash is `09f04b4062e24fbacbb645307462cdddce2b2aa3`.

## Actual local source-pixel measurements (NOT CI/browser art acceptance)

| Necessary geometry | V256 WEST rejected source | V257 new WEST | SOUTH unchanged |
|---|---:|---:|---:|
| Max paired road-anchor displacement | 160.15px (FAIL) | **134.99px (PASS)** | 66.42px (PASS) |
| Minimum sampled Jacobian | 0.3626 | **0.5193** | 0.6999 |
| Folded fraction | 0 | **0** | 0 |
| Source coverage | 99.8345% | **99.8178%** | 99.8427% |
| Maximum anchor remap error | — | **1.001px** | 0.666px |

The new WEST improves the previously blocking deformation by **25.16px** without relaxing any numerical thresholds or changing V123. However, the hand-traced source cartway is not an independent geographic tiepoint; subpixel mathematical remap accuracy does **not** establish subpixel physical road contact. Actual image inspection shows the red V123 route mostly follows the WEST physical cartway and passes near the existing small bridge, but there is still possible road-center offset of several pixels, bridge-bank/source-to-game registration is unverified, and neither Matrei seam is visually approved. SOUTH still visibly drifts through its middle bend and remains rejected.

## Code, testing and safety

Four additive files on isolated branch `terrain-v257-original-west-bridge-cartway-replacement-20261028`: this README, `scripts/v257_replacement_west.py`, `scripts/test_v257_replacement_west.py`, isolated CI. The code rejects unpinned originals, verifies the immutable V123 SHA, tests old WEST still fails, tests new WEST necessary geometry passes, leaves SOUTH trace unchanged, tests synthetic road-pixel transport, and only processes real original PNGs when explicitly supplied. Eight tests pass locally **with the actual PNGs**, including actual-image processing; CI without originals must report a skipped real-image test, never claim browser artwork acceptance. No existing game files, Matrei, army sprites, V94 campaign/saves, core mechanics, or V121/V123 roads/bridge graph changed. No main merge, spending or deployment.

## Unresolved acceptance

Production gate **RED** until original high-resolution WEST and SOUTH art is hosted with reviewed provenance/rights, independently reconciled natural source/game tiepoints (V209 remains unverified) or clearly labelled fictional geometry, physically correct bridge banks and Matrei border transitions, strict V203 image metrics, four exact-art Chromium/WebKit iPhone portrait/landscape gameplay screenshots, human inspection, and explicit **user visual approval**. SOUTH middle-bend drift must be repaired without fake roads. **Three octagons unfinished.**

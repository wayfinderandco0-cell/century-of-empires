# V171: V170 real phone screenshots — fail-closed art review (2026-10-24)

Source: original, unmodified **V170 WebKit/Chromium** portrait/landscape screenshot ZIP from [successful technical QA 40139621442](https://github.com/wayfinderandco0-cell/century-of-empires/actions/runs/40139621442), artifact 12578300700. Inspected the actual eight center/West/South/whole screenshots and measured all twelve same-configuration center/West/South captures. This is NOT an approval of the three octagons.

## Visual findings

The Matrei river, bridge, forest and settlement remain a recognizably detailed painted photographic island. The Western Pass and Southern Valley are much less detailed, with conspicuous synthetic speckled tree shapes and a distinct photographic/material transition. The western and southern graph cartways terminate at question-mark survey-limit symbols in apparently open ground. The full crossing image does not resolve the physical bridge banks or independent historic road provenance. Passing movement and technical phone checks does not cure these problems.

## Original V140 image-detail thresholds, applied unchanged to V170

Minimum relative 1px luminance gradient **0.35** and minimum relative strong-edge density **0.25**, compared against Matrei at the same viewport, browser and orientation. The audit compares the center 58% horizontal / 56% vertical HUD-free image area; the original center opening capture is the Matrei reference. All results are *ratios* against Matrei, not historical correctness scores.

| Configuration | West gradient | West edges | South gradient | South edges | Gate |
|---|---:|---:|---:|---:|---|
| Chromium portrait | 0.3085 | 0.2107 | 0.4437 | 0.4122 | FAIL West |
| Chromium landscape | 0.2130 | 0.1209 | 0.2584 | 0.1685 | FAIL both |
| WebKit portrait | 0.3159 | 0.2316 | 0.4493 | 0.4269 | FAIL West |
| WebKit landscape | 0.2180 | 0.1261 | 0.2643 | 0.1766 | FAIL both |

**Outcome: 0/4 phone configurations satisfy both neighboring-detail requirements.** The existing V170 technical CI succeeded because it checks boot, route, pan, seams, and basic contrast rather than this strict neighbor-versus-Matrei detail parity. This is not a regression of movement code; it is a newly exposed art-acceptance failure.

## Code and verification

- Isolated branch `terrain-v171-v170-visual-rejection-gate-20261024` adds `scripts/qa_v171_neighbor_detail.py`, six positive/negative unit tests, and a dedicated fail-closed four-phone CI workflow.
- All **six synthetic unit tests PASS locally**; the unmodified V170 screenshot artifact was independently audited and **fails** as reported above.
- The V171 workflow regenerates phone screenshots, audits them with the unchanged V140 thresholds and retains failure evidence as an artifact. An expected red art gate is more accurate than a false green release signal.
- No original V121 painting, V123 road geometry, V94 campaign, saved games, main branch or live preview is modified.

## Next task

Replace West/South decorative synthetic terrain with **distinct, source-informed, period-interpreted game-frame artwork**, after validating V121/V123 landmark correspondence to geographic source imagery. V168/V169 aerial sectors are modern SOURCE coordinates, not registered V123 GAME terrain, and their asphalt, roofs and 2023 labels are excluded/unknown. Do not paint speculative historic road continuations, fake bridge banks or new conquest targets. Preserve all V140/V171 visual gates and obtain physical iPhone acceptance at four zoom levels before any production promotion.

`productionApproved=false`, `v123RoadsGeoregistered=false`, `physicalIPhoneApproved=false`.

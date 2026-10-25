# V174 — evidence-gated LOD for three modern geographic SOURCE sectors

**Date:** 2026-10-24 (America/Chicago). **Branch:** `terrain-v174-source-l-lod-eligibility-20261024`, forked from V173 `f831e214`. This is not a game-art replacement, playable map or historical road survey.

## Why this change

The actual V171 WebKit portrait/landscape screenshots (artifact 12578863866) still show a detailed Matrei island surrounded by synthetic West/South texture and two survey-limit road endpoints. V171's strict four-browser GAME-art acceptance remains **0/4**. The V173 real geographic SOURCE L artifact contains genuine high-resolution imagery, but excluded modern roads/roofs and the unacquired southwest quadrant are transparent. Rendering them as complete terrain or automatically enabling ground zoom would fabricate geographic content.

## Implemented

`scripts/v174_source_l_lod.py` reads and **fully re-verifies** the original 18 V168 JPEG identities and V169/V173 modern-source exclusions. It deterministically partitions the exact 1536×1024 SOURCE L alpha mask into **48×32 = 1,536 blocks of 32×32 pixels**. Every block stores the exact count of retained modern source pixels (0–1024), distinguishes fully retained, mixed and entirely excluded/unknown blocks, and preserves the southwest unknown quadrant as all-zero. A small coverage diagnostic PNG is emitted and byte/pixel verified. This is a geographically sourced **availability index**, not invented terrain detail.

All four named zoom tiers are represented but explicitly `gameArtEligible=false`, `playableRoadsEligible=false`, and `deepZoomEligible=false`. Retained imagery is still modern and unreviewed. Source→V123 registration, historical road/bridge evidence, physical iPhone approval and production approval remain false.

## Real verification

[GitHub Actions run 40154595873](https://github.com/wayfinderandco0-cell/century-of-empires/actions/runs/40154595873) **SUCCESS**: original V121/V123 immutable identity tests, V168 geography tests, V169/V173 modern-exclusion tests, **eight V174 synthetic/negative tests**, actual 18-tile source reconstruction, exact alpha coverage and output re-verification. The downloaded [artifact 12583513402](https://github.com/wayfinderandco0-cell/century-of-empires/actions/runs/40154595873/artifacts/12583513402) was inspected independently.

Measured retained source pixels and block classes (each source sector is 24×16=384 blocks):

| Sector | Retained pixels | Fully retained | Mixed | Entirely excluded |
|---|---:|---:|---:|---:|
| West | 370,771 | 332 | 47 | 5 |
| Center | 330,064 | 284 | 74 | 26 |
| South | 268,387 | 221 | 83 | 80 |

Southwest unknown region: 384/384 blocks zero. Total SOURCE blocks: 1,536. No masks, routes, paintings or game saves were altered.

## Still blocked

These are **modern source sectors, not three playable V123 game octagons**. A retained pixel is not historical approval. No independent V121↔source geological landmarks, valid road transform, surveyed historical bridge banks, completed West/South period-interpreted artwork or user iPhone acceptance. Existing V171 strict game-art test remains **0/4**; this new source test does not supersede it.

**Next highest-impact task:** Author a separate source-first period-interpreted GAME-art prototype that renders only source-supported natural materials, clearly excludes/flags unknown modern holes, and tests all three neighboring tile centers on real iPhone-layout browsers. Do not copy the 2023 orthophoto/modern asphalt or imply the V123 graph is registered. Preserve original four-browser route/seam/detail gates; no merge/deploy until the user approves the visuals.

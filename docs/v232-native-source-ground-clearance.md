# V232 — native source ground clearance (isolated, RED)

**Date:** 2026-10-27. **Purpose:** Stop wasting full four-browser screenshot
runs on WEST/SOUTH source photographs that physically cannot support the
unchanged V123 cartway. This is a **necessary preflight**, not new playable
art, a 1780 road survey, source/game registration, or user visual approval.

## Why this test is materially different

V231 inserts a **synthetic meadow strip along the graph before rendering**.
Testing only its generated WebP can mistakenly classify a painted rock crossing
as open ground. V232 instead extracts the exact, unmodified 1536×1024 crop
from each original SHA1-pinned CC0 photograph **before** any road or canopy
editing. The test samples the V123 route with a 25px-wide ground neighborhood
at ~4px intervals and reports dark canopy, bare rock, route obstruction and
longest continuous blocked section. The route comes from
`terrain-grid/v123-atlas.js` itself; no new endpoints or graph edits.

## Original sources and license

- WEST: Stijn te Strake, *Forested mountain valley (Unsplash).jpg*,
  Schönenbach/Bezau, Austria, original Wikimedia Commons SHA1
  `4a01fd2356056ceea1bfdf0374751040fdbd0145`.
- SOUTH: Volker Schnäbele, *Turquoise mountain lake (Unsplash).jpg*,
  Triebental, Austria, original Wikimedia Commons SHA1
  `776d4f0f7959d1ee1f14dfdc10ae8c3113a2ace1`.
- Both **CC0 1.0** (source URLs and source SHA256 in generated manifest).
  They depict **modern, non-Matrei Austrian locations**. They are not
  evidence of 1780 cartways, historical vegetation, Matrei geography or
  the V209 source-to-game tiepoints.

## Reproduced test result (actual unmodified source pixels)

Ran `python scripts/build_v232_unaltered_source_crops.py` followed by
`python scripts/v232_route_ground_preflight.py` on the resulting native
PNG crops. Python six negative/positive controls passed. The V123 JS file
SHA256 is `c58c935d9e2a29451e74fde08fb01c5ff5a7d2855ff871faad0f3ac6c997caef`.

| Native source | Open roadbed area | Open route samples | Bare rock | Longest blocked run | Result |
|---|---:|---:|---:|---:|---|
| WEST | 0.72154 | 0.67178 | 0.00363 | 180px | **FAIL** |
| SOUTH | 0.46165 | 0.28223 | 0.43449 | 656px | **FAIL** |

Necessary thresholds: >=0.72 for both open measures and <=70px
continuous obstruction. They are **not** a sufficient game-art approval test.
On the V231 **post-inpainting** images SOUTH misleadingly appeared to pass
this preflight. The unmodified source exposes the actual rock obstruction.
Actual red/green diagnostic overlays were rendered and inspected; WEST has
intermittent dark-tree obstructions, SOUTH has a long steep rock obstruction.

## What is deliberately unchanged

No V94 campaign/saves, V100 mechanics, unit sprites, V121 Matrei artwork,
V121/V123 cartway/bridge geometry, main V192 or production files were edited.
No spend, merge or deployment. V203 numeric and human/physical-iPhone gates
remain unchanged and RED. The V231 four-browser gameplay tests already
passed on the unchanged code, but V231's visual art failed all four. V232
does not claim a fresh four-browser run or new user approval.

## Next substantive artwork work

**Reject both V231 source crops** rather than applying more road strips,
photo patches or cosmetic noise. Author two coherent, genuinely distinct
full-cell Alpine landscapes **around** the exact WEST/SOUTH road envelopes
and real Matrei seam/bridge-bank geometry. Verify the pre-inpainting native
ground before any expensive browser QA; then run unchanged strict V203,
Chromium/WebKit portrait/landscape, and human screenshots. Independent
V209 tiepoints, 1780 road evidence, meaningful destinations, physical iPhone
and user visual acceptance are still missing.

`sourceRegisteredToV123=false; historicalRoadsVerified=false;
bridgeBanksVerified=false; humanVisualApproval=false;
physicalIPhoneApproved=false; productionApproved=false`.

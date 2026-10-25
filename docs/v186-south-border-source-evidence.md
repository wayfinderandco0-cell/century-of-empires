# V186 — ten-tile cross-border SOURCE candidate overlay (NOT GAME ART)

**2026-10-25.** Isolated branch `terrain-v186-south-border-source-candidates-20261025`. No edits to main, live deployment, V94 campaign/saves, V121 painted photo or immutable V123 road controls.

## Baseline and evidence

Reviewed issue #9 through V185, successful V185 CI [40198021170](https://github.com/wayfinderandco0-cell/century-of-empires/actions/runs/40198021170), V184 original 60-tile imagery, and the prior actual V171 WebKit portrait GAME screenshot artifact 12578863866. The **GAME** screenshot is still rejected: sharp isolated Matrei photo, synthetic Western Pass/Southern Valley, and unverified road termini. V171 strict GAME acceptance remains 0/4.

## What was coded

- [V186 acquisition and verification](../scripts/v186_south_border_candidates.py) derives 10 native EPSG:3857 256px WMS requests for **rows 10–11** of V184's geographically registered 5×12 zoom-14 overview; tile `r11c03` is cross-checked byte-for-byte at the WMS request URL level against the independently verified V185 probe.
- Each candidate South Tyrol 2023 JPEG is retained with SHA256, byte count, original Austrian JPEG SHA256, exact native XYZ and WMS bounds. Source: Autonomous Province of Bolzano / South Tyrol, [2023 orthophoto metadata](https://data.civis.bz.it/de/dataset/ortofoto-2023), conservative CC BY 4.0 attribution; original Austrian basemap.at CC BY 4.0 attribution retained.
- The **1280×512 RGBA candidate mask** has alpha 255 only when the Austrian pixel is near-white AND the independent South Tyrol source pixel is non-white. Every observed non-white Austrian source pixel remains alpha 0. No compositing into the GAME, seam blending, invented terrain, historical-road assumptions, or modern-infrastructure removal.
- [Eight fail-closed synthetic tests](../scripts/test_v186_south_border_candidates.py) check exact geometry, immutable false approvals, unchanged observed Austrian pixels, parent/alternative/overlay tampering, forged approval metadata and missing/malformed WMS imagery.
- [CI workflow](../.github/workflows/qa-v186-south-border-candidates.yml) first verifies V184's real 60-tile artifact, with original verified re-acquisition fallback after the artifact expires, then acquires all ten independent WMS tiles and regenerates the exact mask.

## Verified run and actual-image inspection

[GitHub Actions run 40202212082](https://github.com/wayfinderandco0-cell/century-of-empires/actions/runs/40202212082) **PASSED**: 11 V184 + 7 V185 + 8 V186 tests (**26 total**); original real V184 source verification, ten real South Tyrol WMS JPEG downloads, exact mask regeneration and output verification.

[Actual V186 source artifact 12602097229](https://github.com/wayfinderandco0-cell/century-of-empires/actions/runs/40202212082/artifacts/12602097229) downloaded and visually inspected, including transparency checkerboard. **138,560** native candidate pixels in the bottom two rows; exact count of originally near-white pixels there is also **138,560**. This is an image-source candidate measurement, **not 138,560 approved historic/game pixels**.

Tile-by-tile candidate pixels:

| V184 tile | Candidate pixels |
|---|---:|
| r10c00 | 0 |
| r10c01 | 0 |
| r10c02 | 8,321 |
| r10c03 | 6,336 |
| r10c04 | 0 |
| r11c00 | 0 |
| r11c01 | 7,126 |
| r11c02 | 46,727 |
| r11c03 | 59,118 |
| r11c04 | 10,932 |

The actual candidate mask forms a geographically plausible irregular cross-border wedge; it **still visibly includes modern highways/transport infrastructure**. The edge is a *source-coverage boundary*, not an approved blended terrain seam. Near-white Austrian pixels may represent no-data, snow, cloud or provider effects; there is no independent border survey. No claim of historical appearance or safe automatic stitching.

## Remaining blockers / next action

1. Inspect actual Austrian-versus-Italian overlap and edge color/texture at each candidate boundary; independently distinguish true source no-data from snow/cloud and reject false coverage.
2. Extend bounded source recovery to any remaining suspected upper-row gaps only when the imagery shows them. Modern highways, rail and age-unverified settlements must be excluded or historically interpreted before game use; never paste modern orthophoto unchanged into 1780–1880 art.
3. Independently register the **three actual GAME octagon footprints** and historical road/bridge-bank controls to geography. Do not move V121/V123 controls on conjecture. Then create connected, period-appropriate art and rerun unchanged V140/V171 strict four-browser route/seam/detail/movement QA plus physical iPhone visual approval.

All historic, bridge, GAME-art, iPhone and production approval flags remain **false**. No main merge or live deployment.

# V194 — weathered cartway material and pixel evidence (2026-10-25)

**Status:** isolated graphics trial, NOT approved production game art. This branch extends V193 camera coverage; it does not modify `main`.

## Baseline and boundaries
- Main baseline: V192 `b29bbf06f2848d641b4b3d80ab0a64728958431b`, with passing four-configuration road/terrain QA.
- V193 branch baseline: `65fa2f4d7dd63604ec5fc0c811b99d80d356e284`, with successful camera-coverage QA.
- Only the neighboring road **pigment** function changed in the graphics HTML. The V121 original Matrei image, V123 graph, bridge positions, unit sprites, game rules, and campaign files are untouched.
- The road centerline remains the original V123 polyline; no curved visual road is allowed to diverge from unit navigation.

## Implemented
- Reduced the neighbor road's continuous layered pavement widths (27/22/18/13 to 22/18/14/10 world pixels).
- Replaced two uninterrupted parallel ruts with deterministic broken wheel marks, irregular gravel shoulders, sparse verge vegetation, and small roadbed flecks.
- Added `scripts/qa_v194_cartway_pigment.py`, which tests actual rendered painter pixels rather than treating a navigation-to-navigation distance as independent visual evidence.
- New branch-only workflow reruns V194 pigment coverage, V192 mobile cartway routes, V192 three-center detail parity, and V193 mobile camera bounds on Chromium and WebKit, portrait and landscape.

## Verified
- GitHub Actions [V194 run 40222168567](https://github.com/wayfinderandco0-cell/century-of-empires/actions/runs/40222168567): **PASS**, all four test stages.
- V194 pigment QA covers all 23 neighboring polyline segments and 514 on-road samples in each phone configuration; zero unpainted centerline samples. The straight-road probe has 154/154 centerline pixels present and 85 painted versus 69 unpainted edge probes, confirming nonuniform shoulders.
- CI screenshot evidence: [artifact 12610106211](https://github.com/wayfinderandco0-cell/century-of-empires/actions/runs/40222168567/artifacts/12610106211).

## Visual review — still rejected for final game art
I inspected the actual Chromium portrait close-zoom captures of all three regions, not just numerical metrics. The original Matrei artwork has a detailed river, bridge, cliffs, and forest. The west and south regions still look materially flatter, with synthetic repeated-looking vegetation and a relatively smooth road strip. The three regions are **not visually equivalent**, despite passing the numerical detail floor. There are no verified new town/bridge positions for the neighboring octagons; no historical source-to-route registration was established. Do not describe these three octagons as complete or visually approved.

**Next safe graphics work:** improve the actual western/southern scenic material toward Matrei-level recognizable cliffs, drainage, and vegetation *without* duplicating Matrei imagery, inventing towns/bridges, or moving V123 roads. Keep all existing route/phone gates. Any replacement regional artwork needs independent human visual review and source/geographic evidence before acceptance.

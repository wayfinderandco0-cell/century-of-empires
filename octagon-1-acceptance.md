# Century of Empires — Octagon 1 acceptance contract

This is a **single-cell source-art pilot**, not another playable game version. Keep `v94.html`, campaign data, existing branches, production movement, and all saves unchanged.

## Source-of-truth rule

The playable road must be a visible road **in the same landscape**. Movement and visible cartway must sample the same road geometry. A successful graph-to-overlay equality test is *not* evidence that the underlying terrain photograph depicts that road.

The standalone `octagon-1-road-authoring.html` displays the actual source JPEG embedded in V119 and isolates the east-bank road, with the bridge approach and stone bridge fixed. Edits to east-bank control points change road paint and army samples together; this is an authoring tool only. Road edits are held locally in the browser and can be copied as JSON; they are **not** loaded into the campaign.

## Current unresolved art problems

- Original JPEG still contains an embedded Matrei am Brenner banner; V119 adds a separate map-anchored label, which does not erase it.
- The east-bank cartway is an *artist-authored overlay* and is not backed by a consistently painted continuous historical road across the mountain terrain. It may visually cross rocks, creeks, or slopes without a road cut.
- The south branch has not been independently marked against the painting.
- No adjacent east octagon art has been finished. Matching `eastEdge: [1100,704]` to `nextCellEntry: [0,704]` proves only a coordinate contract, **not** a neighboring traversable road.
- iPhone Safari physical inspection and historical geography checks have not been completed.

## Definition of complete / required before production

- [ ] A **single authored landscape** with historical mountain topography, passable slope, vegetation, buildings, river, bridge and both road branches that agree visually
- [ ] Remove baked-in labels; draw map-anchored labels on a separate UI layer
- [ ] Every section of the road has an actual road surface in the terrain source; no overlays masquerading as source-art proof
- [ ] At each fork, bridge and boundary: a continuous, plausible cartway, including the far-bank bridge exit and painted route in next octagon
- [ ] Soldiers never leave road centerlines under movement, pauses, camera follows, panning or zoom changes
- [ ] Four browser cases pass (Chromium/WebKit × portrait/landscape) and manual physical iPhone Safari review passes
- [ ] Test *artwork against the route*, not just route against the code that draws itself. Review screenshots with the route guide turned **off**, then turned on.
- [ ] Terrain affects gameplay as specified separately (forests/mountains/river/roads); terrain engine and game saves untouched until acceptance

## Gate

**Do not mark the first octagon finished or multiply it across Europe** until all of these are checked and approved by the owner. A green CI check means the geometry editor functions; it does not mean the artwork is approved.

### Candidate provenance

- Source art: V115/V119 embedded 1100×842 JPEG.
- Fixed bridge arrival: `[699,799]` in source art pixels.
- Current *candidate* east exit: `[1100,704]`.
- Future next-cell matching entry: `[0,704]`. The neighbor is not built.
- No historical-road claim; no production approval.

## Prototype controls versus real campaign interaction (approved requirement, Oct 22 2026)

The standalone Octagon 1 road-authoring inspector may show explicit `Village`, `Bridge`, `East bank`, `Edit road`, `Add point`, `March`, `Halt`, `Tools`, `Undo`, `Reset`, and guide/debug controls **for development and QA only**.

In the finished Century of Empires game, these developer/test controls **must not appear on top of the gameplay map**. Preserve and integrate the existing game mechanics and unit interface instead; do not implement a second, incompatible movement system or rework the established controls for this prototype.

- Player selects an army/formation and uses the **existing tap-to-move / movement-order system** to designate a destination. The underlying connected road/terrain graph determines available movements, unit paths and ETA.
- Where the south village road and eastern bridge provide alternatives, the game must support selecting the intended route through its **existing army-order/path-selection interaction**, not dedicated permanent `South` and `Bridge` buttons. If ambiguous, show a **contextual, temporary route choice or waypoint preview** as part of the unit order, never persistent prototype keys.
- Retain established formation mechanics: split, march, halt, retreat, entrench, forced march/fatigue, leaders, battle engagement and unit movement timing wherever supported by the campaign code. Do not silently change gameplay rules to get the octagon demo to work.
- Show normal unit indicators (flag, troop count where intelligence permits, strength/health and morale bars) according to existing zoom/fog-of-war requirements, not developer waypoint markers or diagnostic UI in the live game.
- Prototype route editing and geometry inspection are restricted to the **development tool**; gameplay routes are not edited by players. The eventual production road graph uses approved authored art but calls the established unit movement/order engine.
- Acceptance: the road fork is a functioning graph junction; either destination can be ordered from the existing unit UI; the chosen route is visibly followed with correct ETA and no water crossing; no `Edit road`, `Add point`, `East bank`, `Village`, `Bridge`, `Tools`, test `March` or debugging buttons clutter the normal campaign map.

**Integration gate:** Do not call Octagon 1 production-ready until this existing-game-order compatibility has been tested. The current authoring editor remains separate and intentionally retains its editing/testing controls.

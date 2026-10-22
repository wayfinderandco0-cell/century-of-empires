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

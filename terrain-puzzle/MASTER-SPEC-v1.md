# Century of Empires — Historical Atlas Puzzle Framework v1
Date: 2026-10-20 · Status: geometry/design checkpoint, **not approved graphics**.

## The core idea (locked)
One uninterrupted historically plausible European atlas lies beneath the game's dynamic borders, cities, flags, armies and UI. A layer of *invisible, georeferenced octagonal art cells* sits over the shared atlas. Each cell is a piece in one enormous puzzle. Do **not** paint separate independent maps and stretch them together: every piece is generated from the same coordinate system and master geographic features, and joins its neighbors at registered boundaries. Player never sees a tile outline.

### Geometry correction
**Regular octagons cannot tessellate a plane alone.** Use the regular 4.8.8 octagon-square tessellation: the primary cells are regular octagons; four corner gaps around each are small rotated square connector cells. The square cells are auto-generated seam patches, not extra hand-painted regions. The art continues across them, and they participate in routing. Do not draw black gaps or expose connector outlines. Other shaped boundary/coast cells may be clipped by the atlas footprint.

For a cell pitch `L=1000 m`:
- Corner cut `c=L/(2+sqrt(2))=292.8932188 m`.
- Octagon vertices in a local plane (east x, north y), ordered counterclockwise, are the first prototype JSON's `geometry.vertices_xy_m`.
- A connector is a square rotated 45 degrees, centred at each grid intersection `((i+1/2)L,(j+1/2)L)`, with its four axis tips `(x±c,y)` and `(x,y±c)`.
- Four diagonal sides connect to connector squares, and four cardinal sides connect directly to adjacent octagons. The layout covers the entire plane with no holes if computed from the registry rather than hand-aligning polygons.
- Routing points are **invisible**. All eight edge-midpoint portals initially exist as *candidates*, not guaranteed military passages. Mountains and impassable water can disable them; add verified passes/ford/bridge/trail nodes separately.

## Layers, bottom to top
1. **Atlas foundation:** single registered elevation/coastline/water source. Continental map uses a validated Europe-wide projected frame (target EPSG:3035); the first Brenner cell initially uses V102's explicit local metric approximation. Do not silently use the local formula for all Europe.
2. **Historical date layers:** year/scenario-specific political boundaries, settlement names, period roads and geography; do not confuse 1800 borders with 1780 or 1880. No modern highways, stations or houses presented as historical. Where historical features are reconstructed, clearly tag them illustrative.
3. **Art patch layer:** each cell renders terrain materials (stone, exposed slope, rivers, woods, valleys, villages), with consistent lighting, color scale and pixel-density targets. Neighbor cells must match atlas-controlled features and edges.
4. **Gameplay layer:** existing provinces, economic systems, saved armies and combat are **not rebuilt**. A separate invisible point-and-edge graph provides georeferenced movement, supply, river crossings, mountain passes and battle positions; use it only after visual approval and migration testing.
5. **UI layer:** borders, unit badges, morale, army strengths, route graphics visible as appropriate; tile borders, octagons, connector squares and path nodes remain fully hidden except an opt-in developer debug view.

## Puzzle assembly rules
- Fix the geographic transform *once*. Every cell stores index, metric footprint, atlas year metadata, central reference, and asset provenance.
- Store one canonical shared edge, identified by endpoint coordinates and ownership, in a registry. Adjacent art patches sample the same source, not guessed parallel rivers or shifted paths.
- Art may bleed 60m beyond the clipped cell mask to permit seam blending, but the authoritative terrain and routing data remain shared; art must never move a real summit, stream or coastline.
- Each edge is reviewed in pairs: color, elevation, forest mass, river continuation, trail/road continuation, and nighttime/performance conditions. Until neighboring cells are accepted, show the atlas foundation rather than an exposed seam.
- Start with a single octagon and its four automatic square connectors; then create an immediately adjacent octagon and test the seam. Do not build Europe or the full node graph first.
- Maintain an LOD hierarchy: full Europe atlas is aggregated. One kilometre is the **detail prototype**, not a mandate to hand-author millions of cells. Reuse approved art families under geographic masks, with bespoke cells for visually or strategically distinctive places.

## First piece: Brenner/Navis prototype
- ID `BNR:O:0:0`, centered at the V102 local origin **11.52°E, 47.13°N**. Approximately 1km pitch, with continuous atlas area outside the octagon.
- Footprint, eight portal candidate midpoints and connector IDs are in `terrain-puzzle/BNR-O-0-0.json`. This currently represents geometry, **not a verified surveyed kilometer of 1800-era forest or roads**.
- Preserve V97 elevation samples and relief. Numeric spacing is roughly 160–230m; rock outcrops, trails, trees and individual slopes inside the tile must be visually plausible illustrations, never advertised as measured 30m elevation.
- Output art brief: a polished historical Alpine valley that visibly includes coherent forest canopy, irregular meadow clearings, rock slopes, one natural stream and an appropriately narrow pack trail where geography permits. Both side edges must continue neighboring geography.
- Reference visual style: the four-tier geographic zoom visual previously approved by the user; compare actual iPhone portrait and landscape. Do not make a new renderer merely to hide unsuitable art.

## Invisible travel graph
- Eight provisional edge portals on the primary octagon, center route anchor, and geographically grounded extra waypoints as needed. Avoid blindly enabling all eight passages: one mountain-wall edge should not allow crossing.
- Every routed edge has optional elevation gain, gradient, terrain, permitted troop types, capacity, river crossing, season, and duration. Edge midpoints sit on *true shared boundaries*; connectors route diagonally and are invisible.
- Do not alter battle rules or march speed until compared against existing campaign saves and rule balance. Combat modifiers attach to actual terrain sampled along movement/battle footprint, not to the art palette.

## Acceptance gates and freeze
1. **Geometry:** polygons regular and exactly connected; connector gap squares fill space; portal positions canonical; deterministic IDs; no visible seams or flashing edge gaps.
2. **Historical atlas:** relief and physical features align; timeline-specific borders and roads checked; ambiguities labeled illustrative.
3. **Artwork:** two neighbor pieces look like *one* realistic atlas at overview and reveal understandable terrain at near zoom. No dotted forest or triangle-tree glyphs, no fuzzy camouflage, no modern road artifacts.
4. **iPhone:** portrait 390×844 and landscape 844×390 visual QA plus real Safari review; UI remains fixed under pinching; performance acceptable.
5. **Gameplay:** old V94 / V100 / V101 / V102 / V103 and all saves untouched until an approved integration plan, automated tests and rollback path are signed off.

## First production milestone
This checkpoint locks puzzle geometry and the first cell. Next: create an **art-first standalone image for BNR:O:0:0**, inspect and approve the image before building additional map renderer code. Then add BNR:O:1:0 and verify shared N/S/E/W seams and square connectors. Do not merge incomplete terrain work into the playable game.

# Century of Empires — Octagon 001 vNext Production Specification

Date: 2026-10-20. State: **DESIGN AND ASSET CONTRACT; NOT COMPLETED ARTWORK**.

## Approved visual target
Use the user's approved illustration as the **art-direction benchmark**: detailed rocky Alpine slopes, natural irregular conifer forests, meadow pockets, rugged blue-green mountain stream with believable banks and rapids, winding narrow trail on accessible benches, coherent lighting. The illustration itself is NOT a historically measured river, bridge, or trail. It must be redrawn and registered to the actual first octagon.

## Non-negotiable principle
**Keep geography fixed, design a believable corridor around the terrain, then derive the visual trail and invisible troop dots from ONE authoritative corridor polyline.** Do not make an attractive map and paint an unrelated computer-generated path over it. Do not make the elevation data conform to an image. If the route is not demonstrably passable, its graph remains disconnected.

### Locked sources and coordinates
- Branch: terrain-puzzle-atlas-v1; main campaign/game files frozen.
- Cell ID BNR:O:0:0, center 11.520° E, 47.130° N, local x=east/y=north in metres, 1000m octagon pitch, 60m bleed. Pixel artwork source covers x and y from -560 to +560m. It is **full rectangular bleed imagery** clipped to octagon in the engine, NOT an octagon-only PNG.
- Exact polygon and eight structural portals: terrain-puzzle/BNR-O-0-0.json.
- Geographic river guides: terrain-v102/features.json; control points and boundary crossings: terrain-puzzle/BNR-O-0-0-geographic-control.json. Fidlerbach enters near northern edge (x~+171m at y=+500m), with Navisbach near southern boundary. Use all mapped vertices; no hand-straightening.
- Existing terrain: terrain-v97/brenner-data.json. Retained DEM spacing ~160–230m, **too coarse to validate cliffs, wheel routes or historic fords**; any finer rock, trees and paths are artistic reconstructions unless supported by better georeferenced sources.
- Prior route trial: terrain-puzzle/BNR-O-0-0-hidden-routing.json: 25 nodes, 23 links, 9 steep-flagged, 1 unverified water crossing, 13 preliminary foot candidates; all DISABLED in gameplay. These old nodes are evidence of where automatic corridor generation failed, not compulsory coordinates for the final painted trail.
- Shared eastern neighbor BNR:O:1:0: canonical shared cardinal edge x=+500m and y from -207.106781 to +207.106781m. Southeast connector: BNR:S:0:-1 centered on (+500,-500)m; never fake passage through it.

## Build order — do not skip
**Phase 1: registered physical base.** Import measured relief and existing mapped river centerlines in one local coordinate frame. Block out rock, scree, forest, meadow, steep slope and wet stream-bank areas. Map real/uncertain landform regions separately. Preserve original valley silhouette. Choose north-up projection; fixed world-space coordinates, never stretch an individual tile to fit its neighbor.

**Phase 2: high-resolution natural artwork.** Paint an editable 4096x4096 master spanning the 1120m full-bleed square, then export appropriate 1024/2048/4096px level-of-detail images for mobile. Layers: (1) terrain relief; (2) scree/stone; (3) soil/meadow; (4) canopy; (5) streambed/rocky banks; (6) water with controlled width/rapids/shadows; (7) trail surface generated from accepted corridor vectors; (8) crossings generated only from accepted crossing records. No baked route dots, octagon edges, numbered labels, compass, army, overlay buttons or bright blue geometric river lines.

For the **river** use varied banks, gravel, boulders, shade, opaque/deep pools and localized foam at suitable changes in gradient. Water style must have recognizable flow direction. No uniform cyan stroke; any illustrative water-width range needs later verification. Stream source coordinates remain authoritative.

**Phase 3: route drafting on real physical terrain.** On a geo-registered rendering of rock, vegetation and river, draw editable route-centerline geometry where travellers could actually move: valley floors, benches, switchbacks, clearings, and junctions. Do not make straight paths across cliffs. Author bridge/ford only with either historical support OR explicit designation as a speculative game-scenario feature and approval; until then, crossing remains blocked. Visual concept bridge near south edge is NOT approved as a real crossing. End a route where no defensible passage exists.

**Phase 4: dots from route, not route from dots.** Freeze each reviewed centerline as a uniquely named geometry record in local metres. Render its visible dirt trail and animate moving troop positions directly on that same polyline. Generate invisible nodes approximately every 40–65m on gentle straights, refining to 10–25m at tight turns, forks, steep transitions, bridge/ford entrances and registered polygon boundaries. Attach each node/link to exact geometry-id and vertex/distance intervals. Never connect node pairs by straight shortcuts that leave the canonical trail. All newly created route links default to disabled and have no travel cost until assessed.

**Phase 5: passability assessment.** Annotate each route span for infantry, cavalry and wheeled artillery separately. Treat the existing provisional slope heuristics (35% blocked; 16% cavalry candidate; 11% artillery candidate) only as screens, not universal historical movement rules. River crossing, slope, forests, season/supply and historical provenance determine final approval. Never infer a bridge from an illustration. Every visible crossing must have exactly one matching graph crossing record and vice versa. If approval fails, hide the false continuous road or keep a visibly broken path and block the link.

**Phase 6: stitch puzzle pieces.** Validate art bleed and canopy/rock/river consistency across the x=+500m shared edge to Octagon 002 and the southeast square connector. They reuse one atlas coordinate system, one river/trail geometry and the same feature endpoint positions. Hidden tile boundaries may be debugged but must never show as octagon seams in normal gameplay. A visible seamless landscape does not imply a military route exists across every edge.

## Data model per art feature
A feature has id, geometry_id, feature type (river/trail/crossing), editable local XY centerline, drawing style reference, real-source or illustrative provenance, terrain-clearance score and assessment, approved_for_render, approved_for_gameplay, troop type restrictions, optional crossing_id, registered neighboring edge/connector links. Keep art assets independently editable rather than making a raster the sole source of route geometry.

## Acceptance tests and hard fail conditions
1. **River visual test:** does it read as irregular shallow/deep water integrated with rocks, natural banks and shadows? Reject old bright-blue pencil stroke.
2. **Physical corridor:** do all illustrated trails visibly follow plausible terrain rather than cliffs, water or arbitrary shortcuts? All currently unverified crossing and steep links must remain non-traversable.
3. **Same-source alignment:** visible trail is generated from the exact vector used for nodes and army animations. QA target <=2 screen pixels misregistration at Terrain zoom, <=2 metres in world coordinates (zero ideal by construction).
4. **Historicity:** label speculative road/ford/bridges as speculative until approved; do not suggest the illustrated bridge is an authenticated c.1800 structure.
5. **Edge match:** shared river/trail feature endpoint difference exactly 0m from canonical source geometry; verify paint seam in all four map levels against eastern neighbor and the diamond connector.
6. **iPhone:** test clean and debug screenshots at 390x844 portrait and 844x390 landscape in WebKit, then obtain a physical iPhone Safari visual approval. Pinch affects the world camera, not browser UI; do not fill the screen with huge branding over close-up terrain.
7. **Performance:** load only visible LOD data and avoid shipping every future octagon at 4096 resolution. The master source can be large, but mobile runtime assets must be streamed/culled.
8. **Safety/continuity:** no changes to campaign save keys, V94, V100, V101, V102, V103, V104, V105, V106, playable game, armies or combat until the art AND seam gate passes.

### Stop rule
If geography or route accessibility is unverifiable with the available coarse elevation source, do not pretend it is proven. Keep any uncertain routes disabled; either seek better georeferenced terrain and period paths, or proceed as clearly labelled historical-game reconstruction. If the image still looks like generic camouflage, blurry slopes or a pasted water line, do not expand to more octagons.

## Immediate implementation milestone
Author ONE geographically aligned rectangular river/forest/rock terrain master for BNR:O:0:0, using the approved image only as a **visual style** target. Then draw one plausible foot-trail centerline from the actual terrain, export a clean view and a developer overlay showing that **the dots sit exactly on that visible trail**. No new Octagon 003 until the user approves the corrected tile and Octagon 001/002 seam.

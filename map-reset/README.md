# Map reset — 5 November 2026
## Single approved visual source
**Retire the unrelated map experiments as production candidates.** The visual baseline is exactly the original WESTERN PASS / MATREI / SOUTHERN VALLEY three-octagon artwork. Preserve the original Matrei V121 image. The West and South images in terrain-approved/ are byte-identical to the two images embedded in the original saved V267 three-piece playable file. These are references, not authorization to randomly tile complete mountain and village scenes across Europe. V300/V303/V304/V305 remain archived for reference only; do not reuse their artwork or substitute another map look.

## Road rule (non-negotiable)
Every main road the user can see is a registered polyline in one shared network; the exact same geometry paints roads and moves the army. No roads painted independently of the route graph. Every registered road point must be reachable from every other point through connected roads; road exits between sections meet at identical world coordinates. Tapping *any position along a road*, not just a town or node, is a legal movement destination. Small paths visibly baked into the three source images still require a final visual trace audit before production signoff; don't falsely claim all photographs are historically georeferenced.
Road-data source: V121 Matrei recorded polylines and the original V123 Western/Southern extension geometry. `approved-three.json` retains the exact coordinates. `road-engine.js` rejects disconnected added roads and routes to projected points along lines. `test-road-graph.cjs` verifies all existing segments and an example joined additional section.

## Visual expansion method — ONE map, divided into manageable artwork sections
1. Start with three original pieces and their exact border road anchors. Preserve original photos without reskinning.
2. Expand **outward from an existing border**, not into a random 50-cell grid. Generate/repaint adjacent physical terrain to match the edges of those originals without copying full villages/roads or building three more distinct map products. Use the accepted photo-realistic material quality. Do not call a procedural terrain filler approved art.
3. **Road-first for topology, art-first for approval:** select a connected route section, register its centerline and where it joins the existing endpoints, build/approve the scenic artwork around it, and then let the *same centerline* draw and route units. A new branch road must meet the existing graph at a node; valid dead ends are fine.
4. Keep map sections purely a rendering/storage optimization. The player sees a continuous world that pans/zooms, not separate game boards. There is no new per-tile order allowance, turns, economy, captures, etc. Integrate geographic coordinates with the original campaign's unit-order system only after the visuals and roads pass.
5. Where historical accuracy is required, research the period road and town positions independently. Do not claim a drawn corridor is historical just because its graph connects.
6. One new sector is accepted only when inspected at real iPhone size: no obvious seam, duplicate landmarks, phantom roads, or unreachable visible paths. Then expand in batches. The 50-tile graphic count is NOT an acceptance metric.

## Current result
- Exact original West and South art copied into source-controlled blobs without modification; Matrei V121 already present and unchanged.
- Captured eight original road polylines as data; all 98 road vertices in one component (five natural dead ends); an army can route to midpoints anywhere along them.
- New map art created: **0**. Whole Europe expanded: **NO**. Live campaign changed: **NO**.
- This reset creates the *reliable expansion contract*, not a falsely described finished map.

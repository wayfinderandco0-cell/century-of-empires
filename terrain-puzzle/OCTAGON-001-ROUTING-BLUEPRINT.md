# Octagon 001 — Hidden movement-node framework

This is a georeferenced candidate graph, **not an activated army movement system**.

- Invisible nodes are spaced about every 65 metres along **candidate accessible corridors**, not scattered uniformly. First: a valley-bank proposal offset 32m from the mapped Fidlerbach stream. Second: the preserved *illustrative* Navisbach-side pack trail.
- Each segment is checked against V97 elevations and all clipped V99-mapped streams. Intersections with water are **blocked until bridge/ford verification**. Gradient above 35% is blocked; above 20% is foot-only candidate; shallower slopes can be candidates for cavalry and wheeled artillery under more restrictive limits.
- These are terrain-screening assumptions, not 1800 historical-route evidence. The retained DEM samples are around 160–230m apart and cannot resolve every short cliff or switchback.
- The original eight edge midpoints remain polygon seam anchors, **not eight automatically passable exits**. Real corridor intersections at the boundary are the only plausible portal candidates, and must line up with a neighboring cell before activation.
- All generated edges: `enabled_in_game=false`, `travel_cost=null`, `historic_path_verified=false`.
- Future nodes: independently sourced town gates, known routes, authenticated bridges/fords and Alpine pass saddles, plus only those extra intermediate points required to follow curves. Riverbanks are obstacles as often as routes; streams themselves are not footpaths.
- The debug SVG is for engineering only; final game map and army interfaces must not show octagons, nodes, or underlying graph lines.

The game, V94, V100–V105 and all saves remain unmodified. Next step: compare node positions with the **approved terrain artwork** and construct a genuinely connected adjacent cell, without inventing crossings.

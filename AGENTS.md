# Century of Empires — project instructions

## Current user direction: 3 November 2026, America/Chicago

The current work is the historical map graphics and their integration with the existing game. The user has already established the unit sprites, orders, movement, and campaign behavior. Preserve those decisions. A map-art task is not authorization to invent another game.

### Preserve the established game

- Keep the original unit sprites, army controls, movement and order behavior, campaign state, and save compatibility.
- The recorded interaction is select an army, select a destination, then Execute, with the established route display and ETA. Use the actual existing implementation as the source for integration; do not rebuild it from a prose summary.
- New map regions do not introduce new commands, turn systems, order allowances, recruitment costs, capture rules, or movement restrictions.
- In particular, the separate 12-province demo's End turn button, two-orders-per-turn allowance, and its standalone economy/combat rules are not the approved replacement for the existing game.
- Terrain, roads, bridges, and settlement locations supply geographical data to the existing movement system. The existing rules determine which orders are available and what happens.
- Keep historical gameplay towns connected to existing settlement/province identifiers. Decorative hamlets and buildings are scenery; do not automatically make them objectives, order triggers, or separate campaign provinces.
- Artwork chunks/octagons are rendering units. Do not infer new gameplay rules or conquest units solely from an artwork boundary.

### Map deliverable

- One coherent historical map for the project's 1780–1880 setting, appropriate to the selected campaign start.
- When zoomed out, it reads as a continuous topographic map: landforms, water, mountains, forests, and restrained overlays.
- Zooming in gradually reveals terrain detail, roads, bridges, period buildings, decorative settlements, and the established historical gameplay towns.
- Pan and pinch zoom must work on iPhone, retain the focal point, and keep terrain, roads, towns, and units aligned.
- Use the three user-approved terrain renderings as the visual reference. Recover their exact assets from the existing work; do not substitute similarly named experimental versions or repeatedly reopen the accepted art direction.
- Reuse appropriate terrain art and decorative assets to expand efficiently. Place real terrain features and historical towns according to geographic data. Repetition or random placement of whole Alpine scenes does not demonstrate historical accuracy.
- Use the same geographic reference for visible routes and movement paths, so units travel along the roads and crossings the player sees.
- Keep dynamic ownership, routes, units, and gameplay labels separately addressable.
- A fully modeled 3D world, a new engine, or new game mechanics is not a prerequisite for making progress on this topographic map and close-up relief presentation.
- Treat historical sources and uncertain placements honestly; do not label schematic links or guessed settlement locations as verified historical geography.

### Work sequence and evidence

1. Locate the approved art and established unit/campaign implementation in the existing project before replacing anything.
2. Expand the geographically anchored map with the approved visual style and continuous roads, rivers, terrain, and settlements.
3. Connect those map coordinates to the existing unit system, preserving its orders and rules.
4. Verify map continuity, aligned movement, and zoom/pan behavior in an iPhone-sized WebKit view. A tile count or a working path graph alone is not visual acceptance or historical validation.
5. Report what was actually changed and tested. Distinguish an art preview, movement test, integrated campaign, and historically checked map.

### Verified scope drift at this correction

- The saved Century_of_Empires_12_Province_Playable.html contains a separate turn-based mini-campaign with two orders per turn. Its replacement rules must not be carried into the original game.
- V303-50-IMAGE-RESUME.md describes 50 cells made from three source images and a 57-link schematic graph. It explicitly does not establish a historical road map.
- This instruction file records the user's corrected scope. It does not claim the expanded historical map has been completed or that any game code has been corrected.

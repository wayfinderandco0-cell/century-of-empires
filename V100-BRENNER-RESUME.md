# Century of Empires — V100 Brenner Pass checkpoint
Updated: 2026-10-20

## VERIFIED / COMPLETED
- V100 interactive vertical-slice HTML: `v100-brenner-slice.html` originally implemented on `terrain-v100-brenner-gameplay`.
- Published that separate file to GitHub `main` with commit `793b2464a3490e1b7b983ef685a65fc5f601b476`. GitHub Pages deployment subsequently runs from main; verify deployment separately.
- Play URL: https://wayfinderandco0-cell.github.io/century-of-empires/v100-brenner-slice.html
- Source geography reused V99 measured Copernicus GLO-30 terrain, forest display, and official modern Austrian aerial photos plus OSM waterway data; V94 unit art reused.
- Four LOD stages: strategic overview **hides all towns/armies**, regional shows labels and army-color dots, mountains shows unit images/counts/status bars, aerial shows orthophoto plus troop overlay.
- Prototype army counts / force condition / morale displayed when allowed by detection.
- Austrian and Prussian sample armies follow **one** curated illustrative Brenner corridor, dynamically march, pause/reset and meet. Slope affects movement; a crossing slowdown is expressly illustrative.
- Fog of war hides enemy counts/locations until own scouting range or optional allied shared sight reveals them.
- Two browser QA runs completed; most recent run passed **20/20** iPhone-sized (390 × 844) Chromium checks, including zero JavaScript page errors, real aerial tile display, units, scout-sharing, commands and eventual contact. Screenshot outputs and report saved under `terrain-v100/` on the V100 branch.
- Visual screenshot review led to follow-up polish: collapsed source/legal note, separated contact markers, adjusted sprite artwork blending.
- Older V94 HTML, its real campaign saves and save keys **remain unchanged**.

## Still NOT done
- A real physical iPhone/Safari test has not been performed. GitHub Pages publication does not prove touch/pan success on the user's device.
- Brenner route follows plausible valley control points for an *illustrative prototype*, not an authenticated 1780 road. Ancient trails/bridges, historical forests, river-crossing specifics and battles remain to be researched.
- Movement is a fixed shared corridor with calculated slowdown, **not** Europe-wide route-aware pathfinding; the unit encounter is a meeting event, **not** an implemented battle simulation.
- V100 standalone scene is not wired into the production V94 game's economy, diplomacy, AI, combat, existing provinces or save state.
- Unit graphic composites remain prototypes; make cavalry and artillery look natural without needing screen-blended dark photographic backgrounds.
- Grounded geography/forests and close-detail textures outside the Brenner prototype remain unfinished.

## Next logical work
1. User view test: open V100 published link in iPhone Safari; evaluate portrait/landscape, tabs, forest/stream rendering, army scale and pinch/pan. Do not assume these verified based solely on headless Chromium.
2. Correct route fidelity against historical geographic sources, keeping **few strategic chokepoint routes**.
3. Finalize infantry/cavalry/artillery composite sprite and status UI.
4. Implement actual province-to-terrain-corrridor integration inside a **new game version** only after reliable standalone QA; preserve older campaign saves.
5. Expand Europe using reusable terrain + army LOD architecture only after this isolated slice is good.

## User-approved principles
- Realistic geography and map appearance outrank adding more game mechanics.
- 4 zoom levels smooth with the same world geography; no artificial multi-route road spaghetti.
- Far: no towns/units. Medium: towns/dots only. Close: small formation art, counts, strength/power and morale.
- No fog leaks from zoom transitions. Enemy counts remain hidden without legitimate sight.
- Trees/rivers/mountains are strategic terrain: control movement, defense and choke points.
- Modern aerial observations must **not** be represented as historically verified terrain from 1780.

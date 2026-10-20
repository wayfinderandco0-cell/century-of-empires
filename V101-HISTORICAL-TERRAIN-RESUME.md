# Century of Empires — V101 generated historical-terrain checkpoint
Date: October 20, 2026
Prototype: `v101-historical-brenner.html`
GitHub Pages intended: https://wayfinderandco0-cell.github.io/century-of-empires/v101-historical-brenner.html
Main-branch publication commit: `4e2efa75c495d3754769df95c6f6b3e8f8005198`
V101 development branch: `terrain-v101-historical-detail`.

## Why the approach changed
User shared actual iPhone Safari screenshots of V100 showing **present-day highways, buildings, and year stamps** at closest zoom. This is incompatible with the 1780–1880 game. User approved constructing imagined period-appropriate local mountain, valley, woodland and path visuals anchored to actual regional geography, not needing exact historical appearance.

## Implemented
- V101 independently developed and published as separate new HTML file, never overwrote `v94.html` or `v100-brenner-slice.html`, preserving campaign save keys.
- Removes all official aerial/orthophoto sources from the close zoom. No modern roads, buildings or modern photographic image tiles are requested there.
- Painter draws new terrain pixel colors and individual tree symbols at runtime, built from measured V97 Copernicus elevation and rough ESA woodland proxy. Forest boundaries smoothed and density reduced; zoom 4 defaults to a broader illustrated region.
- Original compact vector cavalry and artillery silhouettes replace two distracting dark square photographic artwork cutouts; existing infantry illustration reused.
- Keeps OSM mapped stream lines (geographical guides, **not** verified historical courses) and a SINGLE gently curved, illustrative Alpine pass trail. Do not claim precise 1780 road.
- Four zoom levels preserved: no labels/armies far, medium towns/army color dots, mountain relief with troop counts/status and handcrafted period-detail zoom with visible forces where scouted.
- Player can tap a mapped mountain to select geographic focus for the closest zoom (within current Brenner prototype bounds). Panning remembers that location, rather than automatically snapping back to the army.
- Fog of war, troop counts, morale and strength, limited scouting/ally share, march/pause/reset and meeting encounter preserved.

## QA
- Browser script: `scripts/qa_v101_mobile.py`, workflow: `.github/workflows/qa-v101-mobile.yml`.
- iPhone 390×844 Chromium QA on the final V101 HTML passed all browser and gameplay checks, including zero JS errors, no modern aerial imagery, painted forest, vectors, hidden enemy, controls, and eventual contact (workflow run `39458363272`).
- The workflow's **separate optional push of QA screenshots/report failed** because two concurrent runs wrote the same JSON and conflicted during git rebase. Do not call that full workflow successful. Browser QA itself succeeded; logs and Actions-uploaded artifact prove the result.
- Earlier screenshots on branch correspond to interim V101 forest-density iteration, NOT guaranteed final screenshot. Final physical iPhone Safari testing unverified.
- GitHub Pages deployment state must be checked separately.

## Future work
1. Test live V101 on user's actual iPhone. Inspect realism carefully. Current hand-drawn trees and coarse DEM are conceptual art; user may prefer a more polished 2.5D shaded terrain system.
2. Preserve selected world coordinate across all 4 map zoom tiers and add smooth pinch/rotate gestures to genuine production code.
3. Authenticate movement/chokepoint corridor against historical trade-road sources; avoid thousands of tactical alternate routes.
4. Use period-appropriate generated hill shading/rock exposure, riverbanks, tree clusters and historically plausible villages and footpaths; do not turn generated sprites into unrealistic repeating grids.
5. Apply new terrain engine across Europe, then connect to V94 campaign combat, province AI, artillery climb/forest cover, rivers/crossings; keep saves safe.
6. Fix workflow QA screenshot conflict via concurrency or unique artifact paths before reusing multiple parallel runs.

User has not yet approved the V101 visual result.

# Century of Empires — V114 map continuation checkpoint

Date: October 20/21, 2026. The last user upload includes eight iPhone Safari/screenshots around 11:22 PM. This is an isolated map demonstration, not a replacement for V94 or campaign saves.

## Observed failures in V113
- Town view can expose a large uniform blurred/green lower band. Illustration is 1100x842 landscape, while iPhone viewport is tall. Earlier code used a camera span that didn't always keep the image covering the camera.
- Thin fake diagonal road drawn at/beyond bridge is not a plausible continuation on the same side of river. The illustration lacks a complete, clean visible road past the existing stone bridge.
- In the close-up there are still potential off-road markers and a truncated art/tile boundary; cosmetic paint does not solve a missing geographic road.

## V114 delivered
- New standalone v114-town-camera-bridge-safety.html, preserves V109 core illustration, northern path, zoom and older files.
- Uses a coverage-adjusted camera scale that guarantees village art covers the close-up portrait view at span <=0.68 and clamps camera x/y using the actual *rendered visible span*, not requested span.
- Removed invented road stroke past the stone bridge. Demo bridge branch ends at real visible far bank, x704 y824. This is deliberately NOT a completed road connection to the next geographic area.
- South road still continues off bottom artwork. Original Europe/Region/Pass overlays retained. Army route selection, moving and halt remain.
- Verified GitHub readback, Javascript syntax and mocked DOM state; town coverage is 1.111× screen in height at 390x844, cameraInArt true, route selected, moving and halt work. Chromium/WebKit script and workflow added, but a passing run is NOT confirmed.
- User's actual iPhone visual confirmation remains pending; do not claim final perfection.

## Do not repeat previous flawed approach
- Do NOT keep drawing long synthetic lines across grass or rivers. V109's road partly worked, but continuing off the tile must be a single designed/geo-aligned terrain artwork and path network.
- Rebuild art + route together. Before promising true seamless 1780-era Europe, new neighboring illustrated tile must be spatially consistent; historical geography and visual perspective must be honestly labelled.
- Do NOT substitute generated art for working, editable path data.
- The main game MUST keep army commands, independent 4-way splits/merge, halt, entrench, redirect, retreat, morale, strength, unit counts and terrain-based combat across every zoom. These are NOT implemented into V114.

## Next
1. User tests V114 Town, pans to bridge, sees whether image blank-band bug is fixed.
2. Design one source of truth for georeferenced bridge/road centerline and paint the matching road *into* extended art. Until then stop demo route on far bank.
3. Integrate verified route and map LOD into actual V94 army engine, rather than coding separate fake army displays.

Test link: https://wayfinderandco0-cell.github.io/century-of-empires/v114-town-camera-bridge-safety.html

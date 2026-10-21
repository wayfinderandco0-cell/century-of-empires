# Century of Empires — V118 bridge-to-east map checkpoint
Date: 2026-10-21
Development: terrain-v117-road-art-contract
Production: main is preserved. V118 prototype can be separately published on main.

## Why this exists
The previous road graph stopped at [699,799] on the painted far bank and no route or artwork continued. Attempts to move troops along a separately authored path repeatedly sent the sprite off the image.

## V118 changes
- scripts/v118_east_connector.js extends the existing candidate bridge graph with a narrow, artist-authored cart road that bends through the right-bank meadow, approaches the already painted Waldraster Bach crossing, then reaches source-art east boundary [1100,704].
- The one-octagon east exit has a deterministic next-section entry handshake [0,704]. This does **not** imply a finished neighboring art cell.
- The same graph generates the painted cart track and army positions. There are no independent extra "artist road" waypoints for infantry.
- Painter uses muted, thin earth/cobble coloring and visible wagon ruts instead of an opaque, asphalt-like road ribbon.
- V118 HTML keeps embedded original 1100x842 V115 artwork, shows both branches, includes Fork start/March/Bridge, an East exit view under Options, and follows marching infantry until manual drag.
- The isolated preview does not replace V94's geographic source, the default index.html gameplay, the existing saves or protected systems.
- Dedicated Node + Chromium + WebKit phone-size portrait/landscape QA: .github/workflows/qa-v118-east-exit.yml, tests/test_v118_east_connector.js, scripts/qa_v118_east_exit_browser.py.
- V116 48 children are still *visual source crops*; they are not traversable/conquerable cells. The 432 Europe cells remain an index, not completed game octagons.

## Evidence and acceptance
- Pure geometry sync and boundary handshake are testable automatically.
- Source image route judgment is visual; the exit is an artistic authoring candidate, **not a verified historical path**.
- Physical iPhone Safari approval and complete four-level game integration are still required before one octagon is accepted as done.
- Still missing: credible continuation beyond the first cell into actual neighboring artwork; gameplay commands/terrain effects integrated with production.

## How to review on an iPhone
Open standalone v118-connected-bridge-exit.html via GitHub Pages after the pages deployment succeeds. Tap Fork start, then March. The army will continue past the large stone bridge, along the east-bank cart road, across the small stream crossing, and stop at the eastern artwork boundary. To inspect the exit, open Options → East exit. Drag to pan. Do not treat passing tests alone as artistic approval.

## Next gate
Examine screenshots of the latest V118 mobile QA run. Correct any visual mismatch or superimposed road. Then obtain a physical iPhone screenshot; don't claim production-ready or extend the map before genuine visual acceptance.

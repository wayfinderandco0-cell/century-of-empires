# Century of Empires — resume geographic map replacement

Updated 2026-11-10. The user's **new decision supersedes all previous octagon approvals and drafts**: abandon octagon photo art and seam fixes entirely. Do not revive PR #26 or V267 road graphics. No game-mechanics rewrite.

## Safe status

- New map development branch: map-geographic-redesign-matrei-20261110.
- Production game index.html, historical campaign pages, economy, combat, saves, sprites and existing map files are unchanged.
- Standalone new-geography source is inside geo-redesign/. This is not integrated with the saved game.
- For independent HTTPS playtesting only, **copies** of the demonstrator's index.html, road-graph.js and corridor-data.js were added to main under geo-preview/. This neither replaces nor imports into the production homepage, and is not merging the redesign branch.
- Public link TARGET: https://wayfinderandco0-cell.github.io/century-of-empires/geo-preview/index.html
- As of this note, publishing verification of that URL is STILL PENDING; do not say it is playable unless a hosted browser QA run passes.
- Maps are OpenFreeMap modern OSM-derived geography, with transportation/modern-label layers hidden; Mapterhorn DEM overlay; MapLibre GL JS camera.
- Registered Alpine Wipptal cartway vertices are only rough **PROVISIONAL** data along historically documented valley corridor. NOT a period-accurate road trace, and may cut across unsuitable slopes. A 1780-1880 cartway must be surveyed against historical sources.

## Code milestones

- geo-redesign/index.html: georeferenced MapLibre map, DEM hillshade, pan and pinch, settlement labels, selectable marker, tap-road / town destinations, Execute, Halt, Reset, road-following animated demo march.
- geo-redesign/corridor-data.js: WGS84 settlement locations, one provisional cartway geometry (25 segments/26 nodes).
- geo-redesign/road-graph.js: graph of the actual shown polyline with nearest segment, route interpolation, mid-road routing and connectivity checks.
- geo-redesign/test-road-graph.cjs: Node geometrical assertions; 9.89 km test route Matrei to Gries.
- geo-redesign/browser_qa.py: real headless Chromium & WebKit at 390x844 mobile emulation; snapshots at regional and close zoom, marching and pan.
- .github/workflows/qa-geographic-redesign.yml: runs Node and browsers, then tries **external hosted URL**.
- geo-redesign/README.md: data provenance, tech rationale, independent game preservation contract, acceptance gates.

## Testing evidence and failures

- GitHub Actions 42890842879: SUCCESS (Node and Chromium/WebKit local http QA, actual browser screenshots, camera zoom, pan, test-unit route march).
- GitHub Actions 42891018241: SUCCESS local browsers/graph.
- GitHub Actions 42891054938: failed only HTTPS raw.githack branch hosting check; its HTML confirmation/interstitial or hosting prevented page QA. It does **NOT** invalidate local browser pass.
- GitHub Pages publication from main commit b3e9ddaf11454187ec0424c8a202b6c80918d458 in progress via Actions 42891898927.
- Hosted interactive browser QA from branch commit 5b1d9c1aaf792047b25057952d52a5ae285be3fc in progress at Actions 42891922313.
- GitHub Action artifacts (regional/close/march/pan for both browsers) from 42890842879: https://github.com/wayfinderandco0-cell/century-of-empires/actions/runs/42890842879/artifacts/13798003286 .
- WebKit here is a simulation, not actual iPhone Safari device. Simulated pinch currently needs additional explicit gesture test.

## Next actions in this exact sequence

1. Check pages build and deployment run 42891898927; ensure success.
2. Check branch QA run 42891922313; hosted URL truly loads and unit test march succeeds, or diagnose its logs. Only then give user the verified live review link.
3. Exercise explicit multi-touch pinch on Chromium and phone Safari if available; capture screenshots and inspect visually.
4. Historical research: obtain and date archival Tirol/Brenner road maps around selected campaign year, georeference proper cartways, bridges and crossing points, reject impossible slopes; attribute every route segment.
5. Adapt production campaign road order handler and save/province IDs to geographic movement while preserving existing game code, player commands, unit sprites, army speeds and war mechanics; keep branch isolated.
6. Review with user and do not merge without approval. No expansion across Europe before a successful integrated Matrei corridor.

For automated continuation, do not confuse the demonstrator's fast QA animation with the game's campaign clock, and do not claim period accuracy or full-game integration.

Never return to octagons. The independently deployed preview is a safe demonstration, not an acceptance or merge.

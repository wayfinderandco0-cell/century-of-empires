# Century of Empires — V102 Brenner visual pilot

Session: October 20, 2026. Status: **implementation in progress**.

## Branch and preservation
- Work only on `terrain-v102-visual-pilot`.
- Based on `terrain-v101-historical-detail` at `d0733db3d05fb65e3bb08651c4da47a1eac5b1e0`.
- V94, V100, V101, all prior terrain assets, main, and campaign save keys must remain untouched.
- Requested output: `v102-brenner-visual-pilot.html`, assets under `terrain-v102/`, actual portrait/landscape screenshots.

## Inspection completed
- Read `V101-HISTORICAL-TERRAIN-RESUME.md`, V101 renderer, V97 builder and manifests.
- V101 paints at 70% CSS resolution and uses repeated triangular trees; it is not a suitable close-view foundation.
- Reuse `terrain-v97/brenner-data.json` (260×300 elevation + woodland proxy), `terrain-v97/brenner-relief.webp` (1552×1782), and `terrain-v99/brenner-streams.json`.
- Important accuracy limit: the numeric V97 grid was reduced from Copernicus GLO-30. Its retained samples are roughly 160×230 m apart, NOT native 30 m detail. Smoothing or material detail cannot add measured geography.
- OSM waterways are modern mapped geographic guides. Forests/path reconstruction must be explicitly illustrative.

## Rendering direction
Use geographic elevation for a continuous shaded mesh, coherent muted materials and irregular forest canopy, with shared geographic coordinates for water and an illustrative path. Focus on one Brenner corridor scene, not Europe. Keep expensive material preparation off the runtime render path. Preserve space for continuous scale transitions.

## Next action
Inspect waterways coverage; implement and checkpoint the renderer. Then render at 390×844 and 844×390, inspect the images, correct visual problems, and save screenshots and a machine-readable QA report. No visual approval yet; no runtime tests yet. Do not claim commercial quality without inspecting actual output.

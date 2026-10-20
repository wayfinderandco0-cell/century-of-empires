# Century of Empires — V103 visual correction checkpoint

Created: October 20, 2026. Graphics-only prototype; no gameplay or saves altered.

## Goal
Respond to real iPhone V102 screenshots: dot-like forests at medium and close zoom, circular bush-like trees, excessively broad bright trails, visible river occlusion/gaps, and iOS Safari accidentally zooming the *entire page*.

## Source and isolation
- Branch `terrain-v103-visual-repair` builds on production main after additive V102 publication.
- Preview: `v103-brenner-visual-pilot.html`.
- V103 new renderer/CSS in `terrain-v103/`, **reuses existing immutable V102 geographic data and assets**. Do not rewrite V102.
- Campaign saves, V94, V100, V101, V102 remain untouched.

## Changes
- Conifer sprites become tiered tapered crowns instead of circular top-down bushes. Individual tree detail only fades into view at close scales; wider scales show baked forest rather than dot scatter.
- Stream and pack-trail overlays are lifted against the *actually drawn triangular WebGL ground mesh* with 12m sampling and polygon depth bias, reducing hidden/interrupted segments.
- Dirt trail narrowed/desaturated; river widths less exaggerated.
- Prevent native iOS Safari page magnification when gesturing over the map, and handle double tap as camera zoom. Preserve buttons and source dialog.
- Mobile automation runs Chromium and WebKit (iPhone-size portrait and landscape); stores QA reports and image previews on this branch. Physical iPhone visual approval is required.

## Limitations and next step
The V97 retained Copernicus grid is ~160–230m resolution, not 30m. Forests and pack trail are illustrations based on modern proxies, not a verified historical survey. V103 still covers the Navis valley (northern Brenner region), not entire Europe. Inspect actual iPhone screenshots closely: shape of crowns, water continuity, pinching without enlarging UI, nav readability, and rendering speed. Keep visuals separate from game physics until approved.

# V243 — immutable-route-conditioned original Alpine art briefs (ART/PRODUCTION RED)

## Why this branch exists

V242's actual four-configuration Chromium/WebKit screenshot artifact (run 40530879300, artifact 12748747360) was downloaded and visually inspected. The imported WEST/SOUTH photographs are finally visible; Matrei stays unchanged. However, their roads are flat brown strips cutting across forest and their landscape/camera do not match Matrei. V203 SOUTH necessary fine-structure test still FAILS in all four configurations: WebKit portrait fine-luma 0.6481 and fine-area 0.6765 relative to Matrei; WebKit landscape 0.5328 and 0.4880. The screenshot is *not* user-accepted artwork. V242 technical image-import/Matrei/army tests pass all four configurations; that is not an art pass.

V238/V241 attempts to paint dirt stripes onto arbitrary licensed photos are also rejected. V209 independent natural tiepoints remain unverified. Instead of retexturing the same incorrect route, this branch creates **native-resolution spatial conditioning briefs for both cells before any new landscape is composed**.

## Actual change

`python scripts/v243_road_conditioning.py --atlas terrain-grid/v123-atlas.js --out qa/v243-road-conditioning` reads the exact unchanged, Git-blob-pinned V123 road definitions (SHA1 `09f04b4062e24fbacbb645307462cdddce2b2aa3`). It writes 1536×1024 original, deterministic guide images and masks for both WEST and SOUTH:

- `<tile>-composition-guide.png`: full octagon, exact portal/road end points, unblocked corridor and centerline.
- `<tile>-keep-clear-48px.png`: 48px clearance mask; no trees, buildings, cliffs, water or steep slopes should occupy this region in newly composed art.
- `<tile>-roadbed-13px.png`: 13px physical roadbed reference; an artist must create natural embedded ruts, shoulders and correct terrain contact around it.
- `manifest.json`: source Git blob, route points and explicit false approval gates.

WEST must meet Matrei at east portal **(1536,478)** and stops at west survey limit **(275,550)**. SOUTH begins at north portal **(466,0)** and stops at south survey limit **(1270,605)**. These are *game-local* coordinates, **not verified historic geography**. A survey limit is not a confirmed onward road. There is no new bridge or bank claim.

## Review and remaining blockers

This is an **art-production input**, not finished artwork or playable terrain. It is deliberately plain and should never be imported as the WEST/SOUTH visual assets. Next create **two original photo-grade, distinct Alpine landscapes around these exact routes** (or independently source/attribute genuine registered imagery), with natural terrain microstructure comparable to Matrei and no cloned villages/trees/rocks. Independently trace visible cartways from the final images and compare with the V240 alignment gate. Check octagon seams, physical bridge approaches, terrain clearance, source/license evidence, V203 strict 0.70 thresholds, all four mobile configurations, then human iPhone screenshot review. Never infer source/game natural tiepoints from modern orthophotos, change V123 to fit an image, or mark a CI technical pass as visual approval.

No existing game, sprite, campaign, saves, road graph, bridge graph or production files are modified. Production remains RED until explicit user acceptance.

# V267 — actual-art WEST cartway registration and iPhone join inspection (2026-10-28)

**UNAPPROVED. Production remains RED.** The WEST/SOUTH source images are original *fictional game art*, not verified 1780 road/geographic data. The existing V121 Matrei source, V122/V123 modules, campaign V94, army options and saves remain unchanged. This is an isolated offline prototype.

## Eyes-on defect and actual visual change

Inspected the genuine 390×844 Chromium V267 WEST and SOUTH seam screenshots **with and without** the immutable V123 yellow route overlay. At the WEST/MATREI boundary, the Matrei photographed cartway was visibly lower than the route and WEST's physical cartway because the earlier preview reprojected the V121 octagon frame globally. SOUTH's road was already continuous enough to preserve in this iteration.

The updated render-copy registration adds a **localized source-image resampling displacement** along Matrei's WEST approach: `26 * exp(-.5*((x-240)/400)^2) * exp(-.5*((y-505)/110)^2)` source pixels. The original V121 image bytes, both neighboring art source images, and all V123 road points remain unchanged. It corrects the physical cartway's location under the fixed route in the visible WEST seam close-up, without painting a synthetic road. This is a targeted art-to-route registration, **not** historic/geographic verification or a claim of perfect pixel alignment. The SOUTH scene is visually unchanged aside from small falloff of the localized Matrei correction.

## Practical iPhone review and interaction

- Added **WEST join** and **SOUTH join** controls to zoom directly to both existing 0px-gap V123 boundaries, avoiding repeated manual pinch/pan.
- Touch marching now snaps to the closest **existing V123 road segment** rather than only a node, rejecting touches more than 72 map pixels from the route. It does not add/change any graph edge.
- Preserved the original embedded Matrei WebP, original WEST/SOUTH images, the canonical V122/V123 routing implementation, 100 tile-specific nodes / 98 unique world positions, the two seam endpoints, halt and movement.
- Candidate: [one-file offline iPhone review](../v267-three-octagon-original-art-prototype.html).
- [Actual-art Chromium/WebKit screenshot workflow and downloadable screenshots](https://github.com/wayfinderandco0-cell/century-of-empires/actions/runs/40745579967). These are **real rendered WEST/MATREI/SOUTH artwork**, not synthetic test imagery.

## Test status

Locally ran the exact embedded images in real Chromium at **390×844, 844×390, 375×667, 667×375**, touch/DPR2. All four loaded the original Matrei offline, returned 100 nodes / 98 unique positions, both V123 seam checks passed with 0px graph gap, WEST→MATREI→SOUTH traversal used 53 tile-specific path nodes and reached (2806,1629), and no JS page errors occurred. Actual touch-to-march and halt also passed in 390×844 and 844×390. See the Actions workflow for exact-art WebKit results; do not infer them from Chromium.

## Unresolved

Human review and physical iPhone Safari acceptance are **not done**. SOUTH's terrain deformation, the remaining Matrei-to-SOUTH transition, bridge banks, all cartway sections at all zoom levels, and strict V203 production-quality acceptance remain unapproved. The artwork is not historically georegistered. Do not merge/promote until explicit user visual approval and final regressions.

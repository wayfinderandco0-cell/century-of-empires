# V175 — real masked geographic source L on four iPhone-layout browsers

**Date:** 2026-10-24 (America/Chicago). **Isolated branch:** `terrain-v175-masked-source-phone-review-20261024`, based on V174 `010a59a9`. This is a geographically registered **modern SOURCE inspection viewer**, **not** finished 1780–1880 game artwork or V123 game-road registration.

## Why

Inspected the actual V171 WebKit portrait/landscape West, Matrei, South and whole-crossing screenshot artifact 12578863866. The old GAME view still shows one detailed Matrei painting and comparatively synthetic West/South surfaces with survey-limit road termini. The unchanged strict V171 game-art acceptance remains **0/4**.

Inspected the real V173 1536×1024 masked geographic-source image (artifact 12581709214): retained woodland/field imagery has photographic detail, but numerous modern asphalt/roofs/date labels are excluded as transparent holes and the southwest 768×512 quadrant is wholly unknown. These holes cannot be filled with invented trees, houses or roads.

## Actual implementation

- `v175-masked-source-review.html` displays the original V169/V173 muted material-study RGBA image **without filling unknown/modern alpha holes**. Unknown pixels show a contrasting, world-locked checkerboard, not counterfeit terrain. Source West, Center and South retain original 768×512 pixel footprints and a single shared source coordinate frame.
- Viewer checks SHA-256 of the actual source study and mask, validates the V169 source provenance and its agreement with the V174 exact 1536-block LOD manifest, and rejects forged historical/road/production approval.
- Four zoom tiers, sector focus, pointer pan, pinch and anchored zoom support iPhone-layout inspection. No fake road, bridge, capture point or V123 transform is drawn.
- `scripts/qa_v175_masked_source_phone.py` verifies exact RGBA/mask alpha identity, known modern and unknown pixel transparency, retained source pixels, center coordinates, four zoom-tier anchor invariance and forged-approval rejection in Chromium/WebKit portrait/landscape. It saves whole-L and three distinct source-sector PNGs per configuration.

## Verified test evidence

Initial CI run 40158095922 failed because the Playwright Python container did not include `node`. Fixed CI environment with `actions/setup-node@v4`; this did **not** change map/game data.

**Final [GitHub Actions run 40158163038](https://github.com/wayfinderandco0-cell/century-of-empires/actions/runs/40158163038) SUCCESS:** original V121/V123 immutable identity guard passed, V168/V169/V174 Python regression tests passed, all 18 original geographic JPEGs acquired and verified, modern exclusions and LOD regenerated/verified, **4/4 simulated iPhone Chromium/WebKit configurations passed**. [Actual screenshot artifact 12585208358](https://github.com/wayfinderandco0-cell/century-of-empires/actions/runs/40158163038/artifacts/12585208358) downloaded and visually opened: 12 independent West/Center/South source views and four whole-L images. Photographic woodland/meadow detail is present in each acquired source sector, but excluded asphalt/roofs and unacquired southwest are conspicuous checkerboard gaps. This is intentional and **not acceptable final game art**.

## Unfinished / next

These geographic sectors are **not** Matrei/Western Pass/Southern Valley GAME octagons. No geological landmark tie points establish a V121/V123↔modern-source transform; modern fields are not historical proof; the bridge banks and external road continuations are unsurveyed. **No V171 strict game-art acceptance was rerun or passed on this source-only viewer.** No physical iPhone or user visual approval.

**Next:** Create a separate source-first, authored period-interpreted candidate only where geographic/natural-feature evidence is supportable; retain unknown gaps visibly and prohibit any road/bridge/settlement fabrication. Obtain independently reviewed geological controls or explicitly retire the fictitious V121-to-modern registration attempt. Then run the original strict four-browser GAME-art/seam/route tests and get real iPhone approval before any merge/deploy.

`productionApproved=false`; `periodArtComplete=false`; `v123RoadsGeoregistered=false`; `physicalIPhoneApproved=false`. Main, V94 campaign/saves, V121 painting and V123 roads/bridge untouched.

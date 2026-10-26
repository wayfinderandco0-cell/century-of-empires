# V224 — independent licensed oblique source art, NOT approved

**Status: isolated interactive artwork experiment; technical and human approval independent; production RED.**

## Actual change

Two complete **1536×1024** WEST and SOUTH scene images are derived from **two different** 3072-pixel-wide Wikimedia Commons thumbnail JPEGs at native pixel scale, with recorded exact crop boxes and reproducible 0.84 saturation/brightness grading. This is a materially different art input from V222's Matrei motif quilt and V220's top-down modern orthophoto. The original Matrei source remains a **single unchanged** 1536×1024 painting. V123 movement, road control points, crossing graph, army sprites, V94 campaign and saves are not changed.

The separate opt-in `v224-licensed-oblique-west-south-review.html` paints both new images underneath the **unchanged** V123 navigable roadbed overlay. Its original-art toggle allows a direct comparison. There is no new path or invented bridge. The `V224LicensedObliqueNeighbors` loader refuses to show unverified art as approved. Existing blocked road ends remain blocked.

## Source provenance and license

- WEST: **SUHEJLO**, [Drone image of Sharr Mountains during Spring Season](https://commons.wikimedia.org/wiki/File:Drone_image_of_Sharr_Mountains_during_Spring_Season.jpg), May 2023, **CC BY 4.0**.
- SOUTH: **SUHEJLO**, [Aerial photo of Sharr Mountains in Kosovo](https://commons.wikimedia.org/wiki/File:Aerial_photo_of_Sharr_Mountains_in_Kosovo.jpg), May 2023, **CC BY 4.0**.
- License: https://creativecommons.org/licenses/by/4.0/ . Cropped and color-graded for this isolated study; attribution retained. Pinned **3072px Wikimedia thumbnails re-encoded as JPEG quality 62** for repository storage, not original full-resolution camera JPEGs and not exact original Commons thumbnail bytes; `sourceSha256` covers the exact checked-in derivative JPEGs. Exact crop, source/output SHA-256, output data URI parity and negative-control tests are in the manifest and Python QA.

**Important:** These photos depict the **Sharr Mountains in Kosovo, not the Austrian Alps**. They are illustrative natural-cover material only. They do **not** establish Matrei geography, historical 1780 roads, forest species, bridge banks, or correct perspective. The SOUTH crop still visibly includes a modern road near the right edge, so **human period-safe artwork acceptance is already RED**. WEST and SOUTH also differ in vegetation and camera scale from the original Matrei painting. This is an honest negative-control art alternative, not a production-ready solution.

## Testing and non-negotiable blockers

- Offline `scripts/v224_licensed_oblique_cells.py --verify` checks protected V121/V123 hashes, exact source SHA-256, native crops, output/embedded pixels, attribution, and all false approval flags. `scripts/test_v224_licensed_oblique_cells.py` verifies deliberate tampering fails closed.
- `scripts/qa_v224_licensed_oblique_game_art.py` exercises real Chromium/WebKit portrait/landscape screenshots, graph routing, army movement, original center pixel equality and source toggle. Inherited V137/V202 tests and unchanged V203 microstructure thresholds remain mandatory.
- The independent human-art job stays RED even if V203 numeric detail passes. A real screenshot must be inspected; no numeric test can approve modern roads or mismatched perspective.
- V209 independent natural tiepoints are still absent. Road endpoints, bridge banks, cross-cell seams, all V100 zoom tiers and user visual acceptance remain unverified. **Do not merge, deploy, or label approved.**

`sourceRegisteredToV123=false; historicRoadsVerified=false; periodSafe=false; bridgeBanksVerified=false; gameArtApproved=false; physicalIPhoneApproved=false; productionApproved=false`.

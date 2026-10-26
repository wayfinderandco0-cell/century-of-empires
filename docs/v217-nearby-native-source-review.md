# V217 — nine native modern Matrei-area source candidates (NOT game art)

Date: 2026-10-26. Isolated branch `terrain-v217-matrei-nearby-native-scout-20261026`, based on V216. No change to main, original V121 painting, V123 road/army graph, V94 campaign/saves, production renderer or V100 zoom states.

## What was actually coded

`scripts/v217_matrei_nearby_native_scout.py` selects nine **separate** 512×512 source panels in a 3×3 grid of *candidate locations* around the independently identified modern Matrei-area reference (11.45306°E, 47.13083°N). Each panel comprises four original 256×256 basemap.at zoom-18 EPSG:3857 aerial JPEGs, for **36 unique native JPEGs**. Offsets are -8, 0 and +8 native XYZ tiles on each axis; **gaps between panels are unsampled**, not stitched or inpainted. The exact source XYZ/footprints, JPEG SHA-256, decoded RGB, original panel dimensions, source attribution and nonapproval flags are pinned and reverified.

`scripts/test_v217_matrei_nearby_native_scout.py` rejects changed tile origins/URLs, false geographic or historical claims, changed native JPEG bytes, changed contact pixels and source identity swaps. CI preserves inherited V204–V216 source tests and independently runs the unchanged original four-mobile-browser road/bridge/army/camera and strict V203 game-art tests. The native image artifact is **reference only**; there is no new playable art, invented path or false georegistration.

## Real visual review — actual source artifact

The 1600×1935 native contact was downloaded and opened, not inferred from the manifest. The nine panels have **visible geographic gaps** and are not a three-octagon game atlas.

- Site 00: farm fields and modern buildings. Site 01: modern hairpin paved road and houses. Site 02: genuine dense conifers but buildings, a clearing and visible 2023 imprints.
- Site 03: forest/meadow boundary with irregular real canopy, fewer obvious buildings; visible 2023 imprint. Site 04: dense town streets, roofs and recreation facilities, unsuitable. Site 05: dense natural conifer texture with modern clearings and 2023 imprint.
- Site 06: forest/meadow texture, a large cleared strip and 2023 imprint. Site 07: modern rail/river corridor and industrial facilities, unsuitable. Site 08: dense conifer canopy, a track near the lower edge and 2023 imprint.

**Candidates for later exclusion-masked MATERIAL research only:** 03, 05, 06 and 08. This is a visual shortlist, **not** a verified historical landscape, surveyed game footprint, safe-for-use photo, or geographic tiepoint. All candidate panels are substantially closer to the modern Matrei reference than V205's forest source ~3.578 km away, but **distance alone cannot register the V121 painting to any real source**. Their precise source coordinates are in the verified manifest.

## Acceptance status

The original V192 WebKit portrait WEST/SOUTH screenshot still shows artificial canopy and flat scenery beside the high-detail Matrei painting. New native source pixels have **not** been placed in the game. The V209 independent-landmark report remains `BLOCKED_MISSING_REAL_TIEPOINTS` for all three game cells.

`registeredToV121=false; registeredToV123=false; historicalRoadsVerified=false; modernFeaturesExcluded=false; periodSafe=false; gameArtApproved=false; physicalIPhoneApproved=false; productionApproved=false`.

Next: conservative **visible 2023/modern-track exclusion masks** on the reviewed candidate source panels, with unmasked RGB left bit-identical. Do not infer exact 1780 terrain, invent road continuations, or replace Matrei. A separate opt-in art trial must preserve V121/V123 and pass actual four-browser road and strict image tests before user visual approval.

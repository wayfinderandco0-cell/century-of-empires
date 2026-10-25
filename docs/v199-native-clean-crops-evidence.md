# V199 — original-pixel Alpine source-reference crops (25 October 2026)

**Status: authentic modern SOURCE REFERENCES ONLY. The three WEST/MATREI/SOUTH playable octagons remain unapproved.**

## Reviewed before editing
- GitHub issue #9 through V198; V198 final source CI [40240240317](https://github.com/wayfinderandco0-cell/century-of-empires/actions/runs/40240240317) and artifact 12616931804; V196 game CI [40230561361](https://github.com/wayfinderandco0-cell/century-of-empires/actions/runs/40230561361) and its **actual** WebKit portrait WEST/MATREI/SOUTH screenshots. Western Pass and Southern Valley remain visibly synthetic, with artificial trees and regular road strokes; Matrei is a detailed photo with a visible seam. Existing west/south route endpoints are not surveyed.
- V197 full source artifact 12614990453: 12 real native 256px JPEGs, three 512px source-reference images, original metadata and attribution. V198 final transparent exclusion artifact 12616931804: original source pixels preserved outside annotated year stamps and suspected tracks. Both actual contact images inspected.
- Geographic distinction: the three V197/V198 sources are **not** the game octagon centers and are modern orthophotos, not historical evidence.

## V199 code and verification
- `scripts/v199_clean_native_crops.py` extracts **nine nonoverlapping 160×160 pixel reference crops** (three per source), using the actual original RGB pixels only, with **12 native-pixel clearance** from every V198 annotated exclusion. No inpainting, color replacement, resampling, roads or tree generation.
- Every crop records its exact native zoom-18 XYZ source origin, integer source rectangle and computed EPSG:3857 lon/lat footprint. Crop SHA and original decoded RGB byte SHA, V197/V198 parent manifest hashes, masks, transparent-source integrity, license and required attribution are independently checked.
- A fail-closed 10-test synthetic suite rejects altered source images, alpha, masks (even with updated SHA), forged geographic bounds, forged approval, overlapping crops and corrupt pixels. CI reruns V197/V198 inherited tests, downloads and verifies the original JPEGs, and regenerates the actual nine-crop artifact.
- All source and game approval flags remain false. **Zero quarantined pixels in selected crops does NOT mean that all modern infrastructure was detected or that these are 1780-period-safe images.** They are genuine high-detail *visual references*, not world-registered game terrain.

## Local real-source check before branch publication
- Downloaded both original V197 and V198 workflow artifacts, extracted original JPEG/PNG/manifest files, and ran V199 producer, independent verifier and 10 synthetic tests successfully on actual sources.
- Opened the actual 480×564 nine-crop contact sheet: real conifer crowns, variable canopy density and Alpine meadow/ridge textures, without the specifically quarantined date stamps/tracks in these nine areas. No invented geometry.

## Still blocking three-octagon acceptance
1. Survey/register the actual V123 WEST/MATREI/SOUTH game world against geographic source control points; **do not paste these unrelated patches onto game coordinates**.
2. Obtain period-appropriate treatment for modern infrastructure and transparent exclusions; these clean samples alone are not historical reconstruction.
3. Preserve original V121 Matrei photo and immutable V123 route/crossing controls until independent evidence supports change.
4. Build a geographically aligned isolated game art trial, keep strict four-browser movement, route, seam and detail QA, inspect actual iPhone WebKit screenshots and obtain user visual approval before any production merge.

`gameArtApproved=false; gameWorldRegistrationKnown=false; historicalRoadsVerified=false; bridgeBanksVerified=false; physicalIPhoneApproved=false; productionApproved=false`.

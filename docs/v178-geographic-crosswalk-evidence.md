# V178 — exact V168 SOURCE geographic crosswalk (2026-10-25)

**Status: source-coordinate engineering only. THREE GAME octagons remain visually REJECTED.**

Branch: `terrain-v178-geographic-crosswalk-20261025`, based on V177. No production/main/V94 save/V121 painted Matrei/V123 route changes.

## Evidence inspected

- Issue #9 through V177 and actual V177 WebKit portrait and landscape screenshot artifact 12587932541. The authentic geographic SOURCE L has large masked contemporary roads/roofs and an entirely unknown southwest quadrant; the modern-source tonal treatment is not playable historical art.
- V171 actual WebKit/Chromium game screenshots and strict QA remain 0/4 for GAME visual acceptance: Matrei detailed island, West/South synthetic, outer road termini unsurveyed.
- Retained V94 equirectangular 1448×1086 game/8192×6144 atlas manifest; V97 Copernicus DEM relief 1552×1782 with broad bounds [11.26,46.80,11.80,47.42]; V102 257×257 narrow Navis grid with [11.43,47.075,11.625,47.19]; V168 source L uses native XYZ Web Mercator tiles at z17.

## Implemented

`terrain-grid/v178-source-geographic-crosswalk.js` derives V168 XYZ origin [69726,46030,17] from the actual 11.520 E,47.130 N source center, then performs exact inverse/forward Web Mercator source-pixel mapping. It projects only observed SOURCE L pixels into V97 relief raster-edge coordinates, V102 **257-point grid indices 0..256**, and V94 game/atlas raster-edge coordinates. No invented V121 GAME tie points or historical road paths. Unacquired southwest source pixels fail closed. Source seam positions use one coordinate system. `scripts/test_v178_geographic_crosswalk.js` exercises positive/negative geography, tampered manifests, round trips, seam continuity and false approval. A dedicated GitHub workflow runs both V172 and V178 checks and uploads source-only coordinate evidence.

**Important scale finding:** The entire V168 geographic source L spans approximately 11.50818–11.52466 E and 47.12621–47.13369 N, only about **1.25 km east-west by 0.83 km north-south** at this latitude. Each acquired source sector spans roughly 0.62 km by 0.42 km. These are three *SOURCE* patches around the Navis geographic study, **not** geographically validated Matrei / Western Pass / Southern Valley GAME octagons, and cannot be stretched into those locations without inventing geography.

The V97 broad relief and V102 narrow Navis raster have **different** source frames; V167 already warned about that. V178 extends the review to exact V168 XYZ source pixels and the V94 atlas with explicit separate projections.

## Acceptance and next

All returned route/bridge/production/period/physical-iPhone approval flags remain false. Coordinate correspondence between *source rasters* is not evidence of a match to the illustrative V121 painted terrain or V123 route graph. V171 unchanged visual parity remains red. Do not fill masked modern features or unacquired source pixels with procedural scenery; do not fabricate bridge banks or roads.

**Next:** Stop trying to register the V121 painting without geological tie points. Use this exact geographic crosswalk to select a geographically large enough, independently sourced and period-interpreted three-cell GAME-frame footprint, then separately research road/bridge bank evidence and create truly continuous art. Preserve V121/V123 as unregistered prototype; do not merge/deploy until all four phone tests and user iPhone visual approval.

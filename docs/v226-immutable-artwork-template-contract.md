# V226 — exact V123 route-aware artwork authoring templates (NOT approved)

**Purpose:** V224/V225 playable art was visually rejected. The source photographs depict modern Kosovo; V225 road-contact bands looked like highways over forest canopy. This change does NOT add a cosmetic road layer or call either photo suitable for production. It provides a deterministic, source-graph-exact artwork clearance contract for two future distinct high-resolution WEST/SOUTH compositions.

## Source of truth and geometry
- Protected original V121 painted Matrei Git blob: 4c6aa5cda9e7c359b6d2a49d5b5fe8a597346382.
- Protected V123 road atlas Git blob: 09f04b4062e24fbacbb645307462cdddce2b2aa3.
- WEST 1536×1024 local coordinates: east road from (1536,478) at Matrei join to (275,550) at unverified outer end, 13 exact V123 control points.
- SOUTH 1536×1024 local coordinates: north road from (466,0) at Matrei join to (1270,605) at unverified outer end, 12 exact V123 control points.
- The template has a translucent 52px wide canopy-clearance warning, the existing 22px cartway reference, the original dashed centerline, and distinct join/unsurveyed terminus marks. The 52px warning is NOT a roadbed, traversable route, bridge bank, surveyed road, or permission to alter the graph.
- No invented roads, bridges, riverbanks, historical dates, conquest nodes or destinations. No change to Matrei image, V94 campaign, V100 unit options, saves or main.

## Implemented code
- terrain-grid/v226-artwork-contract.js: fail-closed exact graph-point contract, immutable deep-copied output and transparent SVG authoring guide.
- scripts/build_v226_artwork_templates.js: reproduces two 1536×1024 transparent SVG guides and JSON manifest with source identities, original points and explicit nonapproval flags. Outputs under terrain-v226/templates/ when executed; generated files are CI artifacts, not silently merged into production.
- scripts/test_v226_artwork_templates.js: negative tests for changed interior points, invented edges, endpoints, tile origins, invalid coordinates, approval flags, and generated SVG tampering.
- v226-cartway-artwork-workbench.html: opt-in interactive iPhone view of the unchanged rejected V225 photos with a toggle to display the exact clearance template. It is NOT improved playable art.
- scripts/qa_v226_artwork_templates.py: actual Chromium/WebKit × portrait/landscape capture, validates two guide overlays, original Matrei pixel parity, unchanged graph and movement.
- .github/workflows/qa-v226-artwork-templates.yml: inherited V137/V202, V225 baseline and unchanged strict V203 test. Strict art and human approval remain RED.

## Remaining critical blockers
1. Need two independently created/licensed Austrian-Alpine high-resolution compositions, with a realistic view matching Matrei and a visually clear cartway footprint along the immutable graph. Neither existing Kosovo image is acceptable. A route-aware guide cannot fabricate a road.
2. No independent V209 real natural tiepoints from game coordinates to source imagery. Geographic registration and historic 1780 road claims remain false.
3. Source-backed bridge approaches and meaningful outer destinations are unverified; keep original survey limits and no fictitious onward movement.
4. Full four V100 zoom levels, natural cell-edge transitions, human screenshots and physical iPhone user acceptance remain unapproved.

**Nonapproval state:** sourceRegisteredToV123=false, historicalRoadsVerified=false, bridgeBanksVerified=false, periodSafe=false, gameArtApproved=false, physicalIPhoneApproved=false, productionApproved=false.

This is a development authoring capability, NOT finished artwork or three completed octagons.

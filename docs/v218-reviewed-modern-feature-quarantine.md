# V218 — real modern-feature quarantine in four near-Matrei source candidates

Date: 2026-10-26. Isolated branch `terrain-v218-reviewed-modern-feature-quarantine-20261026` based on V217 `370190ef`. **Research-only. No new game art, no main changes, no new traversable roads, no historical registration.**

## Reviewed evidence before coding

Read issue #9 through V217, branch head and latest V217 CI jobs. V217's real 1600×1935 nine-site contact and the unchanged actual WebKit three-octagon screenshots were opened and visually inspected. The existing WEST/SOUTH game artwork is still simplified, not comparable with original Matrei. Four near-Matrei modern aerial candidates were retained for **material research only**: sites 03, 05, 06, 08. Site 00/01/02/04/07 were not admitted into this mask pipeline.

## Code and deliberately conservative visual decisions

`scripts/v218_reviewed_modern_quarantine.py` fetches **only 16 original 256×256 JPEGs** (4 sites × 4 native EPSG:3857 source tiles), preserves their SHA-256 and native 512×512 decoded RGB, and emits each original source, an exact binary L mask, and a transparent RGBA quarantine image. Pixel values outside the mask remain bit-identical. Masked pixels become (0,0,0,0) **unavailable**, never invented foliage or false reconstructed terrain. An actual original-versus-quarantined contact with attribution is emitted as a CI artifact. Gaps between the four sites remain unsampled.

The exclusion polygons were manually reviewed against actual V217 source screenshots at native 512-pixel coordinates. Site 03: four 2023 date marks, a small meadow structure **and its visible access track**. Site 05: four date marks, the upper-left road/building/clearing complex **and the remaining southwest road continuation**. Site 06: four date marks, the prominent logged/cleared strip **and the visible eastbound track**. Site 08: four date marks, the small eastern structure, the lower-right modern track **and a small top-left structure**. Polygon exclusion is deliberately broad in uncertain areas. **Other modern features may remain; this is NOT a certified period-safe material bank.**

`scripts/test_v218_reviewed_modern_quarantine.py` rejects changed site identities, source XYZ/URLs, geometry/mask edits, changed native JPEGs, original RGB substitutions, masked pixel tampering, contact changes, and any false approval/registration claims. CI runs all inherited V204–V217 source controls and the original four-browser V137/V192–V202 road/bridge/army/camera checks. The strict V203 playable-art gate is preserved **unchanged** and is expected to fail until WEST/SOUTH actually improve. Historical V140 detail script is not present on the V217 parent branch; this work does not fabricate or replace it.

## Actual CI artifact inspection and corrective revision

First V218 native-source job in [CI 40359051126](https://github.com/wayfinderandco0-cell/century-of-empires/actions/runs/40359051126) passed. Downloaded and opened actual original-versus-quarantined artifact 12667012373 (not a synthetic fixture). Its native images showed the date boxes and main exclusion regions worked, but also revealed **additional visible modern track segments** in sites 03, 05 and 06 and a small top-left structure in site 08. Expanded the corresponding source-pixel masks and added four specific regression points. The revised source job must be rerun and the new actual artifact reinspected; this does not make the material historically safe.

## Recovered inherited V137 browser gate

First V218 full browser CI revealed a separate pre-existing test harness defect: `scripts/qa_v137_coherent.py` requested nonexistent `v137-continuous-alpine-preview.html`, timed out, and prevented the later unchanged movement/art gates from executing. The actual retained file is `v137-coherent-alpine-preview.html`. Updated only that stale test URL on this isolated branch, leaving every fail-closed geometry, screenshot, route and movement assertion intact. Subsequent CI must confirm V137 and later gates actually execute. No gameplay or V137 renderer code changed.

## Non-negotiable interpretation

Modern 2023 aerial images are **NOT** evidence of exact 1780 forest boundaries, historic roads, bridges, traversability or V121/V123 photo coordinates. This source quarantine does not register any of the three game octagons. No new source pixels are placed in the game; original 1536×1024 Matrei art and V121/V123 control geometry remain unchanged. No claims of game art approval, physical iPhone approval, or production readiness.

`registeredToV121=false; registeredToV123=false; historicalRoadsVerified=false; allModernFeaturesExcluded=false; periodSafe=false; gameArtApproved=false; physicalIPhoneApproved=false; productionApproved=false`.

**Next:** Inspect the actual V218 CI original-versus-quarantined contact and confirm all visible 2023 marks and large modern features are excluded. If any are missed, expand the reviewed mask and rerun strict source tests. Then seek independently verified natural tiepoints for Matrei; only after that consider a separate opt-in photographic material trial that keeps all route geometry immutable and visibly fails if photographic continuity or user approval is missing.

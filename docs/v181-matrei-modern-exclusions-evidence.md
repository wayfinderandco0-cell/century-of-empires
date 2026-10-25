# V181 — conservative Matrei modern-feature exclusion (2026-10-25)

**SOURCE STUDY ONLY — NOT PERIOD GAME ART, NOT THREE GAME OCTAGONS.** This isolated branch builds on V180 and does not modify production main, campaign saves, the V121 painted Matrei photograph or the V123 immutable road graph.

## Evidence reviewed

- Read issue #9 through V180 and checked V180 CI run [40176746873](https://github.com/wayfinderandco0-cell/century-of-empires/actions/runs/40176746873), which passed.
- Downloaded and visually inspected **actual V180 1536×1024 Matrei orthophoto** from [artifact 12593190495](https://github.com/wayfinderandco0-cell/century-of-empires/actions/runs/40176746873/artifacts/12593190495). It shows a north/south divided motorway, a railway and station corridor, two marked sports areas, and buildings of unverified age. The southwest 768×512 area was never acquired.
- Reopened actual V171 WebKit iPhone-layout whole-crossing screenshot from [artifact 12578863866](https://github.com/wayfinderandco0-cell/century-of-empires/actions/runs/40142947845/artifacts/12578863866). GAME West/South are still synthetic; roads still end at survey limits. Strict V171 visual GAME gate remains **0/4**.

## Implemented

- [scripts/v181_matrei_exclusions.py](../scripts/v181_matrei_exclusions.py) creates a native-coordinate, transparent exclusion mask for four visually identifiable modern source features: motorway (64px corridor), railway (32px corridor), north athletic field and south pitches/courts. All outlines are approximate **image review annotations, not geospatial surveys or historical alignments**.
- Before processing, it verifies all **18 original JPEG SHA256 hashes**, XYZ origin **[69701,46030,17]**, 256px tile placements, original mosaic SHA256 and exact mosaic-vs-JPEG pixels. It preserves attribution **Datenquelle: basemap.at (CC BY 4.0)**.
- Produces **matrei-modern-exclusion-mask.png**, **matrei-modern-excluded-SOURCE.png**, and a manifest. Masked or unacquired pixels remain transparent; all other source pixels remain **byte-for-byte identical**. No inpainting, roads, buildings, trees, or period details are invented.
- The source image inspected locally yielded **154,694 excluded observed pixels of 1,179,648 observed (13.114%)**. This is a measured mask coverage fraction, **not a game-art quality score**.
- [Eight tests](../scripts/test_v181_matrei_exclusions.py) check native source integrity, motorway/rail/sports exclusion and forest/meadow/river retention, and reject altered JPEGs, altered source PNG, altered mask/output or false period-art approval. All eight passed locally against the real downloaded V180 artifact.
- [Dedicated CI](../.github/workflows/qa-v181-matrei-exclusions.yml) re-runs V172/V178/V179/V180 geographic safeguards, downloads and verifies real Matrei source, then executes V181 tests and exports source-only review artifacts.

## Known limits / next

- Remaining buildings and urban areas **have not been historically classified or cleared for use**; masked strips expose transparent unknowns, not completed 1780–1880 landscape. Source modern rail alignment must not be treated as a historic route.
- Matrei native source is **one small neighborhood**; Western Pass and Southern Valley geographic GAME footprints remain unresolved. No independent V121↔geographic landmark registration or V123 historical bridge/road evidence has been established.
- **Next highest-impact:** review remaining building-era-unknown source zones and establish historically evidenced Matrei/West/South game footprints and road/bridge banks. Only after source interpretation and registration should three connected GAME octagons be authored and retested against unchanged V140/V171 visual, route, seam and movement gates. Actual iPhone visual approval remains required.
- All certification flags remain false: source sectors as GAME cells, V121↔geography, V123 road registration, historical roads, bridge banks, 1780 certification, period art, physical iPhone and production.

This mask is a safe **partial subtraction of known modern material**, not a completed art replacement.

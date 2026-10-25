# V185 — South Tyrol source fills a tested Austrian basemap coverage gap (SOURCE ONLY)

**2026-10-25.** Isolated branch `terrain-v185-south-tyrol-crossborder-probe-20261025`.
No main/live/V94 saves/V121 original art/V123 road controls changed.

## Evidence reviewed before coding

- GitHub issue #9 through V184 and the successful V184 CI [40193742019](https://github.com/wayfinderandco0-cell/century-of-empires/actions/runs/40193742019).
- Downloaded and visually inspected the **actual V171 WebKit portrait whole-crossing GAME screenshot** (artifact 12578863866): Matrei remains an isolated sharp photo patch; neighboring GAME areas remain synthetic and outer roads end at unverified survey limits. Strict V171 GAME visual approval remains 0/4.
- Downloaded and visually inspected the **actual V184 60-tile SOURCE image** (artifact 12598932191): large white wedge in southern image, not a completed geographic source.
- [basemap.at](https://basemap.at/en/) says its imagery is based on Austrian administrative geodata and covers Austria; this is a plausible explanation for white pixels near the Austria–Italy boundary, **not a surveyed border mask**.
- Located independent [Autonomous Province of Bolzano / South Tyrol 2023 orthophoto metadata](https://data.civis.bz.it/de/dataset/ortofoto-2023): 20-cm aerial imagery, published under a **CC BY 4.0** statement in the dataset description. The portal also displays a CCZero heading, so use the more conservative attribution requirement until clarified. The official [Italian geodata registry](https://geodati.gov.it/geoportale/visualizzazione-metadati/scheda-metadati?metadataid=p_bz%3AOrthoimagery%3AAerial-2023-RGB) lists the WMS/WMTS distribution.

## Implemented and independently tested

- [Source probe](../scripts/v185_south_tyrol_probe.py) derives the WMS request from V184's canonical **EPSG:3857** native tile geometry, targeting the visibly white V184 tile `r11c03` (XYZ **8715/5763/14**, 256×256).
- WMS layer `Aerial-2023-RGB` is requested from the independent South Tyrol provider, not from basemap.at. Native image bytes, source SHA256, original V184 60-tile manifest integrity, exact geographic bounds, source attribution and false approval flags are validated.
- [Seven new fail-closed tests](../scripts/test_v185_south_tyrol_probe.py) cover native registration, forbidden historic/bridge/production claims, XML/non-JPEG responses, blank alternative imagery, SHA tampering, source alteration, and candidate-only coverage.
- [CI run 40198021170](https://github.com/wayfinderandco0-cell/century-of-empires/actions/runs/40198021170) **SUCCESS**: V184's 11 tests plus all V185's 7 tests, reuses and verifies the real V184 artifact, downloads a real independent Italian 256px JPEG, validates exact native source pixel correspondence, and uploads [V185 source artifact](https://github.com/wayfinderandco0-cell/century-of-empires/actions/runs/40198021170/artifacts/12600239463).
- Downloaded and **opened the actual V185 candidate image**, compared side by side against original V184 `r11c03.jpeg`. Alternative contains visible forest, meadow and modern highway where Austrian source is mostly white. This is **modern geographic imagery**, not historical period art.

## Actual measured source improvement

The verified original V184 source tile has **59,118 / 65,536** near-white pixels. The independent South Tyrol tile has **65,536 / 65,536** non-white pixels; **59,118** source-white positions have non-white candidate imagery. This is a single **candidate** tile (90.2% of its area), not 59,118 approved game pixels or an approved border mosaic. SHA256 and source provenance match the CI artifact. Both sources retain attribution.

The test refuses to merge, inpaint, invent roads or assert completed coverage. `alternativeCoverageApproved=false`, `gameArtCoverageApproved=false`, `historic1780Certified=false`, `bridgeBanksVerified=false`, `physicalIPhoneApproved=false`, `productionApproved=false`.

## Next highest-impact task

Acquire the remaining South Tyrol source tiles intersecting V184's suspected southern provider gap, compare geographic overlap and color/imagery seams, and build a **candidate-only transparent geographic source mask** that never paints over verified Austrian pixels. Independently locate the actual three GAME cell footprints and historical road/bridge tie points before any period-appropriate game-art reconstruction. Keep unchanged V140/V171 strict iPhone browser gates; no production approval without physical user acceptance.

**Known CI maintenance constraint:** V185 currently reuses V184's seven-day Actions artifact; after its expiry the source will need re-acquisition through the existing verified V184 script or a retained, properly licensed repository asset. Do not call the source probe indefinitely reproducible without addressing this.

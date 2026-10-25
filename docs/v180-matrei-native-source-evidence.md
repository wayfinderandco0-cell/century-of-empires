# V180 — independently located Matrei native-source L (2026-10-25)

**Status: authentic modern geographic SOURCE acquired and verified; three GAME octagons remain visually rejected.** Development branch `terrain-v180-matrei-native-source-20261025` only. No main, live deployment, V94 campaign/save, V121 painting or V123 route edits.

## Inspected before development

- Read issue #9 through V179 and verified V179 CI [40172504160](https://github.com/wayfinderandco0-cell/century-of-empires/actions/runs/40172504160).
- Downloaded and inspected **actual V171 WebKit portrait whole-crossing screenshot** from [artifact 12578863866](https://github.com/wayfinderandco0-cell/century-of-empires/actions/runs/40142947845/artifacts/12578863866). Matrei is a sharp isolated photo patch; West/South remain artificial terrain, and roads end at question-mark survey limits. V171 strict GAME-art gate remains **0/4**, even though four technical browser checks passed.

## Actual source acquisition

- [scripts/v180_matrei_source.py](../scripts/v180_matrei_source.py) uses the independently sourced modern Matrei town reference **11.45306 E, 47.13083 N** from V179, rather than the former Navis reference **11.520 E, 47.130 N**.
- Acquired **18 unique native 256×256 modern basemap.at orthophoto JPEGs** (EPSG:3857, XYZ zoom 17, original-pixel 1536×1024 L). The southwest quadrant is **explicitly unacquired/transparent**, not synthesized.
- Geographic bounds: **[11.43951416015625, 47.12621341795226, 11.45599365234375, 47.13368783277606]**. This is one Matrei neighborhood source study, **not** three regional GAME cells, not a historical road survey, and not a V121→world registration.
- Source: [basemap.at orthofoto](https://basemap.at/orthofoto/), **CC BY 4.0**; required attribution **Datenquelle: basemap.at**. Keep attribution with all source-derived studies.
- [scripts/test_v180_matrei_source.py](../scripts/test_v180_matrei_source.py) checks 18 exact unique XYZ positions, V179 anchor agreement, nonreuse of V168 Navis tile coordinates, native image pixels, SHA256 provenance, missing/altered tile rejection, southwest transparency, and fail-closed GAME/road/bridge/historical approval flags.

## Verified CI and actual image inspection

- [GitHub Actions 40176746873](https://github.com/wayfinderandco0-cell/century-of-empires/actions/runs/40176746873) **SUCCESS**. V172, V178, V179 regressions and **9 V180 tests** passed; 18 real source JPEGs downloaded, assembled, and reverified against PNG pixel bytes.
- Downloaded and opened the [actual CI source artifact 12593190495](https://github.com/wayfinderandco0-cell/century-of-empires/actions/runs/40176746873/artifacts/12593190495). All **18 JPEG SHA256 hashes are distinct**; output PNG is 1536×1024 RGBA, SHA matches manifest, southwest alpha=0. Native-pixel adjacent-edge diagnostics: west/center mean RGB delta **3.0117**; center/south **8.2622**. This is source continuity, **not GAME seam acceptance**.
- **Critical visible blocker:** the real Matrei imagery contains a modern divided highway, rail line, dense modern buildings, and sports fields. These features cannot be transferred uncritically into an 1780–1880 scene. The western source has forest/meadow detail, but the southern-western source remains unacquired and the eastern image requires modern-infrastructure exclusion.

## Next concrete task

Build a conservative **source-only Matrei modern-feature exclusion mask** with explicit unknown boundaries for highway/rail/modern buildings. Do not hallucinate pre-modern replacements. Separately establish historically evidenced routes and a bridge with both banks, and independently resolve the Western Pass and Southern Valley GAME geographic footprints before trying to render three GAME cells. Keep V140/V171 strict GAME-art checks unchanged and production approval false. Physical iPhone visual approval remains required.

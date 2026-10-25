# V182 — Matrei SOURCE date-imprint exclusion (2026-10-25)

**Source cleanup only. NOT 1780–1880 GAME artwork, NOT three connected Alpine octagons.**

## Evidence inspected
- Read roadmap issue #9 through V181, confirmed V181 CI [40180837230](https://github.com/wayfinderandco0-cell/century-of-empires/actions/runs/40180837230), downloaded/opened the actual [V181 excluded source artifact](https://github.com/wayfinderandco0-cell/century-of-empires/actions/runs/40180837230/artifacts/12593387720) and [original V180 native source artifact](https://github.com/wayfinderandco0-cell/century-of-empires/actions/runs/40176746873/artifacts/12593190495).
- The authentic modern basemap.at 1536×1024 source includes repeated white **2023** image labels on forests and pastures. They are contemporary image stamps, not period map labels. The V181 modern motorway/rail/sports mask left seven visibly identifiable full/partial stamps.
- Reviewed native-pixel centers: (0,96), (320,96), (640,96), (1280,96), (0,416), (320,416), (640,416). The x=0 samples are clipped at the image edge. Other candidate positions were inspected but not added without a visible stamp.

## Actual coding
- [V182 source-only exclusion script](../scripts/v182_matrei_imprints.py) validates V180's 18 JPEGs and V181's image/mask/manifest through V181's original verifier, then transparently excludes only seven small reviewed native-pixel date-stamp rectangles. No inpainting, image scaling, invented trees/roads, or GAME changes.
- [V182 regression tests](../scripts/test_v182_matrei_imprints.py) reject altered V181 input, tampered output/mask, false period-art approval, and check source/terrain retention.
- [Dedicated CI](../.github/workflows/qa-v182-matrei-imprints.yml) re-runs V172/V178/V179/V180/V181 safeguards, downloads the original 18 native tiles, and exports inspection artifacts.
- Local inspection of real V181 image pixels confirms **6,372 newly excluded source pixels**, seven center pixels transparent, and unchanged sampled forest/meadow/river pixels. This count is NOT a visual quality score. Source attribution remains **Datenquelle: basemap.at (CC BY 4.0)**.

## Remaining blockers
- Most age-unknown/modern built environment remains in the Matrei SOURCE; excluded regions and southwest missing source remain transparent, not reconstructed. Neither source masks nor their high resolution establish an 1780–1880 period surface.
- West/South GAME footprints, source↔V121 landmarks, historic V123 roads and bridge banks, coherent period GAME art, strict V140/V171 four-browser visual acceptance, and physical iPhone approval remain unresolved. All GAME/historic/production flags remain false.
- **Next:** independently review/quarantine remaining age-unknown buildings and acquire historic road/crossing evidence. Do not interpret the surviving orthophoto as period-safe or deploy it into the GAME.

Production main, V94 campaign/saves, V121 painting and V123 route graph were not changed.

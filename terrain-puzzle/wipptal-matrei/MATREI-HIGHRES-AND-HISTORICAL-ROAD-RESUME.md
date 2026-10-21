# Matrei terrain foundation — source and history checkpoint
Date: 2026-10-20.

## Newly solved: measured fine terrain
The State of Tyrol terrain WCS (https://gis.tirol.gv.at/arcgis/services/Service_Public/terrain/MapServer/WCSServer) responded and exposed `Gelaendemodell_50cm_M28` as an available 50cm ground digital terrain layer. The Matrei test retrieved GeoTIFF in `EPSG:31254`, inspected it and reprojected a roughly 1m sample into `EPSG:32632` as a high-resolution painting foundation. This is **modern topography**, not historical circa-1800 vegetation or structures.
- Source Tyrol official documentation: https://www.tirol.gv.at/sicherheit/geoinformation/geodaten-tiris/laserscandaten
- Discovery record: `terrain-puzzle/wipptal-matrei/tirol-high-res-source-discovery.json`
- Probe record: `terrain-puzzle/wipptal-matrei/matrei-highres-wcs-probe.json`
- Renderer: `scripts/build_matrei_fine_relief.py`
- Outputs: `matrei-1800-georelief-study.webp` and `matrei-1800-georelief-debug.webp` plus comparison/QA JSON. **Art study, not approved final aesthetic.**
- Browser-facing isolated review is published as `v107-matrei-terrain-study.html` on main, with source assets only; all gameplay unchanged. QA passed Chromium/WebKit browser sizes; real physical iPhone Safari not yet tested by user.

## Historic road positional evidence not yet complete
The documented Brenner trade corridor through Wipptal existed by 1800 (road upgrades from 1777). The 1,036m modern OSM B182 guide in the Matrei 1km octagon is only a candidate. One mapped Waldraster Bach crossing is blocked and unapproved. Candidate 27 nodes, 26 links disabled.

A stronger positional baseline may be extracted from the **Franziszeischer Kataster** (early-to-mid 19th century, roughly 1817–1861) for Tirol. University of Innsbruck's 2026 FRANZI project presents georeferenced Tyrol cadastral map sheets and historical land records:
- https://geschichte-franzi.uibk.ac.at/franzi/
- https://www.bev.gv.at/Services/Produkte/Kataster-und-Verzeichnisse/Historischer-Kataster-Urmappe.html
- Another viewer for the same period: https://maps.arcanum.com/de/map/cadastral/

This is *not* 1800 evidence exactly. Any reconstructed Matrei road alignment based on 1820–1850 plans requires qualification about intervening road changes and distinction from later 1833–1845 construction. Do not copy modern B182 nor imagine bridges. Explicit next action: locate Matrei source map, identify original road and Waldraster Bach crossing if depicted, georeference it and compare with 2026 LiDAR ground and modern OSM line. Then rebuild the period-plausible centerline, trail rendering, and 27+ invisible nodes from the **same final approved vector**.

## Graphics lessons retained
- Higher-resolution terrain geometry is a genuine foundation but does not itself make high-quality art. V107 forest and river material are preliminary, not professional final graphics and may require upgraded textures, canopy shapes, riverbanks and house artwork.
- Do not backfill forest/roof microdetails with historically unverified claims.
- No visible puzzle lines/dots normally; debug switch only.
- Do not activate a route crossing a stream merely because two graphic path lines touch.
- Preserve rejected Navis Octagon 001 routes as retired and inaccessible. The original campaign and save keys remain untouched.

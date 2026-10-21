# Matrei V108 — Visual correction checkpoint (2026-10-20)

## User iPhone screenshots: V107 was rejected as professional art
The actual V107 Atlas, Region, Local, Terrain screenshots show:
- narrow straightish tan ribbon instead of believable historical road with shoulders, wear and texture;
- uniform blue stream lines without water materials, banks, shadows or small deposits;
- scattered round green blobs presented as trees;
- eight identical small rectangular huts in open fields, inconsistent with Matrei's long-established road-market street settlement;
- nearly uniform dark mossy surface without photographic / artistic foliage detail;
- magnified one-resolution material at all four scales and oversized title covering visible world at Local/Terrain zoom.

**Keep V107's actual high-resolution topographic DGM and the route coordinates. Replace its material renderer and fictional settlement placement.** Do NOT repeat the failed procedural circles/rectangles graphics and do not start another octagon.

## Verified new source
- Official Tyrol orthophoto service: `https://gis.tirol.gv.at/arcgis/services/Service_Public/orthofoto/MapServer/WMSServer`
- GetCapabilities layer `Image_Aktuell_RGB` exists, but WMS 1.3.0 + EPSG:31254 bbox in the originally requested axis order yielded a WHITE image despite HTTP 200. Working request is **WMS 1.1.1 / SRS=EPSG:31254**, east/north BBOX.
- Verified 600×600m Matrei ground photo, requested 900×900px, at center **11.453056°E / 47.130278°N**, projected `EPSG:31254` center (84977.6595, 221866.6664). Image RGB standard deviation ≈ (47,41,41) (non-blank). File `terrain-puzzle/wipptal-matrei/matrei-official-modern-orthophoto-reference.jpg`, and diagnostic `matrei-orthophoto-probe.json`.
- Image license is **CC BY 4.0 / © Land Tirol**; preserve source attribution and official credits if using photographic materials.
- The photo visibly shows a **dense central street settlement**, a **modern motorway to the west** and a **modern railway / associated infrastructure to the east**. The latter are NOT suitable for circa-1800 game artwork. Do not publish unedited modern orthophoto as historical game texture.
- Historical support: Matrei was elevated to a market in 1251 and developed a road-side community with inns and workshops serving Brenner traffic. The early-19th-century cadastral Urmappe (1817–1861) / University of Innsbruck FRANZI platform is a stronger source for c.1800 period settlement geometry than modern aerial photography; its individual Matrei survey date and property geometry still need to be confirmed.
- Historical references: https://de.wikipedia.org/wiki/Matrei_am_Brenner ; https://de.wikipedia.org/wiki/Ansitz_Ballenhaus ; https://geschichte-franzi.uibk.ac.at/franzi/ ; https://www.bev.gv.at/Services/Produkte/Kataster-und-Verzeichnisse/Historischer-Kataster-Urmappe.html

## Concrete next build: one Matrei subscene, not a new atlas
1. Retrieve a geographically exact 1120m full-bleed orthophoto (with tiled WMS if needed) matching 50cm DGM origin/CRS; reject blank data, preserve CC BY attribution.
2. Use real imagery to author **ground materials and forest/river-bank textures**, but mask roads/railways/motorway/new buildings/parking lots/modern utility structures. The orthophoto is modern color / texture reference, not an 1800 survey.
3. Inspect period cadastral map: recreate historically plausible street-wall density and varied Tyrolean buildings aligned along the road, not isolated identically sized boxes; preserve one plausible road centerline and block historically unverified stream crossing.
4. Create separate Atlas/Region/Local/Terrain LOD materials; at closer zoom use sharper canopies, roofs, ruts, hedges, rocks, channel-edge detail; prevent pixel magnification. Keep clean + debug toggles identical and hidden dots from same polyline as the visible road.
5. Reduce header chrome on close zoom to show playable screen area on iPhone.
6. Validate visible graphic quality with **real iPhone screenshots**, not merely automated WebKit page behavior. Do not publish a new V108 until visibly superior to V107 and user approved.

## Preservation
- V107 stays a proof of geographic alignment but is not visually approved.
- Matrei candidate: 1,035.69m modern map-guide, 27 proposed dots, 26 links all disabled; Waldraster Bach crossing blocked until historically/physically approved.
- Retired Navis Octagon 001 candidate trails stay rejected; no gameplay/campaign save changes.

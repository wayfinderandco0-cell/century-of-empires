#!/usr/bin/env python3
"""V200: place V199 *modern reference-site coordinates* on V97 measured relief.

This is a SOURCE-ONLY geographical audit. It never locates a V123 octagon,
adds a road, alters a painted photograph, or claims 1780 vegetation.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
from PIL import Image, ImageDraw

PINNED_V199_SHA256 = "e0ec6301c689d76b40018c5297395bf8b7f055e37cf5d647b374e0cb17124557"
BOUNDS = [11.26, 46.80, 11.80, 47.42]
GRID = [260, 300]
SIZE = [1552, 1782]
GROUPS = ("western_forest_reference", "eastern_ridge_reference", "southern_forest_reference")
REQUIRED_FALSE = ("gameWorldRegistrationKnown", "periodSafe", "gameArtApproved",
                  "historicalRoadsVerified", "bridgeBanksVerified",
                  "physicalIPhoneApproved", "productionApproved")


def require(ok, why):
    if not ok:
        raise ValueError(why)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def native_bounds(origin, rect):
    tx, ty, z = origin
    require(z == 18 and all(isinstance(q, int) for q in origin), "wrong native XYZ origin")
    require(0 <= tx < 2**z and 0 <= ty < 2**z, "native XYZ outside planet")
    l, t, r, b = rect
    require(all(isinstance(q, int) for q in rect) and
            0 <= l < r <= 512 and 0 <= t < b <= 512 and
            r-l == b-t == 160, "invalid original pixel crop")
    n = 2**z
    lon = lambda x: (tx + x/256)/n*360-180
    lat = lambda y: math.degrees(math.atan(math.sinh(math.pi*(1-2*(ty+y/256)/n))))
    return [lon(l), lat(b), lon(r), lat(t)]


def atlas_xy(lon, lat, bounds, dimensions):
    w, s, e, n = bounds
    require(w <= lon <= e and s <= lat <= n, "site outside geographic atlas")
    return [(lon-w)/(e-w)*dimensions[0], (n-lat)/(n-s)*dimensions[1]]


def haversine(a, b):
    lon1, lat1 = map(math.radians, a)
    lon2, lat2 = map(math.radians, b)
    dlat, dlon = lat2-lat1, lon2-lon1
    h = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    return 6371.0088*2*math.asin(min(1, math.sqrt(h)))


def audit(source, v97, v97_manifest, v102, v94, expected_manifest_sha=PINNED_V199_SHA256):
    if expected_manifest_sha is not None:
        require(digest(source) == expected_manifest_sha, "V199 artifact manifest changed")
    m = json.loads(Path(source).read_text())
    require(m.get("version") == 199 and m.get("crs") == "EPSG:3857" and
            m.get("nativeZoom") == 18 and m.get("nativeCropPixels") == [160, 160],
            "V199 source identity/projection changed")
    require(m.get("requiredAttribution") == "Datenquelle: basemap.at" and
            m.get("license") == "CC BY 4.0" and
            m.get("onlyAnnotatedFeaturesExcluded") is True, "source provenance changed")
    require(all(m.get(k) is False for k in REQUIRED_FALSE), "false source/game approval")
    require(v97.get("boundsLonLat") == v97_manifest.get("boundsLonLat") == BOUNDS and
            v97.get("heightGrid") == v97_manifest.get("heightGrid") == GRID and
            v97.get("imageSize") == v97_manifest.get("imageSize") == SIZE and
            "Copernicus" in v97.get("elevationSource", "") and
            "WorldCover" in v97.get("landCoverSource", ""), "V97 relief identity mismatch")
    require(v102.get("version") == 102 and
            v102.get("boundsLonLat") == [11.43, 47.075, 11.625, 47.19] and
            v102.get("grid") == [257, 257], "V102 Navis frame changed")
    require(v94.get("version") == "94" and v94.get("projection") == "equirectangular" and
            v94.get("extent") == [-14, 26, 49, 75] and
            v94.get("atlasSize") == [8192, 6144], "V94 atlas frame changed")
    elevations, forest = v97.get("elevationM"), v97.get("treeGrid")
    require(isinstance(elevations, list) and isinstance(forest, list) and
            len(elevations) == len(forest) == GRID[0]*GRID[1], "V97 numeric grid missing")
    require(all(isinstance(v, (int, float)) and math.isfinite(v) and -100 < v < 9000
                for v in elevations), "invalid V97 elevation")
    require(set(forest) <= {0, 1}, "invalid modern forest proxy")
    crops = m.get("crops")
    require(isinstance(crops, list) and len(crops) == 9, "nine independent crops required")
    rows, names = [], set()
    for item in crops:
        name, group = item.get("name"), item.get("sourceSample")
        require(group in GROUPS and isinstance(name, str) and
                name not in names and name.startswith(group+"-clean-reference-"),
                "duplicate or unexpected crop")
        names.add(name)
        require(item.get("annotatedFeaturePixelsInside") == 0 and
                item.get("maskClearancePixels") == 12 and
                item.get("eligibleForGameArt") is False and
                item.get("historicalNaturalCoverVerified") is False and
                item.get("modernFeaturesFullyExcluded") is False,
                "unsafe crop approval or exclusion")
        box = native_bounds(item["nativeOriginXYZ"], item["sourcePixelRect"])
        require(len(item.get("footprintLonLat", [])) == 4 and
                all(abs(a-b) < 1e-10 for a, b in zip(box, item["footprintLonLat"])),
                "V199 crop native geolocation mismatch")
        lon, lat = (box[0]+box[2])/2, (box[1]+box[3])/2
        px, py = atlas_xy(lon, lat, BOUNDS, SIZE)
        ix = min(GRID[0]-1, int((lon-BOUNDS[0])/(BOUNDS[2]-BOUNDS[0])*GRID[0]))
        iy = min(GRID[1]-1, int((BOUNDS[3]-lat)/(BOUNDS[3]-BOUNDS[1])*GRID[1]))
        index = iy*GRID[0]+ix
        inside102 = (v102["boundsLonLat"][0] <= lon <= v102["boundsLonLat"][2] and
                     v102["boundsLonLat"][1] <= lat <= v102["boundsLonLat"][3])
        rows.append({
            "id": name, "group": group, "lonLat": [round(lon, 9), round(lat, 9)],
            "sourceBoundsLonLat": box,
            "v97ReliefPixel": [round(px, 4), round(py, 4)],
            "v97CoarseGridCell": [ix, iy],
            "v97ApproxElevationM": elevations[index],
            "v97ModernForestProxy": bool(forest[index]),
            "withinV102NavisBounds": inside102,
            "v94AtlasPixel": [round(q, 5) for q in
                              atlas_xy(lon, lat, v94["extent"], v94["atlasSize"])],
            "historicForestConfirmed": False, "gameOctagonRegistered": False,
            "gameRoadOrBridgeVerified": False, "eligibleForGameArtwork": False,
        })
    clusters = {}
    for group in GROUPS:
        subset = [r for r in rows if r["group"] == group]
        require(len(subset) == 3, "missing independent crop group")
        require(max(haversine(a["lonLat"], b["lonLat"]) for a in subset for b in subset)
                < 1.0, "group samples are not one local source study")
        clusters[group] = [sum(r["lonLat"][i] for r in subset)/3 for i in (0,1)]
    for i, a in enumerate(GROUPS):
        for b in GROUPS[i+1:]:
            require(haversine(clusters[a], clusters[b]) > 1.0,
                    "independent source regions collapsed together")
    lat_mid = sum(r["lonLat"][1] for r in rows)/len(rows)
    meters = [111320*math.cos(math.radians(lat_mid))*(BOUNDS[2]-BOUNDS[0])/GRID[0],
              111320*(BOUNDS[3]-BOUNDS[1])/GRID[1]]
    return {
        "version": 200, "v199SourceManifestSha256": digest(source),
        "purpose": "MODERN SOURCE study registration on coarse V97 relief; NOT game mapping",
        "v97GridApproxCellMeters": [round(q, 1) for q in meters],
        "v97DataResolutionInsufficientForRoadOrBridgeSurvey": True,
        "v97ForestIsModern2021ProxyNot1780Evidence": True,
        "v102MaterialIsIllustrativeNotRegisteredV123GameArt": True,
        "siteGroups": {k: [round(v, 8) for v in xy] for k,xy in clusters.items()},
        "siteGroupSeparationKm": {
            a+"__"+b: round(haversine(clusters[a], clusters[b]), 3)
            for i,a in enumerate(GROUPS) for b in GROUPS[i+1:]},
        "sites": rows, "requiredAttribution": "Datenquelle: basemap.at",
        "license": "CC BY 4.0",
        "v121PhotoRegistered": False, "v123RoadsRegistered": False,
        "periodSafe": False, "historicalRoadsVerified": False,
        "bridgeBanksVerified": False, "gameArtApproved": False,
        "physicalIPhoneApproved": False, "productionApproved": False,
    }


def render_map(report, relief_path, out_path):
    with Image.open(relief_path) as source:
        require(source.size == tuple(SIZE), "V97 relief raster dimensions changed")
        image = source.convert("RGB")
    canvas = Image.new("RGB", (SIZE[0], SIZE[1]+115), (23, 29, 29))
    canvas.paste(image, (0, 115))
    draw = ImageDraw.Draw(canvas)
    draw.text((24, 18), "V200  |  MODERN ALPINE SOURCE-SITE LOCATIONS  |  NOT GAME OCTAGONS",
              fill=(255, 244, 210))
    draw.text((24, 44), "Copernicus 2021 relief / ESA 2021 cover / basemap.at reference crops",
              fill=(215, 225, 220))
    draw.text((24, 70), "Coarse regional context only. No 1780 roads, bridge banks or game registration.",
              fill=(255, 200, 165))
    tags = {"western_forest_reference": "W (3 source crops)",
            "eastern_ridge_reference": "E (3 source crops)",
            "southern_forest_reference": "S (3 source crops)"}
    for group, label in tags.items():
        lon, lat = report["siteGroups"][group]
        x, y = atlas_xy(lon, lat, BOUNDS, SIZE)
        x, y = int(x), int(y)+115
        draw.ellipse((x-10,y-10,x+10,y+10), fill=(250,218,114), outline=(32,35,28), width=3)
        tx = x+17 if x < SIZE[0]-270 else x-230
        draw.rectangle((tx-4,y-13,tx+214,y+11),fill=(19,29,24))
        draw.text((tx,y-8),label,fill=(255,244,210))
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out_path)


def produce(source, relief_data, relief_manifest, v102_path, v94_path,
            relief_image, output):
    load = lambda p: json.loads(Path(p).read_text())
    report = audit(source, load(relief_data), load(relief_manifest),
                   load(v102_path), load(v94_path))
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    image_name = "v200-source-sites-on-v97-relief.png"
    render_map(report, relief_image, output/image_name)
    report["reviewImage"] = image_name
    report["reviewImageSha256"] = digest(output/image_name)
    (output/"manifest.json").write_text(json.dumps(report, indent=2)+"\n")
    return report


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--source", default="qa/v199-clean-native-crops/manifest.json")
    p.add_argument("--v97", default="terrain-v97/brenner-data.json")
    p.add_argument("--v97-manifest", default="terrain-v97/manifest.json")
    p.add_argument("--v102", default="terrain-v102/manifest.json")
    p.add_argument("--v94", default="terrain-v94/manifest.json")
    p.add_argument("--relief", default="terrain-v97/brenner-relief.webp")
    p.add_argument("--output", default="qa/v200-source-biome-audit")
    args = p.parse_args()
    result = produce(args.source,args.v97,args.v97_manifest,args.v102,args.v94,
                     args.relief,args.output)
    print("V200 SOURCE geography verified:", len(result["sites"]),
          "crop sites; GAME registration/visual approval FALSE")


if __name__ == "__main__":
    main()

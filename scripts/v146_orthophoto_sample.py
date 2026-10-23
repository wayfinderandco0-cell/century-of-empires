#!/usr/bin/env python3
"""Small, attributable modern basemap.at orthophoto samples for geographic inspection.

These points sample the retained V102 Navis geographic bounds; they are NOT
V123 road-to-world controls, historical routes, or game-octagon centers.
No imagery is incorporated into production artwork or navigable geometry.
"""
import argparse
import hashlib
import io
import json
import math
from pathlib import Path
from urllib.request import Request, urlopen

from PIL import Image

BASE = "https://mapsneu.wien.gv.at/basemap/bmaporthofoto30cm/normal/google3857"
SOURCE = "https://basemap.at/orthofoto/"
LICENSE = "https://creativecommons.org/licenses/by/4.0/"
# Explicit geographic inspection points in V102's smaller bounds.
POINTS = {
    "navis_center": (11.520, 47.130),
    "navis_northwest": (11.495, 47.140),
    "navis_southeast": (11.545, 47.120),
}


def lonlat_to_xyz(lon, lat, zoom):
    if not (math.isfinite(lon) and math.isfinite(lat) and -180 <= lon <= 180
            and -85.05112878 < lat < 85.05112878 and 0 <= zoom <= 20):
        raise ValueError("Invalid EPSG:3857 tile coordinates")
    n = 1 << zoom
    x = min(n - 1, max(0, math.floor((lon + 180) / 360 * n)))
    phi = math.radians(lat)
    y = min(n - 1, max(0, math.floor((1 - math.asinh(math.tan(phi)) / math.pi) / 2 * n)))
    return x, y


def xyz_bounds(x, y, z):
    n = 1 << z
    if not (0 <= x < n and 0 <= y < n):
        raise ValueError("Tile index out of range")
    def latitude(row):
        return math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * row / n))))
    return [(x / n) * 360 - 180, latitude(y + 1),
            ((x + 1) / n) * 360 - 180, latitude(y)]


def plan(source_manifest, zoom=17):
    bounds = source_manifest["boundsLonLat"]
    if len(bounds) != 4 or not (bounds[0] < bounds[2] and bounds[1] < bounds[3]):
        raise ValueError("Invalid V102 bounds")
    records = []
    for name, (lon, lat) in POINTS.items():
        if not (bounds[0] <= lon <= bounds[2] and bounds[1] <= lat <= bounds[3]):
            raise ValueError("Sample outside V102 geographic bounds")
        x, y = lonlat_to_xyz(lon, lat, zoom)
        tile_bounds = xyz_bounds(x, y, zoom)
        if not (tile_bounds[0] <= lon <= tile_bounds[2] and
                tile_bounds[1] <= lat <= tile_bounds[3]):
            raise AssertionError("EPSG:3857 inverse projection mismatch")
        records.append({"name": name, "pointLonLat": [lon, lat],
                        "tileXYZ": [x, y, zoom], "tileBoundsLonLat": tile_bounds,
                        "url": f"{BASE}/{zoom}/{y}/{x}.jpeg"})
    return {"version": 146, "purpose": "Modern source imagery inspection only",
            "geographicSource": "terrain-v102/manifest.json",
            "sourceBoundsLonLat": bounds, "crs": "EPSG:3857",
            "provider": "basemap.at", "sourceUrl": SOURCE,
            "license": "CC BY 4.0", "licenseUrl": LICENSE,
            "requiredAttribution": "Datenquelle: basemap.at",
            "historic1780Certified": False, "gameRouteGeoregistered": False,
            "gameOctagonCentersCertified": False, "productionApproved": False,
            "samples": records}


def fetch_images(manifest, outdir, timeout=20):
    outdir.mkdir(parents=True, exist_ok=True)
    for sample in manifest["samples"]:
        request = Request(sample["url"], headers={"User-Agent": "CenturyOfEmpires-SourceAudit/1.0"})
        with urlopen(request, timeout=timeout) as response:
            data = response.read(1024 * 1024 + 1)
            content_type = response.headers.get("Content-Type", "")
        if len(data) > 1024 * 1024 or not data.startswith(b"\xff\xd8"):
            raise ValueError("Source returned non-JPEG or oversized response")
        with Image.open(io.BytesIO(data)) as im:
            im.verify()
        with Image.open(io.BytesIO(data)) as im:
            if im.size != (256, 256) or im.format != "JPEG":
                raise ValueError("Unexpected orthophoto tile format/dimensions")
        if "image" not in content_type.lower():
            raise ValueError("Source returned non-image content type")
        filename = sample["name"] + ".jpeg"
        (outdir / filename).write_bytes(data)
        sample["imageFile"] = filename
        sample["sha256"] = hashlib.sha256(data).hexdigest()
        sample["byteCount"] = len(data)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", default="terrain-v102/manifest.json")
    parser.add_argument("--output", default="qa/v146-orthophoto-source")
    parser.add_argument("--zoom", type=int, default=17)
    parser.add_argument("--download", action="store_true")
    args = parser.parse_args()
    if not (0 <= args.zoom <= 20):
        parser.error("zoom must be between 0 and 20")
    source = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    report = plan(source, args.zoom)
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    if args.download:
        fetch_images(report, out)
    (out / "manifest.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"V146 geographic source samples: {len(report['samples'])} planned, "
          f"{sum('sha256' in s for s in report['samples'])} verified downloads; "
          "NO road or historical certification")


if __name__ == "__main__":
    main()

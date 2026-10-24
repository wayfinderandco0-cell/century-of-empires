#!/usr/bin/env python3
"""V147: georeferenced adjacent orthophoto mosaic, SOURCE INSPECTION ONLY.

Nine genuine adjacent basemap.at XYZ image tiles form one continuous geographic
raster without invented terrain, roads, villages, or image resampling. This
does NOT map V123 army coordinates to real geographic coordinates or establish
historical 1780–1880 road locations.
"""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image
from v146_orthophoto_sample import (BASE, SOURCE, LICENSE, lonlat_to_xyz,
                                   xyz_bounds, fetch_images)

ATTRIBUTION = "Datenquelle: basemap.at"
CENTER = (11.520, 47.130)
GRID = 3
PIXELS = 256


def plan_grid(source_manifest, zoom=17, center=CENTER):
    bounds = source_manifest["boundsLonLat"]
    if len(bounds) != 4 or not (bounds[0] < bounds[2] and bounds[1] < bounds[3]):
        raise ValueError("Invalid geographic source bounds")
    cx, cy = lonlat_to_xyz(*center, zoom)
    samples = []
    for row in range(GRID):
        for col in range(GRID):
            x, y = cx + col - 1, cy + row - 1
            west, south, east, north = xyz_bounds(x, y, zoom)
            if not (bounds[0] <= west < east <= bounds[2] and
                    bounds[1] <= south < north <= bounds[3]):
                raise ValueError("Adjacent source tile exceeds V102 geographic bounds")
            samples.append({
                "name": f"r{row}c{col}", "gridRow": row, "gridCol": col,
                "tileXYZ": [x, y, zoom],
                "tileBoundsLonLat": [west, south, east, north],
                "url": f"{BASE}/{zoom}/{y}/{x}.jpeg",
            })
    west = samples[0]["tileBoundsLonLat"][0]
    north = samples[0]["tileBoundsLonLat"][3]
    east = samples[-1]["tileBoundsLonLat"][2]
    south = samples[-1]["tileBoundsLonLat"][1]
    return {
        "version": 147, "purpose": "Modern geographic source raster inspection only",
        "geographicSource": "terrain-v102/manifest.json",
        "sourceBoundsLonLat": bounds, "crs": "EPSG:3857",
        "provider": "basemap.at", "sourceUrl": SOURCE,
        "license": "CC BY 4.0", "licenseUrl": LICENSE,
        "requiredAttribution": ATTRIBUTION,
        "centerLonLat": list(center), "grid": [GRID, GRID],
        "pixelDimensions": [GRID * PIXELS, GRID * PIXELS],
        "mosaicBoundsLonLat": [west, south, east, north],
        "worldLockedGeographicXYZ": True,
        "historic1780Certified": False, "gameRouteGeoregistered": False,
        "gameOctagonCentersCertified": False, "navigableRouteCertified": False,
        "productionApproved": False, "samples": samples,
    }


def validate_grid(manifest):
    tiles = manifest["samples"]
    if len(tiles) != GRID * GRID:
        raise ValueError("Incomplete adjacent source grid")
    positions = {(s["gridRow"], s["gridCol"]) for s in tiles}
    if positions != {(r, c) for r in range(GRID) for c in range(GRID)}:
        raise ValueError("Duplicate or missing source tile position")
    cx, cy, z = tiles[4]["tileXYZ"]
    for s in tiles:
        r, c = s["gridRow"], s["gridCol"]
        x, y, zz = s["tileXYZ"]
        if (x, y, zz) != (cx + c - 1, cy + r - 1, z):
            raise ValueError("Geographic XYZ adjacency broken")
        if s["tileBoundsLonLat"] != xyz_bounds(x, y, zz):
            raise ValueError("Geographic tile bounds tampered")
        if s["url"] != f"{BASE}/{zz}/{y}/{x}.jpeg":
            raise ValueError("Unrecognized geographic tile source")


def assemble(manifest, directory):
    """Stitch original JPEG pixels 1:1, verify each recorded SHA before use."""
    validate_grid(manifest)
    result = Image.new("RGB", (GRID * PIXELS, GRID * PIXELS))
    tiles = {}
    for s in manifest["samples"]:
        if "sha256" not in s or "imageFile" not in s:
            raise ValueError("Missing verified source image/hash")
        path = directory / s["imageFile"]
        data = path.read_bytes()
        if hashlib.sha256(data).hexdigest() != s["sha256"]:
            raise ValueError("Source image SHA256 mismatch")
        with Image.open(path) as original:
            if original.format != "JPEG" or original.size != (PIXELS, PIXELS):
                raise ValueError("Invalid source JPEG dimensions")
            im = original.convert("RGB")
        r, c = s["gridRow"], s["gridCol"]
        result.paste(im, (c * PIXELS, r * PIXELS))
        tiles[(r, c)] = im
    # Diagnostic only: an actual acquisition seam may be visible even though
    # tile placement is geometrically exact. Do not claim visual acceptance.
    edge_deltas = []
    for r in range(GRID):
        for c in range(GRID):
            here = tiles[(r, c)]
            if c + 1 < GRID:
                other = tiles[(r, c + 1)]
                delta = sum(abs(a - b) for y in range(PIXELS)
                            for a, b in zip(here.getpixel((PIXELS - 1, y)),
                                            other.getpixel((0, y))))
                edge_deltas.append({"orientation": "vertical", "row": r, "col": c,
                                    "meanRgbChannelDelta": round(delta / (PIXELS * 3), 3)})
            if r + 1 < GRID:
                other = tiles[(r + 1, c)]
                delta = sum(abs(a - b) for x in range(PIXELS)
                            for a, b in zip(here.getpixel((x, PIXELS - 1)),
                                            other.getpixel((x, 0))))
                edge_deltas.append({"orientation": "horizontal", "row": r, "col": c,
                                    "meanRgbChannelDelta": round(delta / (PIXELS * 3), 3)})
    return result, edge_deltas


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", default="terrain-v102/manifest.json")
    parser.add_argument("--output", default="qa/v147-orthophoto-mosaic")
    parser.add_argument("--zoom", type=int, default=17)
    parser.add_argument("--download", action="store_true")
    args = parser.parse_args()
    if not 0 <= args.zoom <= 20:
        parser.error("zoom must be between 0 and 20")
    manifest = plan_grid(json.loads(Path(args.manifest).read_text()), args.zoom)
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    validate_grid(manifest)
    if args.download:
        fetch_images(manifest, output)
        raster, diagnostics = assemble(manifest, output)
        raster.save(output / "geographic-source-mosaic.png", optimize=True)
        manifest["sourceImageSeamDiagnostics"] = diagnostics
        manifest["mosaicFile"] = "geographic-source-mosaic.png"
        manifest["mosaicSha256"] = hashlib.sha256(
            (output / manifest["mosaicFile"]).read_bytes()).hexdigest()
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"V147: {len(manifest['samples'])} adjacent geographic tiles; "
          f"{sum('sha256' in s for s in manifest['samples'])} downloaded; "
          "game route alignment and historical roads NOT certified")


if __name__ == "__main__":
    main()

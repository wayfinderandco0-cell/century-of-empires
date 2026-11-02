#!/usr/bin/env python3
"""V268 Matrei georeferenced 2x2 relief: ONE Copernicus DEM, ONE scene, four crops.

Unapproved geographic art/geometry experiment. No historical roads, water crossing
claims, game routes, or V267 source changes. Requires internet only for the pinned
Copernicus 2021 GLO-30 public AWS DEM; no credentials or paid API.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
from datetime import datetime, timezone
from urllib.request import Request, urlopen

import numpy as np
from PIL import Image, ImageDraw
from pyproj import Transformer
from rasterio import open as raster_open
from rasterio.enums import Resampling
from rasterio.transform import from_origin
from rasterio.warp import reproject
from scipy.ndimage import gaussian_filter
from v267_heightmesh_export import pack_gltf
from v267_relief_materials import paint_tree

COLS, ROWS, TW, TH, MPP, STEP = 2, 2, 1536, 1024, 8, 16
W, H = COLS * TW, ROWS * TH
LAT, LON = 47.1333, 11.4667
TILE = "Copernicus_DSM_COG_10_N47_00_E011_00_DEM"
DEM_URL = "https://copernicus-dem-30m.s3.eu-central-1.amazonaws.com/" + TILE + "/" + TILE + ".tif"
CITATION = ("Copernicus DEM GLO-30 Public 2021; Copernicus WorldDEM-30 "
            "© DLR e.V. 2010–2014 and © Airbus Defence and Space GmbH "
            "2014–2018, provided under COPERNICUS by the European Union and ESA.")
SCHEMA = "coe-v268-matrei-one-source-geographic-pilot/v1"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fetch_dem(cache: Path) -> Path:
    cache.mkdir(parents=True, exist_ok=True)
    target = cache / (TILE + ".tif")
    if target.exists() and target.stat().st_size > 100_000:
        return target
    temp = target.with_suffix(".partial")
    req = Request(DEM_URL, headers={"User-Agent": "COE-V268-geographic-terrain-research/1.0"})
    try:
        with urlopen(req, timeout=90) as response, temp.open("wb") as f:
            if response.status != 200:
                raise RuntimeError("Copernicus HTTP " + str(response.status))
            size = 0
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                size += len(chunk)
                if size > 150_000_000:
                    raise RuntimeError("Unexpected DEM size over 150MB")
                f.write(chunk)
        if temp.stat().st_size < 100_000:
            raise RuntimeError("DEM download truncated")
        temp.replace(target)
    except Exception:
        temp.unlink(missing_ok=True)
        raise
    return target


def build(out: Path, cache: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    dem_file = fetch_dem(cache)
    source_hash = sha(dem_file)
    to_utm = Transformer.from_crs("EPSG:4326", "EPSG:32632", always_xy=True)
    to_geo = Transformer.from_crs("EPSG:32632", "EPSG:4326", always_xy=True)
    center_x, center_y = to_utm.transform(LON, LAT)
    west = center_x - W * MPP / 2
    north = center_y + H * MPP / 2
    transform = from_origin(west, north, MPP, MPP)
    z = np.full((H, W), np.nan, dtype=np.float32)
    with raster_open(dem_file) as src:
        if src.crs is None:
            raise ValueError("DEM lacks source CRS")
        reproject(source=src.read(1), destination=z, src_transform=src.transform,
                  src_crs=src.crs, dst_transform=transform, dst_crs="EPSG:32632",
                  src_nodata=src.nodata, dst_nodata=np.nan,
                  resampling=Resampling.bilinear)
    if not np.isfinite(z).all() or not (350 < float(z.min()) < 3000) or not (500 < float(z.max()) < 4200):
        raise ValueError("Missing or unreasonable measured Matrei DEM coverage")
    # Material and lighting are ONE continuous world-space pass. Vegetation is
    # decorative/UNVERIFIED until modern ESA WorldCover can be sourced.
    gy, gx = np.gradient(z, MPP)
    slope = np.hypot(gx, gy)
    slope_deg = np.rad2deg(np.arctan(slope))
    nx, ny = -gx, -gy
    light = np.clip((.78 * nx - .55 * ny + .90) / np.sqrt(1 + nx * nx + ny * ny), -.8, 1)
    hillshade = np.clip(.68 + .37 * light, .35, 1.1)
    concavity = np.clip((gaussian_filter(z, 19) - z) / 80, 0, 1)
    rock = np.clip((slope_deg - 18) / 32, 0, 1)
    high = np.clip((z - 1650) / 800, 0, 1)
    forest_style = np.clip((2000 - z) / 800, 0, 1) * np.clip((30 - slope_deg) / 20, 0, 1)
    forest_style = gaussian_filter(forest_style, 4)
    yy, xx = np.indices(z.shape)
    # Fine texture is decorative, not a modification to the measured DEM.
    grain = 3.2 * np.sin(xx * .29 + yy * .14) * np.sin(yy * .37 - xx * .19)
    rgb = np.zeros((H, W, 3), dtype=np.float32)
    for i, (grass, woodland, limestone, alpine) in enumerate(zip(
            (119, 130, 79), (58, 94, 60), (154, 151, 137), (178, 171, 156))):
        rgb[..., i] = (grass * (1 - forest_style) + woodland * forest_style) * (1 - rock)
        rgb[..., i] += limestone * rock
        rgb[..., i] = rgb[..., i] * (1 - high * .45) + alpine * high * .45
        rgb[..., i] = rgb[..., i] * hillshade * (1 - concavity * .18) + grain
    scene = Image.fromarray(np.uint8(np.clip(rgb, 0, 255)), "RGB")
    del rgb
    # Reuse V267 foliage drawing but scatter once across the whole world.
    # Placement is visual-only inferred vegetation, not verified landcover.
    rng = np.random.default_rng(2681101)
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    brush = ImageDraw.Draw(overlay, "RGBA")
    trees = []
    for y in range(19, H - 20, 27):
        for x in range(19, W - 20, 27):
            px = int(np.clip(x + rng.integers(-10, 11), 10, W - 11))
            py = int(np.clip(y + rng.integers(-10, 11), 10, H - 11))
            if rng.random() < .68 * float(forest_style[py, px]):
                trees.append((py, px, float(rng.uniform(3.1, 5.0)), float(rng.random())))
    trees.sort()
    for py, px, radius, light_seed in trees:
        paint_tree(brush, py, px, radius, .12, light_seed, 1.0)
    scene = Image.alpha_composite(scene.convert("RGBA"), overlay).convert("RGB")
    del overlay
    # Height, slope and UNKNOWN water state all derive from the same source.
    # No passability certification: 0=blocked/unknown, not a fake clear meadow.
    coarse = z[::STEP, ::STEP].copy()
    z_mesh = np.empty((H // STEP + 1, W // STEP + 1), dtype=np.float32)
    z_mesh[:-1, :-1] = (coarse - float(z.min())) / MPP
    z_mesh[-1, :-1] = (z[-1, ::STEP] - float(z.min())) / MPP
    z_mesh[:-1, -1] = (z[::STEP, -1] - float(z.min())) / MPP
    z_mesh[-1, -1] = (z[-1, -1] - float(z.min())) / MPP
    np.save(out / "heightfield-step16.npy", z_mesh, allow_pickle=False)
    slope8 = Image.fromarray(np.uint8(np.clip(slope_deg / 90 * 255, 0, 255)), "L")
    slope8.resize((W // 4, H // 4), Image.Resampling.BILINEAR).save(out / "slope-degrees-4x.png")
    Image.new("L", (W // 4, H // 4), 0).save(out / "passability-UNVERIFIED.png")
    cells = []
    for row in range(ROWS):
        for col in range(COLS):
            name = "matrei-geo-%d-%d.webp" % (col, row)
            crop = scene.crop((col * TW, row * TH, (col + 1) * TW, (row + 1) * TH))
            crop.save(out / name, "WEBP", quality=86, method=5)
            mesh = pack_gltf(name, z_mesh, out, col, row)
            x0, y0 = west + col * TW * MPP, north - row * TH * MPP
            x1, y1 = x0 + TW * MPP, y0 - TH * MPP
            lon0, lat0 = to_geo.transform(x0, y1)
            lon1, lat1 = to_geo.transform(x1, y0)
            cells.append({
                "id": "matrei-geo-%d-%d" % (col, row),
                "col": col, "row": row,
                "originMeters": [x0, y0],
                "bboxWGS84": [lon0, lat0, lon1, lat1],
                "geoCRS": "EPSG:32632",
                "dimensionsPx": [TW, TH],
                "metersPerPixel": MPP,
                "artWebp": name, "artSha256": sha(out / name),
                "meshGltf": mesh["gltf"], "meshBinary": mesh["binary"],
                "meshSha256": mesh["sha256"],
                "heightfield": "heightfield-step16.npy",
                "passabilityMask": "passability-UNVERIFIED.png",
                "waterMask": None, "verifiedRoadIds": [], "townIds": [],
                "sourceHash": source_hash,
                "visualApproval": False, "gameplayEnabled": False
            })
    # Full-scene is a QA artifact only; the native game uses the four exact crops.
    scene.resize((1536, 1024), Image.Resampling.LANCZOS).save(out / "mosaic-review.webp", "WEBP", quality=83)
    assert len(cells) == 4 and len({c["artSha256"] for c in cells}) == 4
    assert np.array_equal(z_mesh[:, TW // STEP], z_mesh[:, TW // STEP])
    assert np.array_equal(z_mesh[TH // STEP, :], z_mesh[TH // STEP, :])
    manifest = {
        "schema": SCHEMA, "status": "UNAPPROVED_GEOGRAPHIC_3D_CANDIDATES",
        "centerWGS84": [LON, LAT], "centerUTM32": [center_x, center_y],
        "sourceURL": DEM_URL, "sourceRetrievedUTC": datetime.now(timezone.utc).isoformat(),
        "sourceSha256": source_hash, "sourceDataset": "Copernicus DEM GLO-30 Public 2021",
        "sourceCitation": CITATION,
        "sourceLicense": "https://spacedata.copernicus.eu/web/cscda/data-offer/core-datasets",
        "sourceType": "DSM includes vegetation and buildings, not bare-earth historical survey",
        "landcoverSource": None,
        "foliageProvenance": "unverified visual placement using DEM slope/elevation only",
        "waterStatus": "UNKNOWN - not independently sourced or classified",
        "historicalRoadsVerified": 0, "historicalTownsVerified": 0,
        "renderedScenePixels": [W, H], "tilePixels": [TW, TH],
        "metersPerPixel": MPP, "geoCRS": "EPSG:32632",
        "heightfieldSha256": sha(out / "heightfield-step16.npy"),
        "meshUsesSameSourceHeight": True, "geometrySeamOrigin": "one common sampled array",
        "decorativeDiamondGaps": 0, "roadsPainted": 0,
        "baselineApprovedPlayable": 3, "newNativePlayable": 0,
        "userApprovedNew": 0, "finishedToday": 0,
        "cells": cells
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({"cells": 4, "sourceSha256": source_hash,
                      "sourceHeightMin": float(z.min()), "sourceHeightMax": float(z.max()),
                      "treesVisualOnly": len(trees), "newPlayable": 0,
                      "finished": 0}))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--out", type=Path, default=Path("terrain-grid/v268-matrei-geographic"))
    p.add_argument("--cache", type=Path, default=Path("/tmp/coe-v268-dem"))
    args = p.parse_args()
    build(args.out, args.cache)

#!/usr/bin/env python3
"""Build a REAL Alpine waterway network for the V99 proof-of-concept.

HydroRIVERS Europe 1.0, from HydroSHEDS (not Overpass); no guessed river paths.
Raster elevations remain Copernicus GLO-30. Satellite imagery stays online,
not redistributed in the repository. No historic 1780 accuracy is implied.
"""
from __future__ import annotations
import json
import os
import tempfile
import zipfile
from pathlib import Path
import requests
import fiona

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "terrain-v99"
OUT.mkdir(exist_ok=True)
BOUNDS = (11.26, 46.80, 11.80, 47.42)
WEST, SOUTH, EAST, NORTH = BOUNDS
DATA_URL = "https://data.hydrosheds.org/file/HydroRIVERS/HydroRIVERS_v10_eu_shp.zip"
ARCHIVE = OUT / "_rivers_europe.zip"

if not ARCHIVE.exists():
    print("Downloading HydroRIVERS Europe ZIP; no local stream extrapolation", flush=True)
    with requests.get(DATA_URL, stream=True, timeout=(30, 170)) as result:
        result.raise_for_status()
        with ARCHIVE.open("wb") as dest:
            for piece in result.iter_content(chunk_size=1 << 20):
                if piece: dest.write(piece)
if ARCHIVE.stat().st_size < 10_000_000:
    raise RuntimeError("HydroRIVERS ZIP unexpectedly small")

with tempfile.TemporaryDirectory() as tmp:
    with zipfile.ZipFile(ARCHIVE) as z:
        entries = [n for n in z.namelist() if n.lower().endswith((".shp", ".shx", ".dbf", ".prj"))]
        if not any(e.lower().endswith(".shp") for e in entries):
            raise RuntimeError("Missing HydroRIVERS shapefile")
        for name in entries: z.extract(name, tmp)
        shp_name = next(e for e in entries if e.lower().endswith(".shp"))
    shape_path = os.path.join(tmp, shp_name)
    print("Filtering river geometry by target bounds", BOUNDS, flush=True)
    features = []
    with fiona.open(shape_path, "r") as dataset:
        print("HydroRIVERS columns", list(dataset.schema['properties']), flush=True)
        for feature in dataset.filter(bbox=BOUNDS):
            geom = feature.get("geometry")
            if not geom: continue
            g = dict(geom)
            segments = []
            if g["type"] == "LineString":
                segments = [g["coordinates"]]
            elif g["type"] == "MultiLineString":
                segments = g["coordinates"]
            props = dict(feature["properties"])
            for points in segments:
                coords = [[round(float(x), 6),round(float(y),6)] for x,y,*_ in points]
                if len(coords) < 2: continue
                if not any(WEST < x < EAST and SOUTH < y < NORTH for x,y in coords):continue
                # Measurements are from the source; no random polylines.
                features.append({
                    "coordinates": coords[::2] + coords[-1:] if len(coords) > 800 else coords,
                    "order": int(props.get("ORD_STRA") or 1),
                    "flow": float(props.get("DIS_AV_CMS") or 0),
                    "reachId": str(props.get("HYRIV_ID") or "")
                })
print("Verified HydroRIVERS reaches:", len(features), flush=True)
if len(features) < 20:
    raise RuntimeError("Insufficient actual waterways for this region: " + str(len(features)))

result = {
    "source": "HydroRIVERS v1.0 Europe, derived from HydroSHEDS 15 arc-second hydrography",
    "licence": "HydroSHEDS license; scientific/educational/commercial availability subject to source terms",
    "boundsLonLat": list(BOUNDS),
    "count": len(features),
    "features": features
}
(OUT / "hydrorivers.json").write_text(json.dumps(result, separators=(",", ":")))
(OUT / "manifest.json").write_text(json.dumps({
    "riverFeatures": len(features), "riverSource": result["source"],
    "topography": "Copernicus GLO-30 regional overlay inherited from V97",
    "canopyView": "Live satellite/aerial imagery in close-up, attributed to Esri and its imagery providers",
    "disclaimer": "Modern geographic observations; not reconstructed 1780 vegetation or watercourses"
}, indent=2) + "\n")
ARCHIVE.unlink()
print("V99 hydrography assets verified", flush=True)

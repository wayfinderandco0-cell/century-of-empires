#!/usr/bin/env python3
"""V197: source-derived high-resolution Alpine vegetation/rock MATERIAL candidates.

These are modern orthophotos for ART REFERENCE, not geographically registered
WEST/MATREI/SOUTH game octagons. Never overlay the 1780 map automatically.
No modern road, roof, railway or snow/no-data exclusion has been certified.
"""
import argparse
import hashlib
import io
import json
import math
import time
from pathlib import Path
from urllib.error import URLError, HTTPError
from urllib.request import Request, urlopen

from PIL import Image, ImageDraw
import v184_matrei_brenner_overview as v184

ZOOM = 18
TILE = 256
PATCH = 512
# Native V184 EPSG:3857 overview pixel coordinates, visually selected on the
# actual 60-tile source, NOT V123 game/world or surveyed historic coordinates.
SITES = (
    ("western_forest_reference", 170, 1020),
    ("eastern_ridge_reference", 1040, 820),
    ("southern_forest_reference", 380, 2350),
)
FALSE_FLAGS = (
    "v121ToGeographyRegistered", "v123RoadsGeoregistered",
    "gameOctagonsGeoregistered", "modernInfrastructureExcluded",
    "historicalRoadsVerified", "bridgeBanksVerified", "periodArtComplete",
    "physicalIPhoneApproved", "productionApproved",
)

def require(ok, why):
    if not ok:
        raise ValueError(why)

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def tile_bounds(x, y):
    n = 1 << ZOOM
    def lat(row):
        return math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * row / n))))
    return [x/n*360-180, lat(y+2), (x+2)/n*360-180, lat(y)]

def plan():
    base = v184.plan()
    x0, y0, z0 = base["tileOriginXYZ"]
    require(z0 == 14 and base["gridTiles"] == [5, 12], "V184 origin changed")
    samples = []
    for name, x, y in SITES:
        require(0 < x < 1280 and 0 < y < 2560, "outside observed Austrian source")
        cx = (x0 + x/TILE) * (1 << (ZOOM-z0))
        cy = (y0 + y/TILE) * (1 << (ZOOM-z0))
        ox, oy = math.floor(cx - .5), math.floor(cy - .5)
        tiles = []
        for row in range(2):
            for col in range(2):
                tx, ty = ox+col, oy+row
                tiles.append({
                    "name": f"{name}-r{row}c{col}.jpeg",
                    "row": row, "col": col, "tileXYZ": [tx, ty, ZOOM],
                    "url": f"{v184.BASE}/{ZOOM}/{ty}/{tx}.jpeg",
                })
        samples.append({
            "name": name,
            "overviewPixelXY": [x, y],
            "nativeOriginXYZ": [ox, oy, ZOOM],
            "footprintLonLat": tile_bounds(ox, oy),
            "image": f"{name}.png",
            "tiles": tiles,
        })
    all_xyz = [tuple(t["tileXYZ"]) for s in samples for t in s["tiles"]]
    require(len(all_xyz) == 12 and len(set(all_xyz)) == 12, "source patches overlap")
    return {
        "version": 197,
        "purpose": "Modern geographically anchored high-res MATERIAL study, not 1780 GAME octagons",
        "parentSource": "V184 basemap.at EPSG:3857 60-tile Austrian overview",
        "parentGridOriginXYZ": base["tileOriginXYZ"],
        "crs": "EPSG:3857",
        "zoom": ZOOM,
        "nativeTilePixels": TILE,
        "materialPatchPixels": [PATCH, PATCH],
        "materialPatchCount": 3,
        "provider": base["provider"],
        "license": base["license"],
        "requiredAttribution": base["requiredAttribution"],
        "sourceUrl": base["sourceUrl"],
        "notGameOctagonCenters": True,
        "modernSourceYearsNot1780Evidence": True,
        "naturalCoverRequiresManualReview": True,
        "modernRoadRailRoofMaskNotCertified": True,
        "samples": samples,
        **{k: False for k in FALSE_FLAGS},
    }

def validate(m):
    expected = plan()
    require(set(m) - set(expected) <= {"contactSheet", "contactSheetSha256"},
            "unexpected top-level metadata")
    for k, v in expected.items():
        if k == "samples":
            continue
        require(m.get(k) == v, "source/provenance/approval altered: " + k)
    require(len(m.get("samples", [])) == 3, "three independent samples required")
    for got, src in zip(m["samples"], expected["samples"]):
        require(set(got)-set(src) <= {"imageSha256", "reviewMetrics"},
                "unexpected sample metadata")
        for k, v in src.items():
            if k == "tiles":
                require(len(got.get("tiles", [])) == 4, "four source tiles required")
                for tile, original in zip(got["tiles"], v):
                    require(set(tile)-set(original) <= {"sha256", "byteCount"},
                            "unexpected tile metadata")
                    for field, value in original.items():
                        require(tile.get(field) == value, "tile identity changed")
            else:
                require(got.get(k) == v, "source sample altered: " + k)
    return True

def download(m, folder):
    validate(m)
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    for sample in m["samples"]:
        for tile in sample["tiles"]:
            req = Request(tile["url"], headers={"User-Agent": "CenturyOfEmpires-SourceMaterialAudit/1.0"})
            for attempt in range(4):
                try:
                    with urlopen(req, timeout=30) as response:
                        data = response.read(1500001)
                        mime = response.headers.get("Content-Type", "")
                    break
                except (URLError, TimeoutError, HTTPError):
                    if attempt == 3:
                        raise
                    time.sleep(2*(attempt+1))
            require(500 < len(data) <= 1500000 and data.startswith(b"\xff\xd8")
                    and "image" in mime.lower(), "source not native JPEG")
            with Image.open(io.BytesIO(data)) as im:
                require(im.format == "JPEG" and im.size == (TILE, TILE),
                        "wrong high-resolution native tile")
                im.verify()
            target = folder/tile["name"]
            target.write_bytes(data)
            tile["sha256"] = hashlib.sha256(data).hexdigest()
            tile["byteCount"] = len(data)

def assemble(sample, folder):
    canvas = Image.new("RGB", (PATCH, PATCH))
    for tile in sample["tiles"]:
        target = Path(folder)/tile["name"]
        require(target.is_file() and tile.get("sha256") == sha(target)
                and tile.get("byteCount") == target.stat().st_size,
                "missing or modified native JPEG: " + tile["name"])
        with Image.open(target) as im:
            require(im.format == "JPEG" and im.size == (TILE, TILE),
                    "invalid native tile")
            canvas.paste(im.convert("RGB"), (tile["col"]*TILE, tile["row"]*TILE))
    return canvas

def metrics(im):
    rgb = im.convert("RGB")
    p = rgb.load()
    # Descriptive only: neither pixel variation nor color proves natural cover.
    nearwhite = 0
    total = 0
    differences = 0
    for y in range(0, PATCH-2, 4):
        for x in range(0, PATCH-2, 4):
            a = p[x,y]
            nearwhite += min(a) >= 248 and max(a)-min(a) <= 7
            b, c = p[x+1,y], p[x,y+1]
            differences += sum(abs(a[i]-b[i])+abs(a[i]-c[i]) for i in range(3))
            total += 1
    return {
        "nearWhiteFractionSampled": round(nearwhite/total, 5),
        "meanAdjacentRGBDelta": round(differences/(total*6), 4),
        "naturalCoverVerified": False,
        "modernInfrastructureExcluded": False,
        "periodSafe": False,
    }

def produce(m, folder):
    validate(m)
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    contact = Image.new("RGB", (PATCH*3, PATCH+42), (17,32,27))
    draw = ImageDraw.Draw(contact)
    all_hashes = []
    for index, sample in enumerate(m["samples"]):
        image = assemble(sample, folder)
        path = folder/sample["image"]
        image.save(path)
        sample["imageSha256"] = sha(path)
        sample["reviewMetrics"] = metrics(image)
        contact.paste(image, (index*PATCH, 0))
        draw.text((index*PATCH+8, PATCH+6), sample["name"], fill=(240,227,201))
        all_hashes.append(sample["imageSha256"])
    require(len(set(all_hashes)) == 3, "duplicate source material patch")
    m["contactSheet"] = "modern-source-material-contact-sheet.png"
    contact.save(folder/m["contactSheet"])
    m["contactSheetSha256"] = sha(folder/m["contactSheet"])
    (folder/"manifest.json").write_text(json.dumps(m, indent=2)+"\n")
    verify(folder)
    return m

def verify(folder):
    folder = Path(folder)
    m = json.loads((folder/"manifest.json").read_text())
    validate(m)
    contact = Image.new("RGB", (PATCH*3, PATCH+42), (17,32,27))
    draw = ImageDraw.Draw(contact)
    for index, sample in enumerate(m["samples"]):
        image = assemble(sample, folder)
        require(sample.get("reviewMetrics") == metrics(image),
                "review metrics altered")
        target = folder/sample["image"]
        require(target.is_file() and sample.get("imageSha256") == sha(target),
                "material PNG hash mismatch")
        with Image.open(target) as stored:
            require(stored.size == image.size and stored.convert("RGB").tobytes()
                    == image.tobytes(), "material pixels changed")
        contact.paste(image, (index*PATCH,0))
        draw.text((index*PATCH+8, PATCH+6), sample["name"], fill=(240,227,201))
    target = folder/"modern-source-material-contact-sheet.png"
    require(m.get("contactSheet") == target.name
            and target.is_file() and m.get("contactSheetSha256") == sha(target),
            "contact sheet identity changed")
    with Image.open(target) as stored:
        require(stored.convert("RGB").tobytes() == contact.tobytes(),
                "contact sheet pixels altered")
    return True

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="qa/v197-highres-source-materials")
    parser.add_argument("--download", action="store_true")
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    folder = Path(args.output)
    if args.verify:
        verify(folder)
    elif args.download:
        m = plan()
        download(m, folder)
        produce(m, folder)
    else:
        folder.mkdir(parents=True, exist_ok=True)
        (folder/"manifest.json").write_text(json.dumps(plan(), indent=2)+"\n")
    print("V197 modern high-resolution SOURCE reference only; three GAME octagons NOT approved")

if __name__ == "__main__":
    main()

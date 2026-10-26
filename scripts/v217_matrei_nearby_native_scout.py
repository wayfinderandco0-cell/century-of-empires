#!/usr/bin/env python3
"""V217: scout nine NATIVE modern aerial source patches near Matrei reference.

Not a V123 coordinate registration, 1780 landscape, or playable terrain.
Patches are deliberately DISCONTIGUOUS; never stitch them into a fake atlas.
"""
import argparse
import hashlib
import io
import json
import math
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from PIL import Image, ImageDraw
import v204_contiguous_matrei_sources as v204

ROOT = Path(__file__).resolve().parents[1]
OFFSETS = tuple((dx, dy) for dy in (-8, 0, 8) for dx in (-8, 0, 8))
SIDE = 512
GAP = 32
HEADER = 78
LABEL = 45
FOOTER = 90
FLAGS = ("registeredToV121", "registeredToV123", "historicalRoadsVerified",
         "modernFeaturesExcluded", "periodSafe", "gameArtApproved",
         "physicalIPhoneApproved", "productionApproved", "sourcePatchesContiguous")

def require(condition, message):
    if not condition:
        raise ValueError(message)

def sha(data):
    return hashlib.sha256(data).hexdigest()

def plan():
    lon, lat = v204.ANCHORS["matrei"][0]
    fx, fy = v204.xyz(lon, lat)
    x0, y0 = math.floor(fx) - 1, math.floor(fy) - 1
    sites = []
    used = set()
    for i, (dx, dy) in enumerate(OFFSETS):
        x, y = x0 + dx, y0 + dy
        tiles = []
        for row in range(2):
            for col in range(2):
                tx, ty = x + col, y + row
                require((tx, ty) not in used, "candidate native tiles overlap")
                used.add((tx, ty))
                tiles.append({"xyz": [tx, ty, 18],
                              "name": f"candidate-{i:02d}-r{row}c{col}.jpeg",
                              "url": f"{v204.BASE}/18/{ty}/{tx}.jpeg"})
        sites.append({"id": f"site-{i:02d}", "offsetNativeTiles": [dx, dy],
                      "nativeOriginXYZ": [x, y, 18],
                      "footprintLonLat": v204.footprint(x, y),
                      "sourceImage": f"site-{i:02d}.png", "tiles": tiles})
    return {
        "version": 217, "sitePurpose": "Native modern source scouting, not a game atlas",
        "anchorLonLat": [lon, lat], "anchorSource": v204.ANCHORS["matrei"][1],
        "projection": "EPSG:3857", "zoom": 18, "nativeTilePixels": 256,
        "nativePatchPixels": [SIDE, SIDE],
        "geographicGapsBetweenSites": True, "siteGridOffsetsNativeTiles": [list(x) for x in OFFSETS],
        "sourceProvider": "basemap.at", "sourceLicense": "CC BY 4.0",
        "attribution": "Datenquelle: basemap.at", "sourceUrl": "https://basemap.at/orthofoto/",
        "modernRoadsBuildingsDateImprintsMayRemain": True,
        "sites": sites, **{f: False for f in FLAGS},
    }

def verify_plan(manifest):
    expected = plan()
    require(set(manifest) == set(expected) | {"contactFile", "contactSha256"},
            "manifest has missing or unauthorized fields")
    for key in expected:
        if key == "sites":
            continue
        require(manifest[key] == expected[key], "altered geographic/approval metadata: " + key)
    require(len(manifest["sites"]) == 9, "nine geographic sites required")
    for actual, pinned in zip(manifest["sites"], expected["sites"]):
        require(set(actual) == set(pinned) | {"imageSha256"}, "site fields changed")
        for key in pinned:
            if key == "tiles":
                continue
            require(actual[key] == pinned[key], "site identity changed: " + key)
        require(len(actual["tiles"]) == 4, "four native tiles per site")
        for got, ref in zip(actual["tiles"], pinned["tiles"]):
            require(set(got) == set(ref) | {"sha256", "byteCount"}, "tile fields changed")
            for key in ref:
                require(got[key] == ref[key], "source XYZ/URL identity changed: " + key)
    return True

def native_jpeg(data):
    require(len(data) > 500 and data[:2] == b"\xff\xd8",
            "native JPEG required")
    with Image.open(io.BytesIO(data)) as im:
        require(im.format == "JPEG" and im.size == (256, 256),
                "wrong native image dimensions")
        im.verify()

def download(folder, manifest):
    folder.mkdir(parents=True, exist_ok=True)
    for site in manifest["sites"]:
        for tile in site["tiles"]:
            req = Request(tile["url"], headers={"User-Agent": "CenturyOfEmpires-SourceScout/1.0"})
            for attempt in range(4):
                try:
                    with urlopen(req, timeout=35) as response:
                        data = response.read(1500001)
                        mime = response.headers.get("Content-Type", "")
                    require("image" in mime.lower() and len(data) <= 1500000,
                            "source not a JPEG response")
                    native_jpeg(data)
                    break
                except (HTTPError, URLError, TimeoutError):
                    if attempt == 3:
                        raise
                    time.sleep(2 * (attempt + 1))
            (folder / tile["name"]).write_bytes(data)
            tile["sha256"] = sha(data)
            tile["byteCount"] = len(data)

def assemble(site, folder):
    image = Image.new("RGB", (SIDE, SIDE))
    for i, tile in enumerate(site["tiles"]):
        data = (folder / tile["name"]).read_bytes()
        require(sha(data) == tile.get("sha256") and
                len(data) == tile.get("byteCount"), "source JPEG changed: " + tile["name"])
        native_jpeg(data)
        with Image.open(io.BytesIO(data)) as src:
            image.paste(src.convert("RGB"), ((i % 2) * 256, (i // 2) * 256))
    return image

def contact(manifest, folder):
    width = SIDE * 3 + GAP * 2
    height = HEADER + (SIDE + LABEL + GAP) * 3 + FOOTER
    out = Image.new("RGB", (width, height), (19, 30, 27))
    d = ImageDraw.Draw(out)
    d.text((12, 12), "V217: NATIVE MODERN MATREI-AREA SOURCE SCOUT / NOT GAME ART",
           fill=(255, 225, 176))
    d.text((12, 34), "9 separate geographic patches; DARK GAPS = UNSAMPLED AREA (NOT a continuous atlas)",
           fill=(224, 223, 202))
    d.text((12, 55), "Modern infrastructure, dates and buildings NOT excluded; no historical road or V123 match",
           fill=(224, 223, 202))
    for i, site in enumerate(manifest["sites"]):
        row, col = divmod(i, 3)
        x = col * (SIDE + GAP)
        y = HEADER + row * (SIDE + LABEL + GAP)
        patch = assemble(site, folder)
        out.paste(patch, (x, y))
        site["imageSha256"] = sha((folder / site["sourceImage"]).read_bytes())
        lon0, lat0, lon1, lat1 = site["footprintLonLat"]
        d.text((x + 5, y + SIDE + 7),
               f"{site['id']} | {site['offsetNativeTiles']} tiles | {lon0:.5f}E {lat1:.5f}N",
               fill=(255, 226, 171))
        d.text((x + 5, y + SIDE + 23), "Modern 2023 source / NOT V123 coordinates",
               fill=(205, 211, 195))
    d.text((12, height - 66), "Native 512x512 RGB, never resampled or filled; candidate labels are source locations only",
           fill=(240, 223, 189))
    d.text((12, height - 42), "Datenquelle: basemap.at | CC BY 4.0 | NOT a verified 1780 landscape",
           fill=(240, 223, 189))
    return out

def build(folder):
    v204.verify_source_invariants("matrei")
    manifest = plan()
    download(folder, manifest)
    for site in manifest["sites"]:
        image = assemble(site, folder)
        image.save(folder / site["sourceImage"])
    image = contact(manifest, folder)
    image.save(folder / "matrei-nearby-native-contact.png")
    manifest["contactFile"] = "matrei-nearby-native-contact.png"
    manifest["contactSha256"] = sha((folder / manifest["contactFile"]).read_bytes())
    (folder / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    verify(folder)

def verify(folder):
    manifest = json.loads((folder / "manifest.json").read_text())
    verify_plan(manifest)
    for site in manifest["sites"]:
        expected = assemble(site, folder)
        with Image.open(folder / site["sourceImage"]) as stored:
            require(stored.mode == "RGB" and stored.size == (SIDE, SIDE)
                    and stored.tobytes() == expected.tobytes(),
                    "native candidate pixels changed")
        require(sha((folder / site["sourceImage"]).read_bytes()) == site["imageSha256"],
                "candidate image hash changed")
    expected_contact = contact(manifest, folder)
    path = folder / manifest["contactFile"]
    require(sha(path.read_bytes()) == manifest["contactSha256"], "contact hash changed")
    with Image.open(path) as actual:
        require(actual.mode == "RGB" and actual.size == expected_contact.size
                and actual.tobytes() == expected_contact.tobytes(),
                "source scout contact changed")
    return True

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "qa/v217-matrei-nearby")
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    if args.verify:
        verify(args.output)
    else:
        build(args.output)
    print("V217 nine native modern Matrei-area patches verified; NO game or historical approval")

if __name__ == "__main__":
    main()

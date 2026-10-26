#!/usr/bin/env python3
"""V204: native, CONTIGUOUS modern Matrei-area aerial SOURCE grid.

Three geographically adjoining 512px reference panels, NEVER the V123 game
octagons. Real EPSG:3857 XYZ coordinates and unmodified source pixels.
Modern buildings, roads and date marks are NOT period-safe game artwork.
"""
import argparse
import hashlib
import io
import json
import math
import subprocess
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
ZOOM, TILE, SIDE = 18, 256, 2
PATCH = TILE * SIDE
ANCHOR = (11.45306, 47.13083)  # V180 modern Matrei-area geographic anchor
BASE = "https://mapsneu.wien.gv.at/basemap/bmaporthofoto30cm/normal/google3857"
PINNED = {
    "v121-octagon-1-painted-road.html": "4c6aa5cda9e7c359b6d2a49d5b5fe8a597346382",
    "terrain-grid/v123-atlas.js": "09f04b4062e24fbacbb645307462cdddce2b2aa3",
}
FALSE_FLAGS = (
    "sourcePanelsAreGameOctagons", "v121PhotoGeoregistered",
    "v123RoadsGeoregistered", "modernFeaturesFullyExcluded",
    "periodSafe", "historicRoadsVerified", "bridgeBanksVerified",
    "gameArtApproved", "physicalIPhoneApproved", "productionApproved",
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def xyz(lon, lat):
    require(-180 < lon < 180 and -85 < lat < 85, "invalid geographic anchor")
    n = 1 << ZOOM
    return ((lon + 180) / 360 * n,
            (1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n)


def footprint(x, y, span=SIDE):
    n = 1 << ZOOM
    latitude = lambda row: math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * row / n))))
    return [x / n * 360 - 180, latitude(y + span),
            (x + span) / n * 360 - 180, latitude(y)]


def plan():
    fx, fy = xyz(*ANCHOR)
    # The anchor lies within the central 2x2 source panel.
    x0, y0 = math.floor(fx) - 1, math.floor(fy) - 1
    require(x0 < fx < x0 + SIDE and y0 < fy < y0 + SIDE, "anchor outside central panel")
    panels = []
    for name, dx, dy, px, py in (
        ("west_reference", -2, 0, 0, 0),
        ("matrei_reference", 0, 0, PATCH, 0),
        ("south_reference", 0, 2, PATCH, PATCH),
    ):
        ox, oy = x0 + dx, y0 + dy
        tiles = []
        for row in range(SIDE):
            for col in range(SIDE):
                tx, ty = ox + col, oy + row
                tiles.append({
                    "name": f"{name}-r{row}c{col}.jpeg",
                    "tileXYZ": [tx, ty, ZOOM], "row": row, "col": col,
                    "url": f"{BASE}/{ZOOM}/{ty}/{tx}.jpeg",
                })
        panels.append({
            "name": name, "nativeOriginXYZ": [ox, oy, ZOOM],
            "footprintLonLat": footprint(ox, oy),
            "pixelOriginInContact": [px, py],
            "sourceImage": name + ".png",
            "tiles": tiles,
        })
    w, m, s = panels
    require(w["nativeOriginXYZ"][0] + SIDE == m["nativeOriginXYZ"][0]
            and w["nativeOriginXYZ"][1] == m["nativeOriginXYZ"][1],
            "WEST and MATREI native panels do not share a full edge")
    require(m["nativeOriginXYZ"][1] + SIDE == s["nativeOriginXYZ"][1]
            and m["nativeOriginXYZ"][0] == s["nativeOriginXYZ"][0],
            "MATREI and SOUTH native panels do not share a full edge")
    require(abs(w["footprintLonLat"][2] - m["footprintLonLat"][0]) < 1e-11
            and abs(m["footprintLonLat"][1] - s["footprintLonLat"][3]) < 1e-11,
            "geographic footprint edges are not exactly contiguous")
    ids = [tuple(t["tileXYZ"]) for p in panels for t in p["tiles"]]
    require(len(ids) == len(set(ids)) == 12, "source XYZ tiles overlap or are missing")
    return {
        "version": 204, "purpose": "Contiguous modern Alpine SOURCE geometry; NOT V123 GAME geography",
        "anchorLonLat": list(ANCHOR), "anchorSource": "V180 independent modern Matrei-area reference",
        "projection": "EPSG:3857", "nativeZoom": ZOOM,
        "nativeTilePixels": TILE, "sourcePanelPixels": [PATCH, PATCH],
        "contactLayout": "L: WEST at top-left, MATREI at top-right, SOUTH at bottom-right; southwest unfilled",
        "sourcePanelsGeographicallyContiguous": True,
        "sourcePanelsNotRegisteredToV121V123": True,
        "modernInfrastructureAndDateMarksMayRemain": True,
        "noHistoricalRouteOr1780VegetationInference": True,
        "v97DemResolutionTooCoarseToVerifyBridgeBanks": True,
        "provider": "basemap.at", "license": "CC BY 4.0",
        "requiredAttribution": "Datenquelle: basemap.at",
        "sourceUrl": "https://basemap.at/orthofoto/",
        "panels": panels, **{key: False for key in FALSE_FLAGS},
    }


def validate(manifest):
    expected = plan()
    require(set(manifest) - set(expected) <= {"contactImage", "contactSha256", "seamDiagnostics"},
            "unexpected top-level manifest fields")
    for key, value in expected.items():
        if key != "panels":
            require(manifest.get(key) == value, "altered source geometry or approval: " + key)
    got_panels = manifest.get("panels", [])
    require(len(got_panels) == 3, "three source reference panels required")
    for got, expected_panel in zip(got_panels, expected["panels"]):
        require(set(got) - set(expected_panel) <= {"sourceSha256", "nearWhiteFraction"},
                "unexpected panel metadata")
        for key, value in expected_panel.items():
            if key != "tiles":
                require(got.get(key) == value, "panel identity changed: " + key)
        require(len(got.get("tiles", [])) == 4, "source panel missing native tiles")
        for tile, expected_tile in zip(got["tiles"], expected_panel["tiles"]):
            require(set(tile) - set(expected_tile) <= {"sha256", "byteCount"},
                    "unexpected tile metadata")
            for key, value in expected_tile.items():
                require(tile.get(key) == value, "source tile identity changed: " + key)
    return True


def verify_source_invariants():
    for path, expected in PINNED.items():
        actual = subprocess.check_output(["git", "hash-object", path],
                                         cwd=ROOT, text=True).strip()
        require(actual == expected, "immutable V121/V123 changed: " + path)
    v97 = json.loads((ROOT / "terrain-v97/manifest.json").read_text())
    v102 = json.loads((ROOT / "terrain-v102/manifest.json").read_text())
    v94 = json.loads((ROOT / "terrain-v94/manifest.json").read_text())
    require(v97["boundsLonLat"] == v102["broadBoundsLonLat"]
            == [11.26, 46.8, 11.8, 47.42], "V97/V102 relief frame changed")
    require(v94["projection"] == "equirectangular"
            and v94["extent"] == [-14.0, 26.0, 49.0, 75.0],
            "V94 Europe atlas projection changed")
    lon, lat = ANCHOR
    require(v97["boundsLonLat"][0] < lon < v97["boundsLonLat"][2]
            and v97["boundsLonLat"][1] < lat < v97["boundsLonLat"][3],
            "source anchor outside geographic relief coverage")


def download(manifest, folder):
    validate(manifest)
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    for panel in manifest["panels"]:
        for tile in panel["tiles"]:
            request = Request(tile["url"], headers={"User-Agent": "CenturyOfEmpires-ModernSourceAudit/1.0"})
            for attempt in range(4):
                try:
                    with urlopen(request, timeout=30) as response:
                        data = response.read(1500001)
                        mime = response.headers.get("Content-Type", "")
                    require(500 < len(data) <= 1500000
                            and data[:2] == b"\xff\xd8" and "image" in mime.lower(),
                            "not a native JPEG: " + tile["name"])
                    with Image.open(io.BytesIO(data)) as im:
                        require(im.format == "JPEG" and im.size == (TILE, TILE),
                                "unexpected native source dimensions")
                        im.verify()
                    break
                except (HTTPError, URLError, TimeoutError):
                    if attempt == 3:
                        raise
                    time.sleep(2 * (attempt + 1))
            target = folder / tile["name"]
            target.write_bytes(data)
            tile["sha256"] = sha(target)
            tile["byteCount"] = len(data)


def assemble(panel, folder):
    canvas = Image.new("RGB", (PATCH, PATCH))
    for tile in panel["tiles"]:
        target = Path(folder) / tile["name"]
        require(target.is_file() and tile.get("sha256") == sha(target)
                and tile.get("byteCount") == target.stat().st_size,
                "native source missing or altered: " + tile["name"])
        with Image.open(target) as im:
            require(im.format == "JPEG" and im.size == (TILE, TILE),
                    "invalid source JPEG: " + tile["name"])
            canvas.paste(im.convert("RGB"), (tile["col"] * TILE, tile["row"] * TILE))
    return canvas


def seam_mean(a, b, direction):
    if direction == "vertical":
        first = [a.getpixel((PATCH - 1, y)) for y in range(PATCH)]
        second = [b.getpixel((0, y)) for y in range(PATCH)]
    else:
        first = [a.getpixel((x, PATCH - 1)) for x in range(PATCH)]
        second = [b.getpixel((x, 0)) for x in range(PATCH)]
    return round(sum(abs(u - v) for p, q in zip(first, second)
                     for u, v in zip(p, q)) / (PATCH * 3), 4)


def near_white_fraction(image):
    pixels = image.load()
    count = 0
    for y in range(0, PATCH, 4):
        for x in range(0, PATCH, 4):
            r, g, b = pixels[x, y]
            count += min(r, g, b) >= 248 and max(r, g, b) - min(r, g, b) <= 7
    return round(count / ((PATCH // 4) ** 2), 5)


def render(manifest, folder):
    validate(manifest)
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    images = {}
    contact = Image.new("RGB", (PATCH * 2, PATCH * 2 + 62), (18, 34, 28))
    for panel in manifest["panels"]:
        img = assemble(panel, folder)
        images[panel["name"]] = img
        target = folder / panel["sourceImage"]
        img.save(target)
        panel["sourceSha256"] = sha(target)
        panel["nearWhiteFraction"] = near_white_fraction(img)
        require(panel["nearWhiteFraction"] < .60,
                "majority blank source imagery; cannot present this as high-res coverage")
        contact.paste(img, tuple(panel["pixelOriginInContact"]))
    draw = ImageDraw.Draw(contact)
    draw.text((8, PATCH + 10), "SW NOT SAMPLED: no invented geography", fill="#f0d5a1")
    draw.text((8, PATCH * 2 + 8), "MODERN contiguous SOURCE ONLY; not the V123 octagons or a 1780 road survey",
              fill="#fff0ce")
    draw.text((8, PATCH * 2 + 28), "Datenquelle: basemap.at | CC BY 4.0 | original RGB source panels unchanged",
              fill="#fff0ce")
    manifest["seamDiagnostics"] = {
        "westToMatreiMeanAbsRGB": seam_mean(images["west_reference"],
                                           images["matrei_reference"], "vertical"),
        "matreiToSouthMeanAbsRGB": seam_mean(images["matrei_reference"],
                                           images["south_reference"], "horizontal"),
        "diagnosticOnly": True, "gameRoadOrPhotoSeamVerified": False,
    }
    manifest["contactImage"] = "modern-contiguous-reference-contact.png"
    contact.save(folder / manifest["contactImage"])
    manifest["contactSha256"] = sha(folder / manifest["contactImage"])
    (folder / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    verify(folder)
    return manifest


def verify(folder):
    folder = Path(folder)
    manifest = json.loads((folder / "manifest.json").read_text())
    validate(manifest)
    images = {}
    for panel in manifest["panels"]:
        rebuilt = assemble(panel, folder)
        stored = folder / panel["sourceImage"]
        require(stored.is_file() and panel.get("sourceSha256") == sha(stored),
                "source panel hash changed")
        with Image.open(stored) as im:
            require(im.size == rebuilt.size and im.convert("RGB").tobytes() == rebuilt.tobytes(),
                    "source pixels were altered")
        require(panel.get("nearWhiteFraction") == near_white_fraction(rebuilt),
                "source coverage metric altered")
        images[panel["name"]] = rebuilt
    expected = {
        "westToMatreiMeanAbsRGB": seam_mean(images["west_reference"],
                                           images["matrei_reference"], "vertical"),
        "matreiToSouthMeanAbsRGB": seam_mean(images["matrei_reference"],
                                           images["south_reference"], "horizontal"),
        "diagnosticOnly": True, "gameRoadOrPhotoSeamVerified": False,
    }
    require(manifest.get("seamDiagnostics") == expected, "source seam report altered")
    contact = folder / "modern-contiguous-reference-contact.png"
    require(manifest.get("contactImage") == contact.name and contact.is_file()
            and manifest.get("contactSha256") == sha(contact), "source contact identity changed")
    with Image.open(contact) as im:
        require(im.size == (PATCH * 2, PATCH * 2 + 62), "contact dimensions changed")
        for panel in manifest["panels"]:
            x, y = panel["pixelOriginInContact"]
            require(im.crop((x, y, x + PATCH, y + PATCH)).convert("RGB").tobytes()
                    == images[panel["name"]].tobytes(),
                    "source pixels modified inside contact sheet")
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "qa/v204-contiguous-matrei-source")
    parser.add_argument("--download", action="store_true")
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    verify_source_invariants()
    if args.verify:
        verify(args.output)
    elif args.download:
        manifest = plan()
        download(manifest, args.output)
        render(manifest, args.output)
    else:
        args.output.mkdir(parents=True, exist_ok=True)
        (args.output / "manifest.json").write_text(json.dumps(plan(), indent=2) + "\n")
    print("V204 source geography only; V123 GAME registration, historic roads and art approval FALSE")


if __name__ == "__main__":
    main()

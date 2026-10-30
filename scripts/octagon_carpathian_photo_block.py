#!/usr/bin/env python3
"""Eight source-native Carpathian autumn forest photo cells, quarantined from gameplay.

One continuous 4x2 native-pixel crop from a licensed 8000x2763 Carpathian
forest drone panorama. All ten internal seams are original adjacent pixels. Never invent road ports or historical settlements.
No road or historical province is inferred from photographic adjacency. Original photos are
retrieved from Commons at build time; only durable derived art is committed.
"""
from __future__ import annotations
from io import BytesIO
import hashlib, html, json, re, urllib.parse, urllib.request, time
from pathlib import Path
from PIL import Image, ImageEnhance, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "terrain-grid/factory-photo/carpathian-8"
W, H, X0, Y0 = 1536, 1024, 10, 12
SOURCES = (
    {"title": "Осінній ліс в хмарах туману.jpg", "cols": 4, "x": 900, "y": 700,
     "motif": "Carpathian forest canopy, mist and wooded mountain slopes"},
)
USER_AGENT = "CenturyOfEmpiresArtFactory/1.0 (educational game; Wikimedia attribution)"
def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()
def get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=100) as response:
                return response.read()
        except Exception:
            if attempt == 2:
                raise
            time.sleep(3 * (attempt + 1))
def fetch_photo(spec: dict):
    params = urllib.parse.urlencode({
        "action": "query", "format": "json", "prop": "imageinfo",
        "titles": "File:" + spec["title"], "iiprop": "url|size|extmetadata"})
    pages = json.loads(get("https://commons.wikimedia.org/w/api.php?" + params))["query"]["pages"]
    p = next(iter(pages.values()))
    if "imageinfo" not in p:
        raise RuntimeError("Missing Commons image: " + spec["title"])
    info = p["imageinfo"][0]
    short = html.unescape(re.sub("<[^>]*>", "", info["extmetadata"]["LicenseShortName"]["value"])).strip()
    if short != "CC BY-SA 4.0":
        raise RuntimeError("License mismatch " + spec["title"] + ": " + short)
    data = get(info["url"])
    photo = Image.open(BytesIO(data)).convert("RGB")
    if photo.width < spec["x"] + spec["cols"] * W or photo.height < spec["y"] + 2 * H:
        raise RuntimeError("Original image insufficient for unscaled source crops: " + spec["title"])
    return photo, data, info
def main():
    OUT.mkdir(parents=True, exist_ok=True)
    cells = []
    for group, spec in enumerate(SOURCES):
        photo, raw, info = fetch_photo(spec)
        # Apply one global photographic grade, never stretch or warp tree geometry.
        photo = ImageEnhance.Color(photo).enhance(.88)
        photo = ImageEnhance.Contrast(photo).enhance(1.04)
        photo = ImageEnhance.Brightness(photo).enhance(.92)
        xoffset = 0
        for row in range(2):
            for col in range(spec["cols"]):
                gx, gy = X0 + xoffset + col, Y0 + row
                left, top = spec["x"] + col * W, spec["y"] + row * H
                rect = [left, top, left + W, top + H]
                tile = photo.crop(tuple(rect))
                name = f"eu-{gx:02d}-{gy:02d}"
                dest = OUT / (name + ".webp")
                tile.save(dest, "WEBP", quality=93, method=6)
                cells.append({
                    "id": name, "grid": [gx, gy], "origin": [gx * W, gy * H],
                    "image": "terrain-grid/factory-photo/carpathian-8/" + dest.name,
                    "imageSize": [W, H], "originalSource": info["url"],
                    "sourcePage": "https://commons.wikimedia.org/wiki/File:" + urllib.parse.quote(spec["title"].replace(" ", "_")),
                    "author": "Ryzhkov Oleksandr", "license": "CC BY-SA 4.0",
                    "licenseUrl": "https://creativecommons.org/licenses/by-sa/4.0/",
                    "sourceCrop": rect, "sourceSha256": sha(raw),
                    "outputSha256": sha(dest.read_bytes()),
                    "motif": spec["motif"],
                    "sourceRegion": "Ukrainian Carpathians (modern illustrative photo, NOT precise V94 registration)",
                    "nativePhotoSourceGroup": "carpathian-original-" + str(group),
                    "nativePhotoUnderlay": True, "unscaledOriginalPixelCrop": True,
                    "sourceBackedPhotographicArtComposed": True,
                    "exactPhotoGeoreferenced": False, "periodSafe": False,
                    "modernFeaturesQuarantined": False, "artMethodApproved": False,
                    "physicallyRoadSeamChecked": False, "paintedRoads": [],
                    "gameplayEnabled": False, "historicallyVerified": False,
                    "visuallyReviewedOnPhone": False, "provinceIds": [],
                    "scenicSettlements": [], "strategicTowns": []
                })
    by_grid = {tuple(c["grid"]): c for c in cells}
    if len(cells) != 8 or len(by_grid) != 8 or len({c["outputSha256"] for c in cells}) != 8:
        raise RuntimeError("Expected eight distinct photographic crops")
    same, blocked = [], []
    for cell in cells:
        x, y = cell["grid"]
        for next_grid in ((x + 1, y), (x, y + 1)):
            if next_grid not in by_grid:
                continue
            neighbor = by_grid[next_grid]
            native = cell["nativePhotoSourceGroup"] == neighbor["nativePhotoSourceGroup"]
            a, b = cell["sourceCrop"], neighbor["sourceCrop"]
            if native:
                adjacent = (a[2] == b[0] and a[1] == b[1]) if x != next_grid[0] else (a[3] == b[1] and a[0] == b[0])
                if not adjacent:
                    raise RuntimeError("Nonadjacent source crop declared seamless")
            record = {"a": cell["id"], "b": neighbor["id"],
                      "sourceNativePixelAdjacent": native, "roadPainted": False,
                      "routeEnabled": False, "visuallyApproved": False}
            (same if native else blocked).append(record)
    if len(same) != 10 or len(blocked) != 0:
        raise RuntimeError(f"Expected 10 native joins / 0 blocked; got {len(same)} / {len(blocked)}")
    cells.sort(key=lambda c: (c["grid"][1], c["grid"][0]))
    sheet = Image.new("RGB", (3072, 1100), "#182b24")
    for c in cells:
        col, row = c["grid"][0] - X0, c["grid"][1] - Y0
        image = Image.open(ROOT / c["image"]).convert("RGB")
        sheet.paste(image.resize((768, 512), Image.Resampling.LANCZOS), (col * 768, row * 512))
    draw = ImageDraw.Draw(sheet)
    draw.text((18, 1035), "8 original-resolution Carpathian photo crops; 10 exact native joins; no cross-source seam", fill="#f5e3bd")
    draw.text((18, 1062), "ILLUSTRATIVE MODERN SOURCE: 0 roads approved, 0 historical provinces, 0 playable octagons", fill="#f5e3bd")
    sheet.save(OUT / "photo-block-review.webp", "WEBP", quality=91, method=6)
    manifest = {
        "schema": "coe-photo-art/v1", "status": "Carpathian-continuous-panorama-8-photo-study-NOT-playable",
        "fixedArtReference": "456107f28c8db1f87522bbc7511809b2a215f6fb",
        "studyGrid": [X0, Y0, 4, 2], "georegistered": False,
        "geographyWarning": "Modern source location is genuine; individual V94 cell alignment, 1780 roads and villages are NOT verified.",
        "photographicArtComposed": 8, "nativePhotoPixelJoins": same,
        "unapprovedCrossSourceJoins": blocked, "visuallyChecked": 0,
        "physicallyRoadConnected": 0, "mobileRendered": 0,
        "nativeGamePlayable": 0, "historicallyVerified": 0, "finishedToday": 0,
        "cells": cells
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    cards = "".join('<article><img src="' + c["id"] + '.webp" alt="' +
                    html.escape(c["motif"]) + '"><p>' + c["id"] +
                    " · licensed photo source, NO approved roads</p></article>" for c in cells)
    (OUT / "index.html").write_text(
        '<!doctype html><html lang="en"><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>Carpathian 8-cell photographic source block</title>'
        '<style>body{background:#172820;color:#f4e5ca;font:14px system-ui;margin:12px}'
        'main{display:grid;grid-template-columns:repeat(4,minmax(0,1fr))}'
        'article{min-width:0}img{width:100%;display:block}.sheet{width:100%}</style>'
        '<h1>Carpathian forest: eight source-native photographic candidates</h1>'
        '<p>Original photo pixels, no mirrored trees or global warping. No cross-source boundaries;'
        ' no roads or provinces are inferred from seamless terrain.</p>'
        '<img class="sheet" src="photo-block-review.webp" alt="Eight-cell photo overview">'
        '<main>' + cards + '</main>'
        '<p>Photos © Ryzhkov Oleksandr, CC BY-SA 4.0. Adapted color/exposure; attribution and'
        ' share-alike apply to derivative imagery. NOT 1780 georegistration.</p></html>')
    print(json.dumps({"photoArtComposed": 8, "sourceNativeJoins": 10,
                      "crossSourceBlocked": 0, "finishedToday": 0}))
if __name__ == "__main__":
    main()

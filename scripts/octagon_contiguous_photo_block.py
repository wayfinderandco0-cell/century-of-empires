#!/usr/bin/env python3
"""Eight distinct native-pixel photographic octagon source studies in one 4x2 block.

Two independently credited 3072x2304 Sharr aerial photographs each supply a
2x2 native-pixel mosaic. Inside each 2x2 group, edges and decorative diamond
infill are cut from exactly adjacent source pixels, without mirroring, cloning,
resizing, painting fictitious cartways, or changing V121/V123/V94. The two
different photographs do NOT share an authenticated geographic seam: the two
joins between groups are explicitly BLOCKED, not approved road connections.
This is photographic art production, NOT eight finished/playable octagons.
"""
from __future__ import annotations
import hashlib
import html
import json
from pathlib import Path
from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageStat

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "terrain-grid/factory-photo/block-8"
W, H = 1536, 1024
X0, Y0 = 9, 16
SOURCES = (
    {"key": "west", "path": "terrain-v224/source/west-wikimedia-3072-ccby.jpg",
     "columns": (0, 1), "y0": 256, "group": "sharr-west-native-2x2",
     "motif": "Sharr high limestone and mountain meadow"},
    {"key": "south", "path": "terrain-v224/source/south-wikimedia-3072-ccby.jpg",
     "columns": (2, 3), "y0": 256, "group": "sharr-south-native-2x2",
     "motif": "Sharr wooded mountain valley and slopes"},
)
def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()
def cell_id(x: int, y: int) -> str:
    return f"eu-{x:02d}-{y:02d}"
def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    evidence = json.loads((ROOT / "terrain-v224/assets/manifest.json").read_text())
    licenses = {row["tile"]: row for row in evidence["sources"]}
    cells, decoded, graded_sources = [], {}, {}
    for spec in SOURCES:
        license_info = licenses[spec["key"]]
        if license_info["original"] != spec["path"] or license_info["license"] != "CC BY 4.0":
            raise RuntimeError("Missing source attribution / exact license for " + spec["key"])
        source_path = ROOT / spec["path"]
        source = Image.open(source_path).convert("RGB")
        if source.size != (3072, 2304):
            raise RuntimeError("Source not large enough for unscaled 2x2 atlas")
        # Grade the WHOLE photograph once before cropping. This prevents
        # inconsistent per-tile color/exposure bands at native-pixel joins.
        source = ImageEnhance.Color(source).enhance(.88)
        source = ImageEnhance.Contrast(source).enhance(1.035)
        source = ImageEnhance.Brightness(source).enhance(.92)
        graded_sources[spec["group"]] = source
        for local_y in range(2):
            for local_x, grid_x in enumerate(spec["columns"]):
                grid_y = Y0 + local_y
                x, y = local_x * W, spec["y0"] + local_y * H
                rect = (x, y, x + W, y + H)
                tile = source.crop(rect)
                id_ = cell_id(X0 + grid_x, grid_y)
                out_file = OUT / (id_ + ".webp")
                tile.save(out_file, "WEBP", quality=94, method=6)
                actual = Image.open(out_file).convert("RGB")
                if actual.size != (W, H):
                    raise RuntimeError("Incorrect photographic dimensions")
                fidelity = sum(ImageStat.Stat(ImageChops.difference(actual, tile)).mean) / 3
                if fidelity >= 18:
                    raise RuntimeError(f"Lossy encoding harmed photographic source fidelity: {id_}: {fidelity}")
                decoded[id_] = actual
                cells.append({
                    "id": id_, "grid": [X0 + grid_x, grid_y],
                    "origin": [(X0 + grid_x) * W, grid_y * H],
                    "image": "terrain-grid/factory-photo/block-8/" + out_file.name,
                    "imageSize": [W, H], "originalSource": spec["path"],
                    "sourceCrop": list(rect), "sourceSha256": sha(source_path.read_bytes()),
                    "outputSha256": sha(out_file.read_bytes()), "sourcePage": license_info["sourcePage"],
                    "author": license_info["author"], "license": license_info["license"],
                    "licenseUrl": license_info["licenseUrl"], "motif": spec["motif"],
                    "sourceRegion": "Sharr Mountains, Balkans — illustrative photo, NOT grid georegistration",
                    "nativePhotoSourceGroup": spec["group"],
                    "nativePhotoUnderlay": True, "unscaledOriginalPixelCrop": True,
                    "terrainSourceSeamVerifiedWithinGroup": True,
                    "photoEncodingMeanError": round(fidelity, 3),
                    "exactPhotoGeoreferenced": False, "periodSafe": False,
                    "modernFeaturesQuarantined": False,
                    "sourceBackedPhotographicArtComposed": True,
                    "artMethodApproved": False, "physicallyRoadSeamChecked": False,
                    "paintedRoads": [], "gameplayEnabled": False,
                    "historicallyVerified": False, "visuallyReviewedOnPhone": False,
                    "provinceIds": [], "scenicSettlements": [], "strategicTowns": []
                })
    by_grid = {tuple(c["grid"]): c for c in cells}
    if len(cells) != 8 or len(by_grid) != 8 or len({c["outputSha256"] for c in cells}) != 8:
        raise RuntimeError("Expected eight different source-native tiles")
    same_source_joins, blocked_joins = [], []
    for c in cells:
        x, y = c["grid"]
        for neighbor in ((x + 1, y), (x, y + 1)):
            if neighbor not in by_grid:
                continue
            other = by_grid[neighbor]
            horizontal = neighbor[0] != x
            same = c["nativePhotoSourceGroup"] == other["nativePhotoSourceGroup"]
            if same:
                a, b = c["sourceCrop"], other["sourceCrop"]
                adjacent = (a[2] == b[0] and a[1] == b[1] and a[3] == b[3]) if horizontal else (
                    a[3] == b[1] and a[0] == b[0] and a[2] == b[2])
                if not adjacent:
                    raise RuntimeError("Native photographic source coordinates fail to meet")
            record = {"a": c["id"], "b": other["id"],
                      "sourceNativePixelAdjacent": same, "roadPainted": False,
                      "routeEnabled": False, "visuallyApproved": False}
            (same_source_joins if same else blocked_joins).append(record)
    if len(same_source_joins) != 8 or len(blocked_joins) != 2:
        raise RuntimeError("Expected 8 source-native joins and 2 unverified cross-source joins")
    # A literal image mosaic, not a synthetic or geographic screenshot. It
    # lets reviewers see the whole block before native WebKit screenshots.
    sheet = Image.new("RGB", (W * 4 // 2, H * 2 // 2 + 76), "#182b24")
    for c in cells:
        col = c["grid"][0] - X0
        row = c["grid"][1] - Y0
        sheet.paste(decoded[c["id"]].resize((W // 2, H // 2), Image.Resampling.LANCZOS),
                    (col * W // 2, row * H // 2))
    draw = ImageDraw.Draw(sheet)
    x = W
    for y in range(0, H, 18):
        draw.line((x, y, x, min(H, y + 9)), fill="#f5b36b", width=4)
    draw.text((12, H + 12), "8 native photographic tiles / 8 source-coordinate joins / 2 cross-source seams BLOCKED", fill="#f8ead2")
    draw.text((12, H + 36), "ILLUSTRATIVE PHOTO STUDY: 0 road-connected, 0 historically verified, 0 playable", fill="#f8ead2")
    sheet.save(OUT / "photo-block-review.webp", "WEBP", quality=90, method=6)
    manifest = {
        "schema": "coe-photo-art/v1", "status": "eight-cell-contiguous-photo-study-NOT-playable",
        "fixedArtReference": "456107f28c8db1f87522bbc7511809b2a215f6fb",
        "studyGrid": [X0, Y0, 4, 2], "georegistered": False,
        "geographyWarning": "Sharr source photography is NOT evidence of exact V94 cell location, route, province or 1780-era features.",
        "photographicArtComposed": 8, "nativePhotoPixelJoins": same_source_joins,
        "unapprovedCrossSourceJoins": blocked_joins, "visuallyChecked": 0,
        "physicallyRoadConnected": 0, "mobileRendered": 0,
        "nativeGamePlayable": 0, "historicallyVerified": 0, "finishedToday": 0,
        "cells": sorted(cells, key=lambda c: (c["grid"][1], c["grid"][0]))
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    cards = "".join('<article><img src="' + c["id"] + '.webp" alt="' + html.escape(c["motif"]) +
                    '"><p>' + c["id"] + ' · ' + html.escape(c["nativePhotoSourceGroup"]) +
                    ' · NO gameplay roads</p></article>' for c in manifest["cells"])
    (OUT / "index.html").write_text(
        '<!doctype html><html lang="en"><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>Eight-cell original photo atlas source study</title>'
        '<style>body{background:#152720;color:#f5e6ca;font:14px system-ui;margin:10px}'
        'main{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:0}'
        'article{min-width:0}article img{width:100%;display:block}article p{font-size:9px}'
        '.sheet{width:100%;height:auto}a{color:#f5c37e}</style>'
        '<h1>Eight native 1536x1024 photographic art candidates</h1>'
        '<p>Eight true adjacent photographic crops within two different licensed Sharr sources. '
        'Eight exact source-coordinate joins, TWO cross-source joins remain visually UNVERIFIED. '
        'All photos illustrative only; no roads, province captures, historic claims or playable cells.</p>'
        '<img class="sheet" src="photo-block-review.webp" alt="Eight photo tiles with blocked source boundary">'
        '<main>' + cards + '</main>'
        '<p>Both original photographs: SUHEJLO, CC BY 4.0, sourced from Wikimedia Commons. '
        'Use the native game with ?photoBlock=1 then Integrated Alpine atlas / Photo sources to inspect touch pan and zoom.</p>'
        '</html>')
    (OUT / "qa-report.json").write_text(json.dumps({
        "candidatePhotoTiles": 8, "sourceNativeAdjacentJoins": 8,
        "blockedCrossSourceJoins": 2, "roadsApproved": 0,
        "nativeGamePlayable": 0, "historicallyVerified": 0,
        "finishedToday": 0
    }, indent=2) + "\n")
    print(json.dumps({"sourcePhotoTiles": 8, "nativePhotoPixelJoins": 8,
                      "blockedCrossSourceJoins": 2, "roadConnected": 0,
                      "playable": 0, "finishedToday": 0}))
if __name__ == "__main__":
    main()

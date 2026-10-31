#!/usr/bin/env python3
"""Unify existing 1536x1024 licensed photographic cells in ONE native atlas stream.

This is real source artwork already committed, NOT 19 newly produced or playable
octagons. Source-native adjacency is checked before decorative gap infill;
cross-source borders are blocked. V121, V123, V94 and all saves stay untouched.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "terrain-grid/factory-photo/coverage"
W, H = 1536, 1024
SOURCES = (
    ("terrain-grid/factory-photo/manifest.json", "single"),
    ("terrain-grid/factory-photo/block-8/manifest.json", "sharr"),
    ("terrain-grid/factory-photo/carpathian-8/manifest.json", "carpathian"),
)

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    by_id = {}
    superseded = []
    for path, kind in SOURCES:
        source = json.loads((ROOT / path).read_text())
        if source["schema"] != "coe-photo-art/v1":
            raise RuntimeError("Unexpected source schema " + path)
        for item in source["cells"]:
            c = dict(item)
            if c.get("gameplayEnabled") or c.get("historicallyVerified") or c.get("physicallyRoadSeamChecked"):
                raise RuntimeError("Unsafe gameplay/road/historical flag on " + c["id"])
            image = ROOT / c["image"]
            if not image.is_file() or Image.open(image).size != (W, H):
                raise RuntimeError("Missing full-resolution native photograph " + str(image))
            if hashlib.sha256(image.read_bytes()).hexdigest() != c["outputSha256"]:
                raise RuntimeError("Source artwork hash changed " + c["id"])
            x, y = c["grid"]
            if c["origin"] != [x * W, y * H] or c["id"] != f"eu-{x:02d}-{y:02d}":
                raise RuntimeError("Invalid world-coordinate placement " + c["id"])
            c["nativePhotoSourceGroup"] = c.get("nativePhotoSourceGroup", "standalone-" + c["id"])
            c["nativePhotoUnderlay"] = bool(c.get("nativePhotoUnderlay", False))
            c["sourceManifest"] = path
            c["exactPhotoGeoreferenced"] = False
            c["artMethodApproved"] = False
            c["gameplayEnabled"] = False
            c["historicallyVerified"] = False
            c["physicallyRoadSeamChecked"] = False
            c["visuallyReviewedOnPhone"] = False
            c["provinceIds"] = []
            c["strategicTowns"] = []
            if c["id"] in by_id:
                superseded.append({"id": c["id"], "replaced": by_id[c["id"]]["sourceManifest"],
                                   "chosen": path})
            by_id[c["id"]] = c
    cells = sorted(by_id.values(), key=lambda c: (c["grid"][1], c["grid"][0]))
    if len(cells) != 19 or len(superseded) != 2:
        raise RuntimeError(f"Expected 19 unique cells and 2 superseded originals, got {len(cells)}, {len(superseded)}")
    grid = {tuple(c["grid"]): c for c in cells}
    native, blocked = [], []
    for c in cells:
        x, y = c["grid"]
        for nx, ny in ((x + 1, y), (x, y + 1)):
            b = grid.get((nx, ny))
            if b is None:
                continue
            same = c["nativePhotoSourceGroup"] == b["nativePhotoSourceGroup"] and c["nativePhotoUnderlay"] and b["nativePhotoUnderlay"]
            if same:
                a_crop, b_crop = c.get("sourceCrop"), b.get("sourceCrop")
                if not a_crop or not b_crop:
                    raise RuntimeError("Missing native-pixel provenance for " + c["id"])
                horizontal = nx != x
                exact = ((a_crop[2] == b_crop[0] and a_crop[1] == b_crop[1] and a_crop[3] == b_crop[3])
                         if horizontal else
                         (a_crop[3] == b_crop[1] and a_crop[0] == b_crop[0] and a_crop[2] == b_crop[2]))
                if not exact or c["sourceSha256"] != b["sourceSha256"]:
                    raise RuntimeError("Unverified source-pixel seam " + c["id"] + " / " + b["id"])
            row = {"a": c["id"], "b": b["id"], "sourceNativePixelAdjacent": bool(same),
                   "roadPainted": False, "routeEnabled": False, "visuallyApproved": False}
            (native if same else blocked).append(row)
    if len(native) != 18 or len(blocked) != 2:
        raise RuntimeError(f"Expected 18 exact source joins, 2 blocked, got {len(native)}, {len(blocked)}")
    # Four matching, original-source neighboring cells can fill a road-free
    # central corner diamond. A seam between different photographs CANNOT.
    diamonds = []
    for x in range(1, 18):
        for y in range(1, 24):
            quartet = [grid.get((x-1, y-1)), grid.get((x, y-1)),
                       grid.get((x-1, y)), grid.get((x, y))]
            if all(quartet) and all(q["nativePhotoUnderlay"] for q in quartet):
                if len({q["nativePhotoSourceGroup"] for q in quartet}) == 1:
                    diamonds.append({"worldCenter": [x * W, y * H],
                                     "sourceCellIds": [q["id"] for q in quartet],
                                     "playable": False, "roads": []})
    if len(diamonds) != 5:
        raise RuntimeError(f"Expected five authentic source-native corner diamonds, got {len(diamonds)}")
    result = {
        "schema": "coe-photo-art/v1", "status": "unified-source-art-CANDIDATES-not-playable",
        "fixedArtReference": "456107f28c8db1f87522bbc7511809b2a215f6fb",
        "description": "19 distinct preexisting photographic candidates in one native game canvas, NOT new final octagons",
        "sourceArtworkRecords": 21, "photographicArtComposed": 19,
        "newArtworkComposedThisRun": 0, "uniquePhotoCells": len(cells),
        "supersededOverlaps": superseded, "nativePhotoPixelJoins": native,
        "unapprovedCrossSourceJoins": blocked, "roadFreeNativeDiamondInlays": diamonds,
        "exactPhotoGeoreferenced": False, "visuallyChecked": 0,
        "physicallyRoadConnected": 0, "mobileRendered": 0,
        "nativeGamePlayable": 0, "historicallyVerified": 0, "finishedToday": 0,
        "cells": cells
    }
    (OUT / "manifest.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    (OUT / "README.md").write_text(
        "# Native Europe photo coverage — review only\n\n"
        "Nineteen distinct **previously committed** 1536×1024 licensed photographic candidates are now streamed "
        "in one atlas. Two overlapping Sharr source records are superseded by the coherent 4×2 block. "
        "Eighteen original-source adjacent photo joins and five four-cell road-free corner diamonds are "
        "eligible for native-pixel decorative infill. Two cross-source joins remain blocked. "
        "None of these source photographs is exactly georeferenced or 1780–1880 road certified. "
        "**0 newly finished octagons.** Open the native game with `?photoBlock=coverage`, "
        "choose Integrated Alpine atlas → Photo sources → Whole, then zoom or inspect Next region. "
        "This is an opt-in artwork layer and does not alter the V94 campaign, V121 Matrei, V123 roads or saves.\n"
    )
    print(json.dumps({"uniquePhotoCells": len(cells), "sourceNativeJoins": len(native),
                      "blockedSourceJoins": len(blocked), "roadFreeDiamondInlays": len(diamonds),
                      "newArt": 0, "roadConnected": 0, "playable": 0, "finishedToday": 0}))

if __name__ == "__main__":
    main()

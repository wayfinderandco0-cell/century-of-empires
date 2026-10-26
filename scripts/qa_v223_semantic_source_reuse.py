#!/usr/bin/env python3
"""V223 source-pixel reuse gate: unique crop origins do NOT prove distinct art.

This is a necessary anti-quilt test, never a sufficient human-realism or
historical-geography approval. V222 is a deliberately REJECTED control.
"""
import argparse
import json
from collections import defaultdict
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
DEFAULT = ROOT / "terrain-v222/assets/manifest.json"
MAX_REUSE = 0.12
FALSE_APPROVAL = (
    "sourceRegisteredToV123", "historicRoadsVerified", "periodSafe",
    "gameArtApproved", "physicalIPhoneApproved", "productionApproved"
)


def insist(condition, message):
    if not condition:
        raise ValueError("V223 fail-closed: " + message)


def source_key(manifest, cell, patch):
    # Legacy V222 patches all draw from the *same* original Matrei painting.
    return patch.get("sourceSha256") or cell.get("sourceSha256") or manifest.get("originalMatreiGitBlob")


def analyze(manifest):
    insist(isinstance(manifest, dict), "missing manifest")
    for flag in FALSE_APPROVAL:
        insist(manifest.get(flag) is False, "unverified approval flag " + flag)
    cells = manifest.get("cells")
    insist(isinstance(cells, list) and len(cells) == 2, "two neighbor cells required")
    insist({c.get("tile") for c in cells} == {"west", "south"}, "wrong neighbors")
    width, height = manifest.get("sourceNativePixels", manifest.get("nativeCellPixels", [0, 0]))
    insist(isinstance(width, int) and isinstance(height, int) and 0 < width <= 12000 and 0 < height <= 12000,
           "missing or unsafe source dimensions")
    # Difference arrays count ORIGINAL source-pixel reads, across BOTH cells.
    # This detects near-identical overlapping source patches with distinct x/y.
    difference = defaultdict(lambda: np.zeros((height + 1, width + 1), dtype=np.int32))
    count = 0
    for cell in cells:
        patches = cell.get("patches")
        insist(isinstance(patches, list) and patches, "no source provenance for " + str(cell.get("tile")))
        for patch in patches:
            key = source_key(manifest, cell, patch)
            insist(isinstance(key, str) and len(key) >= 12, "unknown source identity")
            rect = patch.get("sourceRect")
            insist(isinstance(rect, list) and len(rect) == 4, "missing original source rectangle")
            x0, y0, x1, y1 = rect
            insist(all(isinstance(v, int) for v in rect) and 0 <= x0 < x1 <= width and 0 <= y0 < y1 <= height,
                   "invalid original source rectangle")
            grid = difference[key]
            grid[y0, x0] += 1
            grid[y1, x0] -= 1
            grid[y0, x1] -= 1
            grid[y1, x1] += 1
            count += 1
    reads = 0
    unique = 0
    repeats = 0
    counts = {}
    for key, diff in difference.items():
        occupancy = diff.cumsum(axis=0).cumsum(axis=1)[:-1, :-1]
        insist(np.min(occupancy) >= 0, "source occupancy underflow")
        pixels = int(occupancy.sum())
        used = int(np.count_nonzero(occupancy))
        reused = pixels - used
        reads += pixels
        unique += used
        repeats += reused
        counts[key] = occupancy
    insist(reads > 0, "empty source coverage")
    ratio = repeats / reads
    return {
        "version": 223,
        "sourceIdentities": len(counts),
        "patches": count,
        "sourcePixelReads": reads,
        "uniqueOriginalSourcePixels": unique,
        "repeatedSourcePixelReads": repeats,
        "sourceReuseFraction": round(ratio, 6),
        "maximumSourceReuseFraction": MAX_REUSE,
        "passedNecessaryNonreuseGate": ratio <= MAX_REUSE,
        "status": "PASS_NECESSARY_SOURCE_NONREUSE_ONLY" if ratio <= MAX_REUSE else "REJECTED_OVERLAPPING_SOURCE_MOTIFS",
        "humanArtApproved": False,
        "historicalGeographyVerified": False,
        "physicalIPhoneApproved": False,
        "productionApproved": False,
    }, counts


def heatmap(counts, path):
    # Exact original source occupancy, not synthetic terrain or a game screenshot.
    tiles = []
    for source, occupancy in sorted(counts.items()):
        small = Image.fromarray(np.uint8(np.clip(occupancy, 0, 4) * 63), "L")
        small.thumbnail((768, 512))
        rgb = Image.new("RGB", small.size)
        a = np.asarray(small)
        data = np.zeros((a.shape[0], a.shape[1], 3), dtype=np.uint8)
        data[:, :, 0] = a
        data[:, :, 1] = np.where(a > 0, 145, 22)
        data[:, :, 2] = np.where(a > 0, 45, 30)
        rgb = Image.fromarray(data, "RGB")
        tiles.append((source, rgb))
    out = Image.new("RGB", (max(im.width for _, im in tiles), sum(im.height + 34 for _, im in tiles)), "#1b241c")
    draw = ImageDraw.Draw(out)
    y = 0
    for source, im in tiles:
        draw.text((8, y + 5), "ORIGINAL SOURCE REUSE (RED=REPEATED) " + source[:18], fill="white")
        out.paste(im, (0, y + 34))
        y += im.height + 34
    path.parent.mkdir(parents=True, exist_ok=True)
    out.save(path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=DEFAULT)
    parser.add_argument("--out", type=Path, default=ROOT / "qa/v223-source-reuse")
    parser.add_argument("--enforce", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text())
    result, counts = analyze(manifest)
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "report.json").write_text(json.dumps(result, indent=2) + "\n")
    heatmap(counts, args.out / "original-source-occupancy.png")
    print(json.dumps(result, indent=2))
    if args.enforce and not result["passedNecessaryNonreuseGate"]:
        raise SystemExit("V223 SOURCE ART REJECTED: repeated original Matrei pixels, not distinct landscapes")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""V232 source-art cartway preflight. Never asserts 1780 geography or art approval.

The exact immutable V123 polylines are read from source. This rejects images
where the gameplay road would be painted across dark tree canopy, bare rock or
highly textured non-ground. It does NOT edit pixels, invent a road, or certify
a crossing; semantic thresholds are conservative necessary conditions only.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
ATLAS = ROOT / "terrain-grid/v123-atlas.js"
SIZE = (1536, 1024)
MIN_OPEN = 0.72
MAX_BLOCKED_RUN = 70.0
SAMPLE_STEP = 4.0
FALSE_FLAGS = {
    "sourceRegisteredToV123": False,
    "historicalRoadsVerified": False,
    "bridgeBanksVerified": False,
    "periodSafe": False,
    "humanVisualApproval": False,
    "physicalIPhoneApproved": False,
    "productionApproved": False,
}

def source_roads(text=None):
    text = ATLAS.read_text() if text is None else text
    roads = {}
    for tile in ("west", "south"):
        m = re.search(r"const\s+" + tile + r"Road\s*=\s*(\[.*?\]);", text, re.S)
        if not m:
            raise ValueError("Immutable V123 " + tile + " road not found")
        road = json.loads(m.group(1))
        if len(road) < 3 or not all(len(p) == 2 for p in road):
            raise ValueError("Invalid V123 road " + tile)
        roads[tile] = road
    if roads["west"][0] != [1536, 478] or roads["west"][-1] != [275, 550]:
        raise ValueError("STOP: WEST immutable V123 endpoints changed")
    if roads["south"][0] != [466, 0] or roads["south"][-1] != [1270, 605]:
        raise ValueError("STOP: SOUTH immutable V123 endpoints changed")
    return roads

def sample_polyline(points, spacing=SAMPLE_STEP):
    out = []
    for a, b in zip(points[:-1], points[1:]):
        a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
        dist = float(np.linalg.norm(b-a))
        for i in range(max(1, int(np.ceil(dist / spacing)))):
            t = i / max(1, int(np.ceil(dist / spacing)))
            out.append((float(a[0]*(1-t)+b[0]*t), float(a[1]*(1-t)+b[1]*t)))
    out.append(tuple(map(float, points[-1])))
    return out

def ground_mask(image):
    rgb = np.asarray(image.convert("RGB"))
    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
    h, s, v = cv2.split(hsv)
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY).astype(np.float32)
    high = np.abs(gray - cv2.GaussianBlur(gray, (0, 0), 4.0))
    # Sunlit grass/soil: dark conifers and gray rock cannot masquerade as roadbed.
    plausible = ((h >= 17) & (h <= 95) & (s >= 28) &
                 (v >= 70) & (v <= 230) & (high < 24))
    return plausible.astype(np.uint8), {"darkCanopy": (v < 70).astype(np.uint8),
                                        "bareRock": ((s < 35) & (v > 100)).astype(np.uint8)}

def inspect(image, points, tile):
    if image.size != SIZE:
        raise ValueError(f"{tile}: expected {SIZE}, got {image.size}")
    ground, exclusions = ground_mask(image)
    samples = sample_polyline(points)
    flags = []
    blocked_run = longest = 0.0
    for x, y in samples:
        xi, yi = round(x), round(y)
        x0, x1 = max(0, xi-12), min(SIZE[0], xi+13)
        y0, y1 = max(0, yi-12), min(SIZE[1], yi+13)
        # A cartway needs clearance on BOTH sides; point-only sampling misses
        # trees that overhang the painted road.
        open_fraction = float(ground[y0:y1, x0:x1].mean())
        ok = open_fraction >= 0.67
        flags.append(ok)
        blocked_run = 0.0 if ok else blocked_run + SAMPLE_STEP
        longest = max(longest, blocked_run)
    canvas = np.zeros((SIZE[1], SIZE[0]), np.uint8)
    cv2.polylines(canvas, [np.asarray(points, np.int32)], False, 255, 24, cv2.LINE_AA)
    near = canvas > 128
    metrics = {
        "tile": tile,
        "imageSha256": hashlib.sha256(image.tobytes()).hexdigest(),
        "pixels": list(image.size),
        "roadVertices": len(points),
        "sampleCount": len(samples),
        "openRoadbedArea": round(float(ground[near].mean()), 5),
        "openRouteSamples": round(float(np.mean(flags)), 5),
        "darkCanopyArea": round(float(exclusions["darkCanopy"][near].mean()), 5),
        "bareRockArea": round(float(exclusions["bareRock"][near].mean()), 5),
        "longestBlockedRunPx": round(longest, 1),
    }
    metrics["necessaryRoadGroundGate"] = (
        metrics["openRoadbedArea"] >= MIN_OPEN
        and metrics["openRouteSamples"] >= MIN_OPEN
        and metrics["longestBlockedRunPx"] <= MAX_BLOCKED_RUN
    )
    metrics.update(FALSE_FLAGS)
    review = image.convert("RGBA")
    overlay = Image.new("RGBA", SIZE)
    draw = ImageDraw.Draw(overlay)
    for (x1, y1), (x2, y2), good in zip(samples[:-1], samples[1:], flags[:-1]):
        draw.line([(x1, y1), (x2, y2)],
                  fill=(44, 196, 97, 180) if good else (230, 58, 50, 205),
                  width=23)
    review = Image.alpha_composite(review, overlay).convert("RGB")
    return metrics, review

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--west", type=Path, required=True)
    p.add_argument("--south", type=Path, required=True)
    p.add_argument("--output", type=Path, default=ROOT/"qa/v232-road-ground")
    p.add_argument("--enforce", action="store_true")
    args = p.parse_args()
    roads = source_roads()
    args.output.mkdir(parents=True, exist_ok=True)
    records = {}
    for tile in ("west", "south"):
        with Image.open(getattr(args, tile)) as im:
            records[tile], review = inspect(im, roads[tile], tile)
        review.save(args.output/f"{tile}-actual-image-road-ground-review.jpg",
                    quality=91)
    report = {
        "version": 232,
        "purpose": "Necessary semantic road-ground clearance, NOT visual approval",
        "immutableRoads": "terrain-grid/v123-atlas.js",
        "bothGroundGatesPass": all(r["necessaryRoadGroundGate"] for r in records.values()),
        "tiles": records,
        **FALSE_FLAGS,
    }
    (args.output/"report.json").write_text(json.dumps(report, indent=2)+"\n")
    print(json.dumps(report, indent=2))
    if args.enforce and not report["bothGroundGatesPass"]:
        raise SystemExit("RED: source images cannot ground both immutable cartways")

if __name__ == "__main__":
    main()

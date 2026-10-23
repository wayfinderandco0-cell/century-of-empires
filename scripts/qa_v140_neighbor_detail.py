#!/usr/bin/env python3
"""Fail-closed *detail parity* gate for three Alpine screenshot views.

A necessary, NOT sufficient, condition for credible terrain. High-frequency
noise can fool edge metrics; no machine score grants geographic/art approval.
"""
import argparse
import json
from pathlib import Path
from PIL import Image

REGIONS = ("matrei", "west", "south")
ENGINES = ("chromium", "webkit")
ORIENTATIONS = ("portrait", "landscape")
MIN_RELATIVE_GRADIENT = 0.35
MIN_RELATIVE_STRONG_EDGES = 0.25
STRONG_EDGE_LUMA = 12.0

def detail_score(image):
    """One-pixel luma transitions inside same HUD-free fractional viewport."""
    im = image.convert("RGB")
    width, height = im.size
    x0, x1 = int(width * .22), int(width * .80)
    y0, y1 = int(height * .22), int(height * .78)
    if x1 - x0 < 8 or y1 - y0 < 8:
        raise ValueError("Screenshot too small for visual detail audit")
    pixels = im.load()
    def luma(x, y):
        r, g, b = pixels[x, y]
        return .2126 * r + .7152 * g + .0722 * b
    count = 0
    total = 0.0
    strong = 0
    for y in range(y0, y1 - 1, 2):
        for x in range(x0, x1 - 1, 2):
            c = luma(x, y)
            for d in (abs(c - luma(x + 1, y)), abs(c - luma(x, y + 1))):
                total += d
                strong += d >= STRONG_EDGE_LUMA
                count += 1
    return {"mean_luma_gradient": round(total / count, 4),
            "strong_edge_fraction": round(strong / count, 5),
            "samples": count}

def assess(scores):
    matrei = scores["matrei"]
    checks = {}
    for region in ("west", "south"):
        other = scores[region]
        gradient_ratio = other["mean_luma_gradient"] / max(.001, matrei["mean_luma_gradient"])
        edge_ratio = other["strong_edge_fraction"] / max(.00001, matrei["strong_edge_fraction"])
        checks[region] = {
            "relative_gradient": round(gradient_ratio, 4),
            "relative_strong_edges": round(edge_ratio, 4),
            "passes_minimum_detail": gradient_ratio >= MIN_RELATIVE_GRADIENT and edge_ratio >= MIN_RELATIVE_STRONG_EDGES,
        }
    return checks

def audit(folder):
    results = {}
    missing = []
    for engine in ENGINES:
        for orientation in ORIENTATIONS:
            prefix = f"{engine}-{orientation}"
            scores = {}
            for region in REGIONS:
                path = folder / f"{prefix}-{region}-terrain.png"
                # V139 had an opening Matrei view, not a dedicated Matrei capture.
                if region == "matrei" and not path.exists():
                    path = folder / f"{prefix}-opening.png"
                if not path.exists():
                    missing.append(str(path))
                    continue
                with Image.open(path) as im:
                    scores[region] = detail_score(im)
            if len(scores) == 3:
                checks = assess(scores)
                results[prefix] = {"scores": scores, "neighbors": checks,
                                   "detail_gate_pass": all(v["passes_minimum_detail"] for v in checks.values())}
    passed = not missing and len(results) == 4 and all(x["detail_gate_pass"] for x in results.values())
    return {"passed": passed, "screenshots_missing": missing,
            "relative_gradient_floor": MIN_RELATIVE_GRADIENT,
            "relative_strong_edges_floor": MIN_RELATIVE_STRONG_EDGES,
            "results": results, "human_visual_approval": False,
            "geographic_or_historical_certification": False,
            "note": "Texture parity is necessary, never sufficient: procedural noise can pass without believable geography."}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--screenshots", type=Path, required=True)
    parser.add_argument("--enforce", action="store_true")
    args = parser.parse_args()
    result = audit(args.screenshots)
    target = args.screenshots / "v140-neighbor-visual-audit.json"
    target.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    if args.enforce and not result["passed"]:
        raise SystemExit("V140 visual gate REJECTED: neighbor terrain has insufficient high-frequency detail")

if __name__ == "__main__":
    main()

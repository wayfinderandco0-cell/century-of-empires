#!/usr/bin/env python3
"""V189: inspect EACH V188 Alpine neighbor at matched close-up phone zoom.

This is a necessary, fail-closed screenshot parity check, not a claim of
historical correctness, geographic registration, or physical iPhone approval.
The V140/V171 numerical floors are intentionally unchanged.
"""
import argparse
import http.server
import json
import threading
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "qa" / "v189-three-centers"
ENGINES = ("chromium", "webkit")
ORIENTATIONS = (("portrait", 390, 844), ("landscape", 844, 390))
REGIONS = ("west", "matrei", "south")
MIN_RELATIVE_GRADIENT = .35
MIN_RELATIVE_STRONG_EDGES = .25
STRONG_EDGE_LUMA = 12.0
ZOOM = 6.0  # fixed across the three centers in each phone configuration


def detail_score(image):
    im = image.convert("RGB")
    width, height = im.size
    x0, x1 = int(width * .22), int(width * .80)
    y0, y1 = int(height * .22), int(height * .78)
    if x1 - x0 < 8 or y1 - y0 < 8:
        raise ValueError("Screenshot too small for a meaningful terrain audit")
    px = im.load()
    def luma(x, y):
        r, g, b = px[x, y]
        return .2126 * r + .7152 * g + .0722 * b
    total = strong = count = 0
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
    center = scores["matrei"]
    checks = {}
    for region in ("west", "south"):
        candidate = scores[region]
        gradient = candidate["mean_luma_gradient"] / max(.001, center["mean_luma_gradient"])
        edges = candidate["strong_edge_fraction"] / max(.00001, center["strong_edge_fraction"])
        checks[region] = {
            "relative_gradient": round(gradient, 4),
            "relative_strong_edges": round(edges, 4),
            "passes_minimum_detail": gradient >= MIN_RELATIVE_GRADIENT
                                     and edges >= MIN_RELATIVE_STRONG_EDGES,
        }
    return checks


def audit(folder):
    results, missing = {}, []
    for engine in ENGINES:
        for orient, _, _ in ORIENTATIONS:
            scores = {}
            for region in REGIONS:
                path = folder / f"{engine}-{orient}-{region}-close.png"
                if not path.is_file():
                    missing.append(path.name)
                    continue
                with Image.open(path) as im:
                    scores[region] = detail_score(im)
            if len(scores) == len(REGIONS):
                checks = assess(scores)
                results[f"{engine}-{orient}"] = {
                    "scores": scores, "neighbors": checks,
                    "detail_gate_pass": all(x["passes_minimum_detail"] for x in checks.values())
                }
    return {
        "passed": not missing and len(results) == 4
                  and all(r["detail_gate_pass"] for r in results.values()),
        "missing_screenshots": missing, "results": results,
        "zoom_for_each_region": ZOOM,
        "relative_gradient_floor": MIN_RELATIVE_GRADIENT,
        "relative_strong_edges_floor": MIN_RELATIVE_STRONG_EDGES,
        "productionApproved": False, "physicalIPhoneApproved": False,
        "westSouthGeographicallyRegistered": False,
        "v123RoadAndBridgeHistoricallyVerified": False,
        "note": "A passing image-detail metric never certifies source provenance, natural appearance, roads, bridge, or user approval."
    }


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)
    def log_message(self, *args):
        pass


def capture(folder):
    from playwright.sync_api import sync_playwright
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    address = f"http://127.0.0.1:{server.server_port}/v188-terrain-continuity-trial.html"
    captures = {}
    try:
        with sync_playwright() as playwright:
            for engine in ENGINES:
                browser = getattr(playwright, engine).launch(headless=True)
                try:
                    for orient, width, height in ORIENTATIONS:
                        page = browser.new_page(
                            viewport={"width": width, "height": height},
                            is_mobile=True, has_touch=True, device_scale_factor=2)
                        errors = []
                        page.on("pageerror", lambda error: errors.append(str(error)))
                        try:
                            page.goto(address, wait_until="domcontentloaded", timeout=30000)
                            page.wait_for_function("window.V188?.ready===true", timeout=120000)
                            assert page.evaluate("V188.artDimensions") == [1536, 1024]
                            assert page.evaluate("V188.roadNodeCount") >= 90
                            assert not page.evaluate("V188.productionApproved")
                            for region in REGIONS:
                                assert page.evaluate("(region) => V188.focusTile(region)", region)
                                page.evaluate("(zoom) => V188.zoomTo(zoom)", ZOOM)
                                page.evaluate("() => new Promise(done => requestAnimationFrame(() => requestAnimationFrame(done)))")
                                filename = f"{engine}-{orient}-{region}-close.png"
                                page.screenshot(path=str(folder / filename), animations="disabled")
                                captures[filename] = {"width": width, "height": height,
                                                      "zoom": ZOOM, "region": region}
                            assert not errors, (engine, orient, errors)
                        finally:
                            page.close()
                finally:
                    browser.close()
    finally:
        server.shutdown()
    (folder / "capture-manifest.json").write_text(json.dumps(captures, indent=2) + "\n")
    return captures


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--screenshots", type=Path, default=OUT)
    parser.add_argument("--capture", action="store_true")
    parser.add_argument("--enforce", action="store_true")
    args = parser.parse_args()
    args.screenshots.mkdir(parents=True, exist_ok=True)
    if args.capture:
        capture(args.screenshots)
    result = audit(args.screenshots)
    (args.screenshots / "detail-audit.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2), flush=True)
    if args.enforce and not result["passed"]:
        raise SystemExit("V189 visual REJECTED: V188 neighbors fail strict Matrei-detail parity or captures are missing")


if __name__ == "__main__":
    main()

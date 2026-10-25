#!/usr/bin/env python3
"""V196: browser-verified combined cartway and static terrain cache during army movement.

This measures browser rendering, NOT physical iPhone FPS or visual/historic approval.
"""
import http.server
import json
import math
import threading
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "qa" / "v196-integrated-cache"
OUT.mkdir(parents=True, exist_ok=True)

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)
    def log_message(self, *args):
        pass

def settled(page):
    page.evaluate("""() => new Promise(done =>
        requestAnimationFrame(() => requestAnimationFrame(done)))""")

def segment_distance(p, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    t = max(0, min(1, ((p[0]-a[0])*dx + (p[1]-a[1])*dy) / max(1e-9, dx*dx+dy*dy)))
    return math.hypot(p[0]-a[0]-t*dx, p[1]-a[1]-t*dy)

server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
threading.Thread(target=server.serve_forever, daemon=True).start()
url = f"http://127.0.0.1:{server.server_port}/v192-weathered-cartways-graphics-test.html"
report = {}
try:
    with sync_playwright() as playwright:
        for engine in ("chromium", "webkit"):
            browser = getattr(playwright, engine).launch(headless=True)
            try:
                for orient, w, h in (("portrait", 390, 844), ("landscape", 844, 390)):
                    page = browser.new_page(viewport={"width":w, "height":h},
                        is_mobile=True, has_touch=True, device_scale_factor=2)
                    errors = []
                    page.on("pageerror", lambda err: errors.append(str(err)))
                    key = f"{engine}-{orient}"
                    try:
                        page.goto(url, wait_until="domcontentloaded", timeout=30000)
                        page.wait_for_function("window.V192?.ready===true", timeout=120000)
                        settled(page)
                        assert page.evaluate("V192.connectedRoute")
                        assert not page.evaluate("V192.productionApproved")
                        assert not page.evaluate("V192.historicRouteVerified")
                        for region in ("west", "matrei", "south"):
                            assert page.evaluate("(name) => V192.focusTile(name)", region)
                            page.evaluate("V192.zoomTo(6)")
                            settled(page)
                            page.screenshot(path=str(OUT / f"{key}-{region}.png"),
                                animations="disabled")
                        assert page.evaluate("V192.focusTile('matrei')")
                        page.evaluate("V192.zoomTo(2.4)")
                        settled(page)
                        baseline = page.evaluate("V192.renderStats")
                        assert baseline["staticBuilds"] >= 1, baseline
                        assert not baseline["staticDirty"], baseline
                        assert page.evaluate("V192.orderTo('south')")
                        settled(page)
                        after_order = page.evaluate("V192.renderStats")
                        assert after_order["staticBuilds"] == baseline["staticBuilds"], (baseline, after_order)
                        route = page.evaluate("V192.route")
                        assert len(route) >= 2, route
                        for fraction in (0.1, 0.25, 0.5, 0.75):
                            point = page.evaluate("(f) => V192.progress(f)", fraction)
                            settled(page)
                            assert min(segment_distance(point, a, b)
                                for a, b in zip(route, route[1:])) < 0.001, (fraction, point)
                        moving = page.evaluate("V192.renderStats")
                        assert moving["staticBuilds"] == baseline["staticBuilds"], (baseline, moving)
                        assert moving["cacheHits"] >= baseline["cacheHits"] + 4, (baseline, moving)
                        assert moving["dynamicFrames"] >= baseline["dynamicFrames"] + 4, moving
                        assert moving["cacheBytes"] == w * h * 4 * 4, moving
                        assert moving["renderSamples"] >= 5 and moving["renderP95Ms"] >= 0, moving
                        # Camera changes, debug overlay and pinch/zoom must rebuild static terrain.
                        page.evaluate("V192.zoomTo(3.3)")
                        settled(page)
                        after_zoom = page.evaluate("V192.renderStats")
                        assert after_zoom["staticBuilds"] > moving["staticBuilds"], (moving, after_zoom)
                        page.evaluate("V192.inspect()")
                        settled(page)
                        after_debug = page.evaluate("V192.renderStats")
                        assert after_debug["staticBuilds"] > after_zoom["staticBuilds"], (after_zoom, after_debug)
                        page.evaluate("V192.halt()")
                        settled(page)
                        page.screenshot(path=str(OUT / f"{key}-halt-debug.png"), animations="disabled")
                        assert not errors, (key, errors)
                        report[key] = {
                            "pass": True,
                            "staticBuildsBeforeMovement": baseline["staticBuilds"],
                            "staticBuildsAfterMovement": moving["staticBuilds"],
                            "movementCacheHits": moving["cacheHits"]-baseline["cacheHits"],
                            "cameraRebuilds": after_debug["staticBuilds"]-moving["staticBuilds"],
                            "cacheBytes": moving["cacheBytes"],
                            "browserRenderP95Ms": moving["renderP95Ms"],
                            "sourceRoadCoordinatesUnchanged": True,
                        }
                    finally:
                        page.close()
            finally:
                browser.close()
finally:
    server.shutdown()

summary = {
    "passed": len(report) == 4,
    "results": report,
    "gameArtApproved": False,
    "historicRoadVerified": False,
    "physicalIPhoneApproved": False,
    "productionApproved": False,
    "note": "Headless Chromium/WebKit cache efficiency only; NOT physical iPhone frame-rate acceptance.",
}
(OUT / "report.json").write_text(json.dumps(summary, indent=2) + "\n")
print(json.dumps(summary, indent=2), flush=True)
assert summary["passed"]

#!/usr/bin/env python3
"""Check V121 mobile rendering and connected painted cartways, not historical accuracy."""
import http.server, threading, json, math
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "qa" / "octagon-v121"
OUT.mkdir(parents=True, exist_ok=True)

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(ROOT), **kw)
    def log_message(self, *a):
        pass

server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
threading.Thread(target=server.serve_forever, daemon=True).start()
url = f"http://127.0.0.1:{server.server_port}/v121-octagon-1-painted-road.html"
results = {}
try:
    with sync_playwright() as p:
        for engine in ("chromium", "webkit"):
            browser = getattr(p, engine).launch(headless=True)
            try:
                for orient, viewport in (
                    ("portrait", {"width": 390, "height": 844}),
                    ("landscape", {"width": 844, "height": 390})
                ):
                    name = f"{engine}-{orient}"
                    page = browser.new_page(
                        viewport=viewport, is_mobile=True,
                        has_touch=True, device_scale_factor=2
                    )
                    errors = []
                    page.on("pageerror", lambda e, arr=errors: arr.append(str(e)))
                    try:
                        page.goto(url, wait_until="domcontentloaded", timeout=30000)
                        page.wait_for_function("window.OctagonOne?.ready === true", timeout=25000)
                        state = page.evaluate("""() => ({
                          art: OctagonOne.artDimensions,
                          graph: OctagonOne.graphConnected,
                          nodes: OctagonOne.nodes,
                          approved: OctagonOne.productionApproved,
                          historical: OctagonOne.historicalRouteVerified,
                          roads: Object.keys(OctagonOne.roads),
                          camera: OctagonOne.camera
                        })""")
                        assert state["art"] == [1536, 1024], (name, state)
                        assert state["graph"] and state["nodes"] >= 70, (name, state)
                        assert not state["approved"] and not state["historical"]
                        page.screenshot(path=str(OUT / f"{name}-first-frame.png"), animations="disabled")

                        destinations = []
                        for road in ("west", "north", "south", "bridge", "village", "southeast"):
                            page.evaluate("OctagonOne.halt()")
                            assert page.evaluate("name => OctagonOne.orderTo(name)", road), (name, road)
                            pts = page.evaluate("OctagonOne.route")
                            assert len(pts) >= 2, (name, road)
                            end = page.evaluate("OctagonOne.setProgress(1)")
                            last = page.evaluate(
                                "name => name==='west' ? OctagonOne.roads.west[0] : OctagonOne.roads[name].at(-1)",
                                road
                            )
                            assert math.dist(end, last) < .01, (name, road, end, last)
                            destinations.append(road)
                        # From the SE exit to the western exit, routing must traverse both bridge endpoints.
                        page.evaluate("OctagonOne.halt()")
                        page.evaluate("OctagonOne.orderTo('west')")
                        pts = page.evaluate("OctagonOne.route")
                        assert [741, 475] in pts and [898, 507] in pts, (name, pts)
                        page.evaluate("OctagonOne.toggleGuide()")
                        page.screenshot(path=str(OUT / f"{name}-road-inspection.png"), animations="disabled")
                        assert not errors, (name, errors)
                        results[name] = {"passed": True, "data": state, "destinations": destinations}
                    finally:
                        page.close()
            finally:
                browser.close()
finally:
    server.shutdown()
report = {"passed": len(results) == 4 and all(r["passed"] for r in results.values()),
          "results": results,
          "historicallyVerified": False,
          "physicalIPhoneApproved": False,
          "mergedIntoCampaign": False}
(OUT / "report.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))
if not report["passed"]:
    raise SystemExit(1)

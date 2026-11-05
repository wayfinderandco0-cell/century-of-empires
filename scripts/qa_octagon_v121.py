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

                        # Test actual touchscreen tap, not only the test API. 
                        # Project an on-cartway bridge point into CSS pixels at the initial camera.
                        camera = state["camera"]
                        fit_scale = max(viewport["width"] / 1536, viewport["height"] / 1024)
                        tap_x = viewport["width"] / 2 + (813 - camera[0]) * fit_scale
                        tap_y = viewport["height"] / 2 + (486 - camera[1]) * fit_scale
                        page.touchscreen.tap(tap_x, tap_y)
                        page.wait_for_function("OctagonOne.moved === true", timeout=5000)
                        page.evaluate("OctagonOne.halt()")

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
                        # Regression: redirect an army halfway through a painted segment.
                        # The first rerouted point must remain at its exact current position,
                        # and every subsequent progress sample must be on the road artwork graph.
                        page.evaluate("OctagonOne.halt()")
                        reroute = page.evaluate("""() => {
                          if (!OctagonOne.orderTo('south')) return null;
                          const middle = OctagonOne.setProgress(0.37);
                          const deviation = OctagonOne.roadDeviation;
                          if (!OctagonOne.orderTo('village')) return null;
                          return {middle, deviation, route: OctagonOne.route};
                        }""")
                        assert reroute, name
                        assert reroute["deviation"] < 0.001, (name, 'midroad', reroute)
                        assert math.dist(reroute["route"][0], reroute["middle"]) < 0.001, (name, reroute)
                        for fraction in (0, .11, .24, .33, .48, .67, .81, 1):
                            loc = page.evaluate("f => OctagonOne.setProgress(f)", fraction)
                            error = page.evaluate("OctagonOne.roadDeviation")
                            assert error < 0.001, (name, fraction, loc, error)

                        # Mid-segment destinations are not rounded to a nearby waypoint.
                        # A 20px-off-road destination must be rejected by the deterministic API.
                        page.evaluate("OctagonOne.halt()")
                        end_point = [792.5, 482.4125]  # fractional location on bridge approach
                        assert page.evaluate("p => OctagonOne.orderToPoint(p)", end_point), name
                        projected_end = page.evaluate("OctagonOne.targetPosition")
                        assert math.dist(projected_end, end_point) < 0.01, (name, projected_end)
                        arrived = page.evaluate("OctagonOne.setProgress(1)")
                        assert math.dist(arrived, end_point) < 0.01, (name, arrived)
                        assert page.evaluate("OctagonOne.roadDeviation") < .001, name
                        assert not page.evaluate("OctagonOne.orderToPoint([820,220])"), name
                        page.evaluate("OctagonOne.halt()")
                        # From the SE exit to the western exit, routing must traverse both bridge endpoints.
                        # Restore the actual SE origin after exercising midsegment routing above.
                        page.evaluate("OctagonOne.halt()")
                        assert page.evaluate("OctagonOne.orderTo('southeast')")
                        page.evaluate("OctagonOne.setProgress(1)")
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

"""V116 actual V115-JPEG + unified two-branch road QA; Chromium and WebKit iPhone-sized.
Run: python scripts/qa_v116_road_network.py
Screenshots/reports: qa/v116/ . This is NOT an actual iPhone Safari validation.
"""
import http.server
import json
import socketserver
import threading
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = Path(__file__).resolve().parents[1]
OUT = BASE / "qa" / "v116"
OUT.mkdir(parents=True, exist_ok=True)


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(BASE), **kwargs)

    def log_message(self, *args):
        pass


class Server(socketserver.TCPServer):
    allow_reuse_address = True


server = Server(("127.0.0.1", 0), Handler)
threading.Thread(target=server.serve_forever, daemon=True).start()
url = f"http://127.0.0.1:{server.server_address[1]}/v116-bridge-road-centerline-candidate.html"
results = {}
try:
    with sync_playwright() as p:
        for engine in ("chromium", "webkit"):
            browser = getattr(p, engine).launch(headless=True)
            try:
                for size in ((390, 844), (844, 390)):
                    w, h = size
                    name = f"{engine}-{w}x{h}"
                    page = browser.new_page(
                        viewport={"width": w, "height": h},
                        device_scale_factor=2,
                        is_mobile=True,
                        has_touch=True,
                    )
                    js_errors = []
                    page.on("pageerror", lambda err: js_errors.append(str(err)))
                    checks = {}
                    try:
                        page.goto(url, wait_until="domcontentloaded", timeout=30000)
                        page.wait_for_function("window.centuryV116Proof?.ready === true", timeout=20000)
                        checks["real_v115_jpeg_loaded"] = page.evaluate(
                            "document.images.length === 0 && centuryV116Proof.ready"
                        )
                        checks["48_tiles"] = page.evaluate(
                            "centuryV116Proof.index.tiles.length === 48"
                        )
                        checks["two_branches_same_fork"] = page.evaluate("""
                            (() => {
                              const n=centuryV116Proof.roadNetwork;
                              return n.southPathArtPx.slice(0,n.forkIndex+1).every(
                                (p,i)=>p[0]===n.bridgePathArtPx[i][0] &&
                                       p[1]===n.bridgePathArtPx[i][1]);
                            })()""")
                        checks["four_zoom_transform"] = page.evaluate(
                            "centuryV116Proof.sharedTransformError < 0.000001"
                        )
                        checks["initial_bridge_mode"] = page.evaluate(
                            "centuryV116Proof.route === 'bridge' && "
                            "centuryV116Proof.progress >= 0.7"
                        )
                        checks["bridge_candidate_on_manual_painted_reference"] = page.evaluate(
                            "centuryV116Proof.measurePoint([600,781],'bridge') < 4"
                        )
                        page.screenshot(path=str(OUT / f"{name}-bridge.png"), full_page=True)
                        page.locator("#south").click()
                        checks["south_mode"] = page.evaluate(
                            "centuryV116Proof.route === 'south' && "
                            "centuryV116Proof.measurePoint([438,816],'south') < 4"
                        )
                        page.screenshot(path=str(OUT / f"{name}-south.png"), full_page=True)
                        for view in ("whole", "town", "junction", "bridge"):
                            page.locator(f'[data-view="{view}"]').click()
                            checks[f"view_{view}"] = page.evaluate(
                                "centuryV116Proof.sharedTransformError < .000001"
                            )
                        page.locator("#bridgeRoute").click()
                        before = page.evaluate("centuryV116Proof.snapshot.cam")
                        page.mouse.move(130, 270)
                        page.mouse.down()
                        page.mouse.move(130, 340, steps=8)
                        page.mouse.up()
                        after = page.evaluate("centuryV116Proof.snapshot.cam")
                        checks["drag_moves_camera"] = (
                            abs(after[1]-before[1]) > 0.00001
                        )
                        page.locator("#audit").click()
                        page.locator("#mark").click()
                        page.locator("#map").click(position={"x": w//2, "y": h//2})
                        checks["road_annotation_tap"] = page.evaluate(
                            "centuryV116Proof.count === 1"
                        )
                        page.locator("#mark").click()
                        page.locator("#undo").click()
                        checks["road_annotation_undo"] = page.evaluate(
                            "centuryV116Proof.count === 0"
                        )
                        page.locator("#audit").click()
                        page.locator('[data-view="bridge"]').click()
                        if h > w:
                            page.locator("#march").click()
                            page.wait_for_function(
                                "centuryV116Proof.progress >= 1", timeout=14000
                            )
                            checks["army_stops_at_visible_far_bank"] = page.evaluate(
                                "centuryV116Proof.progress === 1 && !centuryV116Proof.moving "
                                "&& JSON.stringify(centuryV116Proof.roadNetwork.bridgePathArtPx.at(-1)) === '[699,799]'"
                            )
                            page.screenshot(path=str(OUT / f"{name}-end-of-crossing.png"))
                        checks["no_js_errors"] = not js_errors
                        results[name] = {
                            "passed": all(checks.values()),
                            "checks": checks,
                            "page_errors": js_errors,
                        }
                    except Exception as exc:
                        results[name] = {
                            "passed": False,
                            "checks": checks,
                            "exception": str(exc),
                            "page_errors": js_errors,
                        }
                    finally:
                        page.close()
            finally:
                browser.close()
finally:
    server.shutdown()

report = {
    "passed": bool(results) and all(result["passed"] for result in results.values()),
    "browser_results": results,
    "artwork_source": "exact V115 embedded JPEG, not synthetic texture",
    "physical_iphone_tested": False,
    "historical_road_verified": False,
    "production_terrain_integrated": False,
}
(OUT / "results.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))
if not report["passed"]:
    raise SystemExit(1)

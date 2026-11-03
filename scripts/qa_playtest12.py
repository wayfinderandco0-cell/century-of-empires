"""Browser smoke tests for the standalone Century of Empires 12-province campaign."""
import contextlib
import functools
import http.server
import pathlib
import threading
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "qa" / "playtest12"
ARTIFACTS.mkdir(parents=True, exist_ok=True)

class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass

def run_engine(browser_type, engine, url):
    browser = browser_type.launch(headless=True)
    ctx = browser.new_context(viewport={"width": 390, "height": 844},
                              device_scale_factor=2, has_touch=True, is_mobile=True)
    page = ctx.new_page()
    errors = []
    page.on("pageerror", lambda err: errors.append(str(err)))
    response = page.goto(url, wait_until="load", timeout=30000)
    assert response and response.status == 200, f"{engine}: missing playtest page"
    page.wait_for_function("!!window.COE && window.COE.imageLoaded", timeout=15000)
    initial = page.evaluate("window.COE.snapshot")
    assert len(initial["owners"]) == 12, f"{engine}: 12 provinces missing"
    assert sum(v == "you" for v in initial["owners"].values()) == 3, f"{engine}: wrong initial ownership"
    assert initial["armyTile"] == "MATREI" and initial["army"] == 650
    assert page.locator("#land").inner_text() == "3 / 12"
    page.screenshot(path=str(ARTIFACTS / f"{engine}-initial.png"))

    # Exercise on-screen zoom controls.
    original_transform = page.locator("#scene").evaluate("(e) => e.style.transform")
    page.locator("#zoomIn").click()
    assert page.locator("#scene").evaluate("(e) => e.style.transform") != original_transform
    page.locator("#fit").click()

    # A real tap on the rendered map must select EAST-01 (middle row, third cell).
    bounds = page.locator("#scene").bounding_box()
    assert bounds, f"{engine}: map is not rendered"
    x = bounds["x"] + bounds["width"] * 720 / 1152
    y = bounds["y"] + bounds["height"] * 327 / 659
    page.touchscreen.tap(x, y)
    page.wait_for_function("window.COE.snapshot.selected === 'EAST-01'")
    assert not page.locator("#act").is_disabled(), f"{engine}: reachable province unavailable"
    page.locator("#act").click()
    page.wait_for_function("!window.COE.movementActive && window.COE.snapshot.owners['EAST-01'] === 'you'",
                           timeout=10000)
    after = page.evaluate("window.COE.snapshot")
    assert sum(v == "you" for v in after["owners"].values()) == 4
    assert after["armyTile"] == "EAST-01"
    assert after["food"] == initial["food"] - 8
    page.screenshot(path=str(ARTIFACTS / f"{engine}-captured.png"))

    page.reload(wait_until="load")
    page.wait_for_function("!!window.COE && window.COE.imageLoaded")
    assert page.evaluate("window.COE.snapshot.owners['EAST-01']") == "you", f"{engine}: save was lost"
    page.locator("#endTurn").click()
    assert page.evaluate("window.COE.snapshot.turn") == 2
    page.evaluate("window.COE.reset()")
    assert page.locator("#land").inner_text() == "3 / 12"
    assert not errors, f"{engine}: JavaScript errors: {errors}"
    print(f"PASS {engine}: map image, touch select, zoom, move/capture, save/reload, turn, reset")
    ctx.close()
    browser.close()

def main():
    handler = functools.partial(QuietHandler, directory=str(ROOT))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    url = f"http://127.0.0.1:{server.server_port}/playtest-12.html"
    try:
        with sync_playwright() as pw:
            for engine in ("webkit", "chromium"):
                run_engine(getattr(pw, engine), engine, url)
    finally:
        server.shutdown()
        server.server_close()

if __name__ == "__main__":
    main()

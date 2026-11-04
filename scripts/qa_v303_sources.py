"""Browser test for V303 source image stability and playable route movement."""
import functools
import http.server
import pathlib
import threading
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "qa" / "v303"
OUT.mkdir(parents=True, exist_ok=True)

class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass

def test(browser_type, engine, url):
    browser = browser_type.launch(headless=True)
    context = browser.new_context(viewport={"width":390,"height":844},device_scale_factor=2,
                                  has_touch=True,is_mobile=True)
    page = context.new_page()
    errors=[]
    page.on("pageerror", lambda e: errors.append(str(e)))
    response = page.goto(url, wait_until="load", timeout=30000)
    assert response and response.status == 200, f"{engine}: unable to load V303 page"
    page.wait_for_function("!!window.COE50 && !!window.COE50ArtState", timeout=20000)
    assets = page.evaluate("window.COE50ArtState")
    assert assets["total"] == 3 and set(assets["loaded"]) == {"west","matrei","south"} and not assets["failed"], f"{engine}: image failures {assets}"
    road = page.evaluate("window.COE50.validateRoads()")
    assert road["ok"] and road["joins"] == 57 and road["connected"] == 50, f"{engine}: road graph {road}"
    assert page.evaluate("COE50.cloneCount") == 50 and page.evaluate("COE50.sourceCount") == 3
    assert page.evaluate("COE50.localArt") is True
    assert page.evaluate("COE50.pathBetween(24,49).length") > 1
    page.locator("#fit").click()
    page.screenshot(path=str(OUT / f"{engine}-all50.png"))
    page.locator("#home").click()
    page.screenshot(path=str(OUT / f"{engine}-matrei.png"))
    page.evaluate("COE50.marchTo(25)")
    page.wait_for_function("COE50.getState().marching", timeout=2000)
    page.screenshot(path=str(OUT / f"{engine}-march.png"))
    page.wait_for_function("!COE50.getState().marching && COE50.getState().armyCell === 25", timeout=15000)
    assert not errors, f"{engine}: JS errors {errors}"
    print(f"PASS {engine}: 3 source images loaded, 50 reachable cells, 57 joins and movement")
    context.close()
    browser.close()

def main():
    server=http.server.ThreadingHTTPServer(("127.0.0.1",0),functools.partial(Quiet,directory=str(ROOT)))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    try:
        url=f"http://127.0.0.1:{server.server_port}/v303-50-octagon-playtest.html"
        with sync_playwright() as p:
            for engine in ("webkit","chromium"):
                test(getattr(p,engine),engine,url)
    finally:
        server.shutdown()
        server.server_close()

if __name__ == "__main__":
    main()

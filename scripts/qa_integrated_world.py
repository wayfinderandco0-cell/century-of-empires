"""Regression for WORLD atlas inside the actual Century of Empires campaign."""
import functools
import http.server
import pathlib
import threading
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "qa" / "integrated-world"
OUT.mkdir(parents=True, exist_ok=True)

class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass

def run(browser_type, name, url, width, height):
    browser = browser_type.launch(headless=True)
    context = browser.new_context(viewport={"width": width, "height": height},
        device_scale_factor=2, is_mobile=True, has_touch=True)
    page = context.new_page()
    errors = []
    page.on("pageerror", lambda exc: errors.append(str(exc)))
    response = page.goto(url + "/index.html", wait_until="domcontentloaded", timeout=60000)
    assert response.status == 200
    page.wait_for_function("window.COEAtlasQA && window.COEAtlasQA.ready",
        timeout=60000)
    geography = page.evaluate("window.COEAtlasQA")
    assert geography["worldFeatureCount"] == 641, geography
    assert geography["worldPolygonCount"] >= 641, geography
    assert page.locator("#worldHistoricalLands path").count() >= 641
    assert page.locator("#mapViewToggle").is_enabled()
    assert page.locator("#worldAtlasGroup").is_hidden()
    page.locator("#startBtn").click()
    page.wait_for_function("document.getElementById('hudNation').textContent !== 'France' || !!localStorage.getItem('century_of_empires_prototype_1780_v1')",
        timeout=10000)
    assert page.locator("#marchBtn").count() == 1
    save_before = page.evaluate("localStorage.getItem('century_of_empires_prototype_1780_v1')")
    assert save_before and '"provinces"' in save_before, "Original campaign was not saved"
    original_provinces = page.evaluate("document.querySelectorAll('#provinces .flag-province').length")
    assert original_provinces >= 25, original_provinces
    page.locator("#mapViewToggle").click()
    assert page.locator("#worldAtlasGroup").is_visible()
    assert page.locator("#mapViewToggle").inner_text() == "Europe"
    assert "1783" in page.locator("#worldAtlasGroup").text_content()
    page.screenshot(path=str(OUT / f"{name}-{width}-world.png"))
    page.locator("#mapViewToggle").click()
    assert page.locator("#worldAtlasGroup").is_hidden()
    assert page.locator("#mapViewToggle").inner_text() == "World"
    page.locator("#mapZoomFit").click()
    page.wait_for_timeout(200)
    frame = page.evaluate("""() => {
      const s=document.getElementById('mapScroll');
      const m=document.getElementById('map');
      return {viewport:s.clientWidth,mapWidth:m.getBoundingClientRect().width,
        roadVisibility:getComputedStyle(document.getElementById('routes')).display}
    }""")
    assert abs(frame["viewport"]-frame["mapWidth"]) <= 2, frame
    assert frame["roadVisibility"] == "none", frame
    assert page.locator("#provinces .flag-province").count() == original_provinces
    assert page.locator("#marchBtn").count() == 1
    assert page.evaluate("localStorage.getItem('century_of_empires_prototype_1780_v1')") == save_before, "Atlas actions mutated the save"
    page.screenshot(path=str(OUT / f"{name}-{width}-europe.png"))
    assert not errors, errors
    print(f"PASS {name} {width}x{height}: {geography['worldFeatureCount']} world features, original {original_provinces} playable towns, fit/world toggle, save unchanged")
    context.close()
    browser.close()

def main():
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0),
        functools.partial(Quiet, directory=str(ROOT)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        url = f"http://127.0.0.1:{server.server_port}"
        with sync_playwright() as pw:
            for name in ("webkit", "chromium"):
                for width, height in ((390,844),(844,390)):
                    run(getattr(pw,name),name,url,width,height)
    finally:
        server.shutdown()
        server.server_close()

if __name__ == "__main__":
    main()

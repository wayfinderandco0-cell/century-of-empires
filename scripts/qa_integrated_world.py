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
    assert not page.locator("#mapViewToggle").is_visible(), "World mode must not occupy playable map UI"
    assert page.locator("#worldAtlasGroup").is_hidden()
    page.locator("#startBtn").click()
    page.wait_for_function("document.getElementById('hudNation').textContent !== 'France' || !!localStorage.getItem('century_of_empires_prototype_1780_v1')",
        timeout=10000)
    assert page.locator("#marchBtn").count() == 1
    assert page.locator("#incomingToggle").count() == 1
    assert "is-collapsed" in (page.locator("#incomingAlert").get_attribute("class") or "")
    save_before = page.evaluate("localStorage.getItem('century_of_empires_prototype_1780_v1')")
    assert save_before and '"provinces"' in save_before, "Original campaign was not saved"
    original_provinces = page.evaluate("document.querySelectorAll('#provinces .flag-province').length")
    assert original_provinces >= 25, original_provinces
    # All 32 interactive provinces remain, without oversized flag art.
    assert page.locator("#provinces .map-city-node").count() == original_provinces
    assert page.locator("#provinces .banner-outline").count() == 0
    assert page.locator("#provinces .town-hit").count() == original_provinces
    assert page.locator("#provinces .town-core").count() == 0, "Gold globe markers still present"
    assert page.locator("#provinces .town-label").count() == 0, "Town names should only appear in selected town details"
    assert page.locator("#provinces .capital-cockade").count() == page.evaluate(
        "JSON.parse(localStorage.getItem('century_of_empires_prototype_1780_v1')).provinces.filter(p=>p.capital).length"
    ), "Circular capital badges missing"
    assert page.locator("#provinces .town-capital-flag").count() == 0, "Square flags remain"
    assert page.locator("#provinces .town-noncapital-dot").count() > 0
    assert page.locator("#nationalLabels clipPath[id^='coec-realm-']").count() >= 15
    assert page.locator("#nationalLabels .atlas-realm-name").first.evaluate(
        "(el) => el.parentNode.hasAttribute('clip-path')"
    )
    assert page.locator("#provinces .capital-cockade circle.cockade-ring").count() >= 12
    assert page.locator("#provinces .tiny-flag-border").count() == 0
    assert page.locator("#nationalLabels .atlas-realm-name").count() >= 15
    assert page.locator("#nationalLabels .atlas-realm-name").evaluate_all(
        "(els) => els.some(el => getComputedStyle(el).display !== 'none')"
    ), "No visible realm labels"
    assert page.locator("#terrainVisual ellipse").count() == 0, "Cartoon mountain or forest shapes still drawn"
    assert page.locator("#naturalDetails path").count() == 0, "Schematic bright rivers still drawn"
    assert page.locator("#brennerLensPin").evaluate("(el) => getComputedStyle(el).display") == "none"
    page.evaluate("document.getElementById('mapViewToggle').click()")
    assert page.locator("#worldAtlasGroup").is_visible()
    assert page.locator("#mapViewToggle").inner_text() == "Europe"
    assert "1783" in page.locator("#worldAtlasGroup").text_content()
    assert page.locator("#worldHistoricalLands path[data-playable='false']").count() > 200
    assert not page.locator("#worldPlayableCapitals").is_visible()
    page.screenshot(path=str(OUT / f"{name}-{width}-world.png"))
    page.evaluate("document.getElementById('mapViewToggle').click()")
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
    assert frame["roadVisibility"] != "none", "Major roads should be visible at strategic zoom"
    if height > width:
        margin = page.locator("#map").evaluate("(el) => parseFloat(el.style.marginTop)||0")
        assert margin > 150, f"Portrait fitted map not centered: {margin}"
    assert page.locator("#provinces .flag-province").count() == original_provinces
    assert page.locator("#nationalLabels text").count() >= 4, "Strategic nation labels missing"
    assert page.locator("#mapRoutesToggle").count() == 1, "Movement route control missing"
    assert page.locator("#routes path").count() >= 50, "Route topology failed to draw"
    # Fit intentionally hides the regional movement network; zoom to inspect it.
    for _ in range(4):
        page.locator("#mapZoomIn").click()
    assert page.evaluate("document.getElementById('map').getBoundingClientRect().width") > 900
    # Country names remain; town labels never appear at any zoom level.
    assert page.locator("#nationalLabels .atlas-realm-name").count() >= 15
    assert page.locator("#provinces .town-label").count() == 0
    assert page.locator("#provinces .capital-cockade").count() >= 12
    assert page.locator("#mapRoutesToggle").get_attribute("aria-pressed") == "true"
    visible_routes = page.locator("#routes").evaluate("(el) => getComputedStyle(el).display")
    assert visible_routes != "none", f"Routes should be visible by default: {visible_routes}"
    assert page.locator("#routes path.route").count() >= 50
    assert page.locator("#routes path.route.sea").count() >= 5
    assert page.locator("#routes .alpine-pass").count() == 3
    page.screenshot(path=str(OUT / f"{name}-{width}-regional-routes.png"))
    page.locator("#mapRoutesToggle").click()
    assert page.locator("#mapRoutesToggle").get_attribute("aria-pressed") == "false"
    assert page.locator("#routes").evaluate("(el) => getComputedStyle(el).display") == "none"
    page.locator("#mapRoutesToggle").click()
    assert page.locator("#routes").evaluate("(el) => getComputedStyle(el).display") != "none"
    page.locator("#mapZoomFit").click()
    assert page.locator("#nationalLabels").evaluate("(el) => getComputedStyle(el).display") != "none"
    assert page.locator("#marchBtn").count() == 1
    assert page.evaluate("localStorage.getItem('century_of_empires_prototype_1780_v1')") == save_before, "Atlas actions mutated the save"
    page.screenshot(path=str(OUT / f"{name}-{width}-europe.png"))
    # At deep zoom, roundels and political labels must stay small in *screen* pixels.
    for _ in range(4):
        page.locator("#mapZoomIn").click()
    bounds = page.evaluate("""() => {
      const visible = el => getComputedStyle(el).display !== 'none' &&
        el.getBoundingClientRect().width > 0;
      const labels=[...document.querySelectorAll('#nationalLabels .atlas-realm-name')].filter(visible);
      const caps=[...document.querySelectorAll('#provinces .capital-cockade')].filter(visible);
      const w=elems=>elems.map(el=>el.getBoundingClientRect().width);
      const h=elems=>elems.map(el=>el.getBoundingClientRect().height);
      return {labelCount:labels.length,capCount:caps.length,
        maxLabelWidth:Math.max(0,...w(labels)),maxLabelHeight:Math.max(0,...h(labels)),
        maxCapitalWidth:Math.max(0,...w(caps)),
        nonplayable:document.querySelectorAll('#historyPolygons [data-playable="false"]').length};
    }""")
    assert bounds["maxLabelWidth"] <= 175, bounds
    assert bounds["maxLabelHeight"] <= 25, bounds
    assert bounds["maxCapitalWidth"] <= 22, bounds
    assert bounds["nonplayable"] > 0, bounds
    page.screenshot(path=str(OUT / f"{name}-{width}-deep-zoom.png"))
    page.locator("#mapZoomFit").click()
    # Issue a genuine order through the current campaign UI, not a separate simulation.
    page.evaluate("""() => {
      const paris = document.querySelector('#provinces .flag-province[aria-label^="Paris,"]');
      if (!paris) throw Error('Paris troop marker not found');
      paris.dispatchEvent(new MouseEvent('click', {bubbles:true}));
      document.getElementById('marchBtn').click();
      document.getElementById('ownMarchContinue').click();
      const bordeaux = document.querySelector('#provinces .flag-province[aria-label^="Bordeaux,"]');
      if (!bordeaux) throw Error('Bordeaux destination marker not found');
      bordeaux.dispatchEvent(new MouseEvent('click', {bubbles:true}));
    }""")
    order = page.evaluate("""() => {
      const save=JSON.parse(localStorage.getItem('century_of_empires_prototype_1780_v1'));
      return save.orders.find(o => o.from==='paris' && o.to==='bordeaux');
    }""")
    assert order and order["totalEta"] >= 1, f"Marching order missing: {order}"
    assert page.locator("#travel .army-click").count() >= 1
    first_position = page.locator("#travel .army-click").first.get_attribute("transform")
    page.wait_for_timeout(1200)
    second_position = page.locator("#travel .army-click").first.get_attribute("transform")
    assert first_position != second_position, (first_position, second_position)
    page.screenshot(path=str(OUT / f"{name}-{width}-actual-march.png"))
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

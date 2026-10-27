#!/usr/bin/env python3
"""V242 four-browser integration: imported photo artwork must be visible, not hidden.

V224 fixtures are previously rejected CC BY 4.0 studies (SUHEJLO); they are
used solely to prove image-layer integration, NEVER as accepted Alpine art.
"""
import http.server
import json
import threading
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "qa/v242-photo-import"
CONFIGS = (("chromium", "portrait", 390, 844),
           ("chromium", "landscape", 844, 390),
           ("webkit", "portrait", 390, 844),
           ("webkit", "landscape", 844, 390))
FIXTURES = {
    "west": ROOT / "terrain-v224/assets/west.webp",
    "south": ROOT / "terrain-v224/assets/south.webp",
}
FALSE_FLAGS = ("productionApproved", "sourceRegisteredToV123",
               "historicalRoadsVerified", "bridgeBanksVerified",
               "humanVisualApproval", "physicalIPhoneApproved")


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)
    def log_message(self, *args):
        pass


def crop_rgb(path):
    with Image.open(path) as img:
        w, h = img.size
        return np.asarray(img.convert("RGB").crop(
            (int(w * .30), int(h * .28), int(w * .70), int(h * .68))),
            dtype=np.int16)


def difference(before, after):
    a, b = crop_rgb(before), crop_rgb(after)
    if a.shape != b.shape:
        raise AssertionError("Viewport changed")
    return round(float(np.abs(a - b).mean()), 3)


def capture(page, tile, dest):
    assert page.evaluate("(id) => V192.focusTile(id)", tile)
    page.evaluate("V192.zoomTo(6)")
    assert page.evaluate("V192.snapshotForReview()")
    page.screenshot(path=str(dest), animations="disabled")
    return page.evaluate("V192.terrainCamera")


def run():
    OUT.mkdir(parents=True, exist_ok=True)
    for tile, path in FIXTURES.items():
        assert path.is_file(), (tile, path)
        with Image.open(path) as img:
            assert img.size == (1536, 1024), (tile, img.size)
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{server.server_port}/v242-photo-art-import-playtest.html?reviewCapture=1"
    report = {"version": 242, "technicalPassed": False,
              "purpose": "VISIBLE_IMPORT_INTEGRATION_ONLY",
              "fixtureSource": "REJECTED V224 SUHEJLO CC BY 4.0 artwork",
              "productionApproved": False, "humanVisualApproval": False,
              "geographicRegistrationVerified": False,
              "historicRoadsVerified": False, "bridgeBanksVerified": False,
              "configurations": {}}
    try:
        with sync_playwright() as pw:
            for engine, orientation, w, h in CONFIGS:
                key = engine + "-" + orientation
                browser = getattr(pw, engine).launch(headless=True)
                page = browser.new_page(
                    viewport={"width": w, "height": h},
                    device_scale_factor=2, is_mobile=True, has_touch=True)
                errors = []
                page.on("pageerror", lambda e: errors.append(str(e)))
                try:
                    page.goto(url, wait_until="domcontentloaded", timeout=30000)
                    page.wait_for_function("window.V192?.ready === true", timeout=180000)
                    nodes = page.evaluate("V192.roadNodeCount")
                    endpoints = page.evaluate("V192.destinations()")
                    cameras = {}
                    for tile in ("west", "matrei", "south"):
                        cameras[tile] = capture(page, tile, OUT / f"{key}-{tile}-before.png")
                    for tile, selector in (("west", "#westArt"), ("south", "#southArt")):
                        page.set_input_files(selector, str(FIXTURES[tile]))
                        page.wait_for_function(
                            "(id) => V192.v227ArtImport.cells.some(x => x && x.id === id)",
                            arg=tile, timeout=30000)
                    record = page.evaluate("V192.v227ArtImport")
                    assert len([x for x in record["cells"] if x]) == 2, key
                    assert all(record[flag] is False for flag in FALSE_FLAGS), key
                    for cell in record["cells"]:
                        assert cell["dimensions"] == [1536, 1024], key
                        assert cell["productionApproved"] is False, key
                        assert cell["sourceRegisteredToV123"] is False, key
                    scores = {}
                    for tile in ("west", "matrei", "south"):
                        cam = capture(page, tile, OUT / f"{key}-{tile}-close.png")
                        assert cam == cameras[tile], (key, tile, "camera drift")
                        scores[tile] = difference(
                            OUT / f"{key}-{tile}-before.png",
                            OUT / f"{key}-{tile}-close.png")
                    assert scores["west"] > 8.0, (key, "WEST imported image hidden", scores)
                    assert scores["south"] > 8.0, (key, "SOUTH imported image hidden", scores)
                    assert scores["matrei"] < 0.001, (key, "Matrei modified", scores)
                    assert page.evaluate("V192.roadNodeCount") == nodes, key
                    assert page.evaluate("V192.destinations()") == endpoints, key
                    assert page.evaluate("V192.orderTo('south')") is True, key
                    for fraction in (.2, .5, .8):
                        p = page.evaluate("(f) => V192.progress(f)", fraction)
                        assert page.evaluate("(p) => V192.roadDistance(p)", p) < .001
                    assert not errors, (key, errors)
                    report["configurations"][key] = {
                        "importedWestAndSouthVisible": True,
                        "meanPixelDifference": scores,
                        "MatreiPixelsAndCameraPreserved": True,
                        "V123GraphAndArmyMovementPreserved": True,
                        "allApprovalsFalse": True,
                    }
                finally:
                    page.close()
                    browser.close()
    finally:
        server.shutdown()
    sources = [OUT / f"webkit-portrait-{tile}-close.png"
               for tile in ("west", "matrei", "south")]
    if all(p.exists() for p in sources):
        contact = Image.new("RGB", (1170, 680), "#14241e")
        d = ImageDraw.Draw(contact)
        for i, (tile, path) in enumerate(zip(("west", "matrei", "south"), sources)):
            with Image.open(path) as im:
                contact.paste(im.convert("RGB").resize((390, 650)), (390*i, 30))
            d.text((390*i+8, 8), tile.upper() + " - UNAPPROVED", fill="white")
        contact.save(OUT / "actual-webkit-three-cell-import.jpg", quality=85)
    report["technicalPassed"] = len(report["configurations"]) == 4
    (OUT / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2), flush=True)
    assert report["technicalPassed"]


if __name__ == "__main__":
    run()

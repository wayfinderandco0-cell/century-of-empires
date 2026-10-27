#!/usr/bin/env python3
"""V248: real browser pixels distinguish unverified native roads from playable V123 ink.

The V224 CC BY 4.0 fixture images are REJECTED as game art. This tests only the
inspection/playable-mode separation; it cannot verify real geography or bridges.
"""
import http.server
import json
import threading
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "qa/v248-native-road-review"
CONFIGS = (("chromium", "portrait", 390, 844),
           ("chromium", "landscape", 844, 390),
           ("webkit", "portrait", 390, 844),
           ("webkit", "landscape", 844, 390))
FIXTURES = {"west": ROOT / "terrain-v224/assets/west.webp",
            "south": ROOT / "terrain-v224/assets/south.webp"}


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def log_message(self, *args):
        pass


def mean_difference(a, b):
    with Image.open(a) as aa, Image.open(b) as bb:
        x, y = np.asarray(aa.convert("RGB"), dtype=np.int16), np.asarray(bb.convert("RGB"), dtype=np.int16)
    assert x.shape == y.shape
    # Exclude browser header/footer UI changes from pixel evidence.
    h, w, _ = x.shape
    return round(float(np.abs(x[int(h * .20):int(h * .77), int(w * .15):int(w * .85)] -
                                   y[int(h * .20):int(h * .77), int(w * .15):int(w * .85)]).mean()), 5)


def capture(page, tile, path):
    assert page.evaluate("(id)=>V192.focusTile(id)", tile)
    page.evaluate("V192.zoomTo(3.3)")
    assert page.evaluate("V192.snapshotForReview()")
    page.screenshot(path=str(path), animations="disabled")
    return page.evaluate("V192.terrainCamera")


def run():
    OUT.mkdir(parents=True, exist_ok=True)
    for p in FIXTURES.values():
        with Image.open(p) as im:
            assert im.size == (1536, 1024)
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{server.server_port}/v248-native-cartway-inspection.html?reviewCapture=1"
    report = {"version": 248, "purpose": "RAW_SOURCE_ROAD_VS_PLAYABLE_V123_INSPECTION",
              "fixture": "REJECTED V224 SUHEJLO CC BY 4.0 (not accepted artwork)",
              "productionApproved": False, "sourceRegisteredToV123": False,
              "historicalRoadsVerified": False, "bridgeBanksVerified": False,
              "humanVisualApproval": False, "physicalIPhoneApproved": False,
              "configurations": {}}
    try:
        with sync_playwright() as pw:
            for engine, orientation, w, h in CONFIGS:
                key = engine + "-" + orientation
                browser = getattr(pw, engine).launch(headless=True)
                page = browser.new_page(viewport={"width": w, "height": h},
                                        device_scale_factor=2, is_mobile=True, has_touch=True)
                errors = []
                page.on("pageerror", lambda e: errors.append(str(e)))
                try:
                    page.goto(url, wait_until="domcontentloaded", timeout=30000)
                    page.wait_for_function("window.V192?.ready===true", timeout=180000)
                    assert page.evaluate("V192.setRawArtReview(true)") is False, key
                    assert page.evaluate("V192.rawArtReview") is False
                    nodes = page.evaluate("V192.roadNodeCount")
                    destinations = page.evaluate("V192.destinations()")
                    for tile, selector in (("west", "#westArt"), ("south", "#southArt")):
                        page.set_input_files(selector, str(FIXTURES[tile]))
                        page.wait_for_function(
                            "(id)=>V192.v227ArtImport.cells.some(c=>c&&c.id===id)",
                            arg=tile, timeout=30000)
                    snapshot = page.evaluate("V192.v227ArtImport")
                    assert len([c for c in snapshot["cells"] if c]) == 2
                    assert all(c["productionApproved"] is False for c in snapshot["cells"])
                    route_cameras = {}
                    for tile in ("west", "matrei", "south"):
                        route_cameras[tile] = capture(page, tile, OUT / f"{key}-{tile}-close.png")
                    assert page.evaluate("V192.setRawArtReview(true)") is True
                    assert page.evaluate("V192.rawArtReview") is True
                    assert page.evaluate("V192.orderTo('south')") is False, "raw mode must not issue gameplay commands"
                    p = page.evaluate("V192.point")
                    assert page.evaluate("(p)=>V192.tapRoadWorld(p)", p) is False
                    scores = {}
                    for tile in ("west", "matrei", "south"):
                        cam = capture(page, tile, OUT / f"{key}-{tile}-native.png")
                        assert cam == route_cameras[tile], (key, tile, "camera drift")
                        scores[tile] = mean_difference(
                            OUT / f"{key}-{tile}-close.png",
                            OUT / f"{key}-{tile}-native.png")
                    assert scores["west"] > .01, (key, "WEST native road did not change", scores)
                    assert scores["south"] > .01, (key, "SOUTH native road did not change", scores)
                    assert scores["matrei"] < .001, (key, "Matrei changed", scores)
                    assert page.evaluate("V192.setRawArtReview(false)") is True
                    assert page.evaluate("V192.orderTo('south')") is True
                    for f in (.2, .5, .8):
                        point = page.evaluate("(f)=>V192.progress(f)", f)
                        assert page.evaluate("(p)=>V192.roadDistance(p)", point) < .001
                    assert page.evaluate("V192.roadNodeCount") == nodes
                    assert page.evaluate("V192.destinations()") == destinations
                    assert page.evaluate("V192.productionApproved") is False
                    assert not errors, (key, errors)
                    report["configurations"][key] = {
                        "rawNativePixelsVisiblyDifferentFromPaintedRoute": scores,
                        "MatreiUnchanged": True, "rawReviewArmyOrdersBlocked": True,
                        "V123RoutingRestoredAfterReview": True, "allApprovalsFalse": True}
                finally:
                    page.close()
                    browser.close()
    finally:
        server.shutdown()
    imgs = [OUT / f"webkit-portrait-{tile}-native.png" for tile in ("west", "matrei", "south")]
    if all(p.exists() for p in imgs):
        contact = Image.new("RGB", (1170, 680), "#14241e")
        d = ImageDraw.Draw(contact)
        for i, (tile, path) in enumerate(zip(("west", "matrei", "south"), imgs)):
            with Image.open(path) as im:
                contact.paste(im.convert("RGB").resize((390, 650)), (390 * i, 30))
            d.text((390 * i + 8, 8), tile.upper() + " RAW SOURCE (REJECTED)", fill="white")
        contact.save(OUT / "actual-webkit-native-roads-UNAPPROVED.jpg", quality=85)
    report["technicalPassed"] = len(report["configurations"]) == 4
    (OUT / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2), flush=True)
    assert report["technicalPassed"]


if __name__ == "__main__":
    run()

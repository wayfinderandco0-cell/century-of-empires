#!/usr/bin/env python3
"""V213 real game-camera/mobile review UI QA; modern tiles are SYNTHETIC TEST STUBS.

Never treats a placeholder image, a visual match, or a passing UI test as
geographic registration, 1780 source, physical iPhone, or art approval.
"""
import http.server
import io
import json
import subprocess
import threading
from pathlib import Path
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "qa" / "v213-review-ui"
OUT.mkdir(parents=True, exist_ok=True)
PINNED = {
    "v121-octagon-1-painted-road.html": "4c6aa5cda9e7c359b6d2a49d5b5fe8a597346382",
    "terrain-grid/v123-atlas.js": "09f04b4062e24fbacbb645307462cdddce2b2aa3",
}
for path, expected in PINNED.items():
    assert subprocess.check_output(["git", "hash-object", path], cwd=ROOT, text=True).strip() == expected

image = Image.new("RGB", (256, 256), (71, 77, 70))
draw = ImageDraw.Draw(image)
draw.text((10, 12), "SYNTHETIC TEST TILE", fill=(250, 222, 180))
draw.text((10, 34), "NOT REAL ALPINE SOURCE", fill=(250, 222, 180))
buffer = io.BytesIO()
image.save(buffer, "JPEG")
STUB_JPEG = buffer.getvalue()

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)
    def log_message(self, *args):
        pass

server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
threading.Thread(target=server.serve_forever, daemon=True).start()
url = f"http://127.0.0.1:{server.server_port}/v213-landmark-geographic-review.html"
results = {}
try:
    with sync_playwright() as playwright:
        for engine in ("chromium", "webkit"):
            browser = getattr(playwright, engine).launch(headless=True)
            try:
                for orientation, width, height in (("portrait", 390, 844), ("landscape", 844, 390)):
                    key = f"{engine}-{orientation}"
                    page = browser.new_page(viewport={"width": width, "height": height},
                                            is_mobile=True, has_touch=True, device_scale_factor=2)
                    errors = []
                    page.on("pageerror", lambda err: errors.append(str(err)))
                    # Match by hostname, not a fragile URL glob. Never allow a
                    # synthetic test tile to be mistaken for a real source.
                    page.route("**/*", lambda route: (
                        route.fulfill(status=200, content_type="image/jpeg", body=STUB_JPEG)
                        if route.request.url.startswith("https://mapsneu.wien.gv.at/")
                        else route.continue_()))
                    try:
                        page.goto(url, wait_until="domcontentloaded", timeout=30000)
                        try:
                            page.wait_for_function("window.V213 && V213.ready", timeout=45000)
                        except Exception as exc:
                            # Preserve actionable evidence even when the review
                            # UI fails to initialize. This is NOT a passing test.
                            diagnostics = page.evaluate("""() => ({
                                href: location.href,
                                title: document.title,
                                v213: window.V213 ? V213.diagnostics : null,
                                frameHref: document.querySelector('#gameFrame')?.contentWindow?.location?.href,
                                frameAPI: !!document.querySelector('#gameFrame')?.contentWindow?.V192,
                                body: document.querySelector('#state')?.textContent
                            })""")
                            diagnostics["pageErrors"] = errors
                            (OUT / f"{key}-LOAD-FAILURE.json").write_text(
                                json.dumps(diagnostics, indent=2) + "\\n")
                            page.screenshot(path=str(OUT / f"{key}-LOAD-FAILURE.png"),
                                            animations="disabled", full_page=True)
                            raise AssertionError(f"{key} review UI not ready: {diagnostics}") from exc
                        assert page.evaluate("document.querySelector(\'#gameFrame\').contentWindow.V192.reviewCapture") is True
                        assert page.evaluate("V213.cell") == "matrei"
                        assert page.evaluate("V213.loadedTiles") == 4
                        assert page.evaluate("V213.inside([1537,1],V213.polygon([1536,0]))") is False
                        assert page.evaluate("V213.inside([2300,1500],V213.polygon([1536,1024]))") is True
                        assert page.evaluate("V213.sourceAt([256,256],'west')") == [256, 256]
                        assert page.evaluate("V213.sourceAt([256,256],'matrei')") == [768, 256]
                        assert page.evaluate("V213.sourceAt([256,256],'south')") == [768, 768]
                        for cell in ("west", "matrei", "south"):
                            page.evaluate("(name) => V213.setCell(name)", cell)
                            page.wait_for_function("(name) => V213.ready && V213.cell === name", arg=cell, timeout=150000)
                            camera = page.evaluate("V213.camera")
                            assert camera["scale"] > 0 and camera["viewport"][0] > 0
                            center = camera["center"]
                            assert page.evaluate("(p)=>V213.inside(p,V213.polygon(" +
                                                 "({west:[0,0],matrei:[1536,0],south:[1536,1024]})[V213.cell]))",
                                                 center), (key, cell, center)
                            # Click exact live camera center in the real game screenshot.
                            page.evaluate("""() => {
                              const el=document.querySelector('#gameCanvas'),r=el.getBoundingClientRect();
                              el.dispatchEvent(new MouseEvent('click',{bubbles:true,
                                clientX:r.left+r.width/2,clientY:r.top+r.height/2}));
                            }""")
                            pending = page.evaluate("V213.pending")
                            assert pending and abs(pending["gameWorldXY"][0]-center[0]) < 0.03, (key, cell, pending)
                            page.evaluate("""() => {
                              const el=document.querySelector('#sourcePanel'),r=el.getBoundingClientRect();
                              const e=new MouseEvent('click',{bubbles:true,
                                clientX:r.left+r.width/2,clientY:r.top+r.height/2});
                              // MouseEvent.clientX/Y are integer CSS pixels on
                              // WebKit; preserve the actual dispatched values.
                              window.__v211SourceEvent={x:e.clientX,y:e.clientY,
                                rect:{left:r.left,top:r.top,width:r.width,height:r.height}};
                              el.dispatchEvent(e);
                            }""")
                            report = page.evaluate("V213.observations")
                            assert len(report["matches"][cell]) == 1, (key, cell, report)
                            actual = report["matches"][cell][0]["sourceContactXY"]
                            click = page.evaluate("window.__v211SourceEvent")
                            offsets = {"west": [0, 0], "matrei": [512, 0],
                                       "south": [512, 512]}[cell]
                            rect = click["rect"]
                            expected = [
                                round(offsets[0] + (click["x"] - rect["left"]) * 512 / rect["width"], 2),
                                round(offsets[1] + (click["y"] - rect["top"]) * 512 / rect["height"], 2),
                            ]
                            # Test the actual DOM event mapping, not an idealized
                            # fractional click. WebKit quantizes MouseEvent CSS
                            # client coordinates to integers on small iPhones.
                            assert actual == expected, (key, cell, actual, expected, click)
                            geo = report["matches"][cell][0]["sourceGeo"]
                            origin = {"west": [139398, 92095],
                                      "matrei": [139400, 92095],
                                      "south": [139400, 92097]}[cell]
                            assert geo["sourceCell"] == cell
                            assert geo["sourceStatus"] == "MODERN_NATIVE_XYZ_NOT_REGISTERED_TO_GAME"
                            assert geo["gameGeographyVerified"] is False
                            assert geo["historicalGeographyVerified"] is False
                            offset = {"west": [0, 0], "matrei": [512, 0],
                                      "south": [512, 512]}[cell]
                            assert geo["nativeXYZ"] == [
                                origin[0] + int((actual[0] - offset[0]) // 256),
                                origin[1] + int((actual[1] - offset[1]) // 256), 18]
                            centers = {"west": [11.435394287109375, 47.1000446940252],
                                       "matrei": [11.438140869140625, 47.1000446940252],
                                       "south": [11.438140869140625, 47.09817500706038]}
                            assert abs(geo["lon"] - centers[cell][0]) < 0.00001
                            assert abs(geo["lat"] - centers[cell][1]) < 0.00001
                            assert "MODERN SOURCE ONLY" in page.locator("#geoReadout").inner_text()
                            assert report["schemaVersion"] == 213
                            nominal = [offsets[0] + 256, offsets[1] + 256]
                            assert all(abs(a - b) <= 2 for a, b in zip(actual, nominal)), (
                                key, cell, actual, nominal, click)
                            assert report["matches"][cell][0]["evidenceStatus"] == (
                                "UNVERIFIED_VISUAL_OBSERVATION_NOT_INDEPENDENTLY_MATCHED")
                            assert all(report[flag] is False for flag in (
                                "sourceRegisteredToV123", "historicalRoadsVerified", "bridgeBanksVerified",
                                "gameArtApproved", "physicalIPhoneApproved", "productionApproved"))
                            # Snapshot is labeled SYNTHETIC TEST TILE and is not an authentic aerial review.
                            page.screenshot(path=str(OUT / f"{key}-{cell}-SYNTHETIC-SOURCE-TEST.png"),
                                            animations="disabled", full_page=True)
                        assert not errors, (key, errors)
                        results[key] = {"passed": True, "cells": 3,
                                        "liveCameraCoordinates": True, "clippedPolygonChecked": True,
                                        "modernTiles": "SYNTHETIC_TEST_STUBS_NOT_REAL_SOURCE",
                                        "geographicApproval": False, "artApproval": False}
                    finally:
                        page.close()
            finally:
                browser.close()
finally:
    server.shutdown()

report = {
    "version": 210, "passed": len(results) == 4, "results": results,
    "sourceTilesAuthenticInQAScreenshots": False,
    "sourceRegisteredToV123": False, "historicalRoadsVerified": False,
    "gameArtApproved": False, "physicalIPhoneApproved": False, "productionApproved": False,
    "note": "V213 source-coordinate UI test with clearly labeled synthetic tile stubs; native source requires authenticated V213 capture.",
}
(OUT / "report.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2), flush=True)
assert report["passed"]

#!/usr/bin/env python3
"""V213: REAL modern Alpine source in four mobile review captures, NOT game art.

Original native JPEG bytes are downloaded and SHA-256 audited with V204/V205.
Playwright serves those exact bytes to the existing V213 browser review UI.
No synthetic placeholder, stretch, registration, historical road or approval.
"""
import hashlib
import http.server
import json
import threading
from pathlib import Path
from urllib.parse import urlsplit

from playwright.sync_api import sync_playwright
import v204_contiguous_matrei_sources as source

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "qa/v213-authentic-source-phone"
NATIVE = OUT / "native-original-jpegs"
OUT.mkdir(parents=True, exist_ok=True)
CELLS = ("west", "matrei", "south")
FLAGS = ("sourceRegisteredToV123", "historicalRoadsVerified", "bridgeBanksVerified",
         "gameArtApproved", "physicalIPhoneApproved", "productionApproved")


def source_bytes():
    """Return only independently hashed native XYZ JPEG bytes, never stubs."""
    source.verify_source_invariants("forest")
    manifest = source.plan("forest")
    source.download(manifest, NATIVE)
    source.render(manifest, NATIVE)
    source.verify(NATIVE)
    expected = source.plan("forest")
    by_cell = {}
    mapping = {}
    for cell, actual, planned in zip(CELLS, manifest["panels"], expected["panels"]):
        assert actual["nativeOriginXYZ"] == planned["nativeOriginXYZ"]
        entries = []
        for tile in actual["tiles"]:
            path = NATIVE / tile["name"]
            raw = path.read_bytes()
            digest = hashlib.sha256(raw).hexdigest()
            assert digest == tile["sha256"] and len(raw) == tile["byteCount"]
            assert tile["url"] not in mapping, "overlapping native XYZ tile"
            mapping[tile["url"]] = raw
            entries.append({"xyz": tile["tileXYZ"], "url": tile["url"],
                            "sha256": digest, "bytes": len(raw)})
        by_cell[cell] = entries
    assert len(mapping) == 12 and all(len(v) == 4 for v in by_cell.values())
    assert manifest["sourcePanelsNotRegisteredToV121V123"] is True
    assert all(manifest[k] is False for k in source.FALSE_FLAGS)
    return mapping, by_cell, manifest


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)
    def log_message(self, *args):
        pass


def capture(mapping, tiles, manifest):
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{server.server_port}/v213-landmark-geographic-review.html"
    results = {}
    try:
        with sync_playwright() as playwright:
            for engine in ("chromium", "webkit"):
                browser = getattr(playwright, engine).launch(headless=True)
                try:
                    for orientation, width, height in (("portrait", 390, 844),
                                                        ("landscape", 844, 390)):
                        key = engine + "-" + orientation
                        page = browser.new_page(viewport={"width": width, "height": height},
                                                is_mobile=True, has_touch=True,
                                                device_scale_factor=2)
                        errors, missing, served = [], [], []
                        page.on("pageerror", lambda error: errors.append(str(error)))

                        def intercept(route):
                            target = route.request.url
                            if target in mapping:
                                served.append(target)
                                route.fulfill(status=200, content_type="image/jpeg",
                                              headers={"Access-Control-Allow-Origin": "*"},
                                              body=mapping[target])
                            elif urlsplit(target).hostname == "mapsneu.wien.gv.at":
                                missing.append(target)
                                route.abort()
                            else:
                                route.continue_()

                        page.route("**/*", intercept)
                        try:
                            page.goto(url, wait_until="domcontentloaded", timeout=30000)
                            page.wait_for_function("window.V213 && V213.ready", timeout=120000)
                            assert page.evaluate("document.querySelector('#gameFrame').contentWindow.V192.reviewCapture") is True
                            for cell in CELLS:
                                page.evaluate("(name) => V213.setCell(name)", cell)
                                page.wait_for_function("(name) => V213.ready && V213.cell === name",
                                                       arg=cell, timeout=120000)
                                actual = page.evaluate("""() => ({
                                    images:[...document.querySelectorAll('#sourcePanel img')]
                                        .map(i=>({url:i.currentSrc,ok:i.complete,
                                                  width:i.naturalWidth,height:i.naturalHeight})),
                                    camera:V213.camera,report:V213.observations,
                                    gamePixels:[document.querySelector('#gameCanvas').width,
                                                document.querySelector('#gameCanvas').height]
                                })""")
                                assert len(actual["images"]) == 4
                                assert set(i["url"] for i in actual["images"]) == set(
                                    item["url"] for item in tiles[cell])
                                assert all(i["ok"] and i["width"] == 256 and i["height"] == 256
                                           for i in actual["images"]), (key, cell, actual["images"])
                                assert actual["camera"]["scale"] > 0
                                assert actual["gamePixels"] == [640, 450]
                                assert actual["report"]["status"] == "UNVERIFIED_VISUAL_OBSERVATIONS_ONLY"
                                assert all(actual["report"][flag] is False for flag in FLAGS)
                                assert actual["report"]["matches"][cell] == []
                                assert "MODERN SOURCE ONLY" in page.locator("#geoReadout").inner_text()
                                # Exercise real DOM click coordinates against original JPEG
                                # tiles; the pair is a QA gesture, NOT an observed match.
                                page.evaluate("""() => {
                                  const el=document.querySelector('#gameCanvas');
                                  const r=el.getBoundingClientRect();
                                  el.dispatchEvent(new MouseEvent('click',{bubbles:true,
                                    clientX:r.left+r.width/2,clientY:r.top+r.height/2}));
                                }""")
                                page.evaluate("""() => {
                                  const el=document.querySelector('#sourcePanel');
                                  const r=el.getBoundingClientRect();
                                  el.dispatchEvent(new MouseEvent('click',{bubbles:true,
                                    clientX:r.left+r.width/2,clientY:r.top+r.height/2}));
                                }""")
                                paired = page.evaluate("V213.observations.matches[V213.cell]")
                                assert len(paired) == 1, (key, cell, paired)
                                geo = paired[0]["sourceGeo"]
                                native = {"west": [139399, 92096, 18],
                                          "matrei": [139401, 92096, 18],
                                          "south": [139401, 92098, 18]}[cell]
                                assert geo["nativeXYZ"] == native
                                assert geo["gameGeographyVerified"] is False
                                assert geo["historicalGeographyVerified"] is False
                                assert paired[0]["evidenceStatus"] == "UNVERIFIED_VISUAL_OBSERVATION_NOT_INDEPENDENTLY_MATCHED"
                                # Remove artificial QA click pair before capturing
                                # authentic source evidence; do not imply a landmark match.
                                page.locator("#clear").click()
                                assert page.evaluate("V213.observations.matches[V213.cell]") == []
                                path = OUT / f"{key}-{cell}-REAL-MODERN-SOURCE-NOT-REGISTERED.png"
                                page.screenshot(path=str(path), animations="disabled",
                                                full_page=True, timeout=30000)
                                assert path.stat().st_size > 15000
                            assert not errors and not missing, (key, errors, missing)
                            assert set(served) == set(mapping), (key, "missing native tile")
                            results[key] = {"passed": True, "cells": 3,
                                            "source": "ORIGINAL_NATIVE_JPEG_SHA256_AUDITED",
                                            "modernNotHistorical": True,
                                            "gameCamera": "ORIGINAL_V192_RENDERER",
                                            "approval": False}
                        except Exception:
                            page.screenshot(path=str(OUT / f"{key}-FAIL-CAPTURE.png"),
                                            full_page=True, timeout=30000)
                            (OUT / f"{key}-FAIL.json").write_text(json.dumps({
                                "errors": errors, "missing": missing, "served": served,
                                "status": page.evaluate(
                                    "window.V213 ? V213.diagnostics : {ready:false}")}, indent=2))
                            raise
                        finally:
                            page.close()
                finally:
                    browser.close()
    finally:
        server.shutdown()
    return results


def main():
    mapping, tiles, manifest = source_bytes()
    report = {
        "version": 213, "date": "2026-10-26",
        "source": "V205 forest modern basemap.at native XYZ zoom 18",
        "license": "CC BY 4.0; Datenquelle: basemap.at",
        "sourceManifestSha256": hashlib.sha256(
            (NATIVE / "manifest.json").read_bytes()).hexdigest(),
        "nativeTileEvidence": tiles,
        "sourceRegisteredToV123": False, "historicalRoadsVerified": False,
        "bridgeBanksVerified": False, "gameArtApproved": False,
        "physicalIPhoneApproved": False, "productionApproved": False,
        "historicalPeriodProven": False,
        "gameCells": "V123 ORIGINAL ART ONLY; source images NOT copied into game",
        "sourceAnchorLonLat": manifest["anchorLonLat"],
        "sourcePanelsNotRegisteredToV121V123": True,
    }
    try:
        report["browserResults"] = capture(mapping, tiles, manifest)
        report["passed"] = len(report["browserResults"]) == 4
    finally:
        (OUT / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"passed": report["passed"], "browserResults": report["browserResults"],
                      "sourceRegisteredToV123": False, "gameArtApproved": False}, indent=2))
    assert report["passed"]


if __name__ == "__main__":
    main()

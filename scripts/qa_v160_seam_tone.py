#!/usr/bin/env python3
"""V160 phone-browser tonal-study QA. NOT a game-art or historical approval."""
import http.server
import json
import threading
from pathlib import Path
from PIL import Image, ImageChops, ImageStat
from playwright.sync_api import sync_playwright

root = Path(__file__).resolve().parents[1]
out = root / "qa/v160-seam"
out.mkdir(parents=True, exist_ok=True)
class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(root), **kwargs)
    def log_message(self, *args):
        pass

server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
threading.Thread(target=server.serve_forever, daemon=True).start()
base_url = f"http://127.0.0.1:{server.server_port}/"
results = {}
try:
    with sync_playwright() as pw:
        for engine in ("chromium", "webkit"):
            browser = getattr(pw, engine).launch(headless=True)
            try:
                for orientation, w, h in (("portrait", 390, 844), ("landscape", 844, 390)):
                    prefix = f"{engine}-{orientation}"
                    screenshots = {}
                    report = None
                    for variant, filename in (("original", "v137-coherent-alpine-preview.html"),
                                              ("study", "v160-matrei-seam-study.html")):
                        page = browser.new_page(viewport={"width": w, "height": h},
                            is_mobile=True, has_touch=True, device_scale_factor=2)
                        errors = []
                        page.on("pageerror", lambda error: errors.append(str(error)))
                        page.goto(base_url + filename, wait_until="domcontentloaded", timeout=30000)
                        page.wait_for_function("window.V137?.ready === true", timeout=60000)
                        assert page.evaluate("V137.artDimensions") == [1536, 1024]
                        assert page.evaluate("V137.connectedRoute")
                        assert page.evaluate("V137.productionApproved") is False
                        assert all(x["pass"] for x in page.evaluate("V137.seamStatus"))
                        if variant == "study":
                            report = page.evaluate("V137.seamToneReport")
                            assert report["version"] == 160 and report["anchors"] >= 20
                            assert report["changedBackgroundPixels"] > 500
                            assert report["photoModified"] is False
                            assert report["roadsModified"] is False
                            assert report["productionApproved"] is False
                        else:
                            assert page.evaluate("V137.seamToneReport === undefined")
                        for region in (("matrei",) if variant == "original"
                                       else ("west", "matrei", "south")):
                            assert page.evaluate("(r) => V137.focusTile(r)", region)
                            page.evaluate("() => new Promise(done => requestAnimationFrame(() => requestAnimationFrame(done)))")
                            path = out / f"{prefix}-{region}-terrain.png" if variant == "study" else out / f"{prefix}-original-matrei.png"
                            page.screenshot(path=str(path), animations="disabled")
                            if region == "matrei":
                                screenshots[variant] = path
                        if variant == "study":
                            page.locator("#options").click()
                            page.locator("#whole").click()
                            page.evaluate("() => new Promise(done => requestAnimationFrame(() => requestAnimationFrame(done)))")
                            page.screenshot(path=str(out / f"{prefix}-whole-crossing.png"), animations="disabled")
                            assert page.evaluate("V137.orderTo('west')")
                            page.evaluate("V137.progress(1)")
                            assert page.evaluate("V137.orderTo('south')")
                            page.evaluate("V137.progress(1)")
                        assert not errors, (prefix, variant, errors)
                        page.close()
                    with Image.open(screenshots["original"]) as old, Image.open(screenshots["study"]) as new:
                        diff = ImageChops.difference(old.convert("RGB"), new.convert("RGB"))
                        average_delta = sum(ImageStat.Stat(diff).mean) / 3
                        assert 0.01 < average_delta < 30, (prefix, average_delta)
                    results[prefix] = {"technicalPass": True, "seamToneReport": report,
                                       "meanScreenChannelDelta": round(average_delta, 4)}
            finally:
                browser.close()
finally:
    server.shutdown()
summary = {"technicalPassed": len(results) == 4, "configurations": results,
           "historicalGeoregistration": False, "threeGameOctagonsVisuallyApproved": False,
           "physicalIPhoneApproved": False, "productionApproved": False,
           "note": "Color harmonization only; V140 neighbor-detail parity remains a separate fail-closed acceptance gate."}
(out / "report.json").write_text(json.dumps(summary, indent=2) + "\n")
print(json.dumps(summary, indent=2))
assert summary["technicalPassed"]

#!/usr/bin/env python3
"""V175: four real phone-browser views of the V173 masked geographic SOURCE L.
Never a historical game-art, V123 road, bridge or physical iPhone acceptance test.
Requires genuine 18-JPEG source + modern exclusion + V174 LOD outputs in CI.
"""
import http.server
import json
import threading
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
MODERN = ROOT / "qa/v169-modern-source-L"
LOD = ROOT / "qa/v174-source-lod"
OUT = ROOT / "qa/v175-masked-source-phone"
OUT.mkdir(parents=True, exist_ok=True)

modern = json.loads((MODERN / "manifest.json").read_text())
lod = json.loads((LOD / "manifest.json").read_text())
assert modern["version"] == 169 and lod["version"] == 174
assert lod["sourceMaskSha256"] == modern["maskSha256"]
assert lod["sourceReferenceSha256"] == modern["referenceSha256"]
assert modern["sourceCrs"] == "EPSG:3857"
assert modern["modernInfrastructureCleared"] is False
assert lod["sourceToV123TransformVerified"] is False
assert all(not t["gameArtEligible"] for t in lod["tiers"])
with Image.open(MODERN / modern["studyFile"]) as im:
    assert im.format == "PNG" and im.mode == "RGBA" and im.size == (1536, 1024)
    source_alpha = im.getchannel("A")
with Image.open(MODERN / modern["maskFile"]) as im:
    assert im.mode == "L" and im.size == (1536, 1024)
    assert source_alpha.tobytes() == im.tobytes(), "modern/unknown alpha was filled"

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)
    def log_message(self, *args):
        pass

server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
threading.Thread(target=server.serve_forever, daemon=True).start()
url = f"http://127.0.0.1:{server.server_port}/v175-masked-source-review.html"
results = {}
try:
    with sync_playwright() as p:
        for engine in ("chromium", "webkit"):
            browser = getattr(p, engine).launch(headless=True)
            try:
                for orientation, width, height in (("portrait", 390, 844), ("landscape", 844, 390)):
                    page = browser.new_page(viewport={"width": width, "height": height},
                                            is_mobile=True, has_touch=True, device_scale_factor=2)
                    errors = []
                    page.on("pageerror", lambda e: errors.append(str(e)))
                    page.goto(url, wait_until="domcontentloaded", timeout=30000)
                    page.wait_for_function("window.V175?.ready === true", timeout=30000)
                    assert page.evaluate("""() => V175.sourceOnly &&
                      !V175.productionApproved && !V175.periodArtComplete &&
                      !V175.historic1780Certified && !V175.v123RoadsGeoregistered &&
                      !V175.bridgeBanksVerified && !V175.physicalIPhoneApproved""")
                    assert page.evaluate("V175.manifest.sourceMosaicSha256 === V175.lod.sourceMosaicSha256")
                    assert page.evaluate("V175.lod.retainedPixelsByBlockRowMajor.length") == 1536
                    assert page.evaluate("V175.sampleAlpha(0,700)") == 0
                    assert page.evaluate("V175.sampleAlpha(1100,400)") == 0
                    assert page.evaluate("V175.sampleAlpha(100,200)") == 255
                    assert page.evaluate("V175.sampleAlpha(1200,200)") == 255
                    assert page.evaluate("V175.sampleAlpha(900,700)") == 255
                    page.evaluate("V175.setTier(0)")
                    page.screenshot(path=str(OUT / f"{engine}-{orientation}-whole-L.png"))
                    for i, (name, center) in enumerate((
                        ("west", (384,256)), ("center", (1152,256)), ("south", (1152,768))
                    )):
                        assert page.evaluate("([i]) => V175.focusSector(i,3)", [i])
                        xy = page.evaluate("""() => V175.screenToSource(
                          document.querySelector('#map').clientWidth/2,
                          document.querySelector('#map').clientHeight/2)""")
                        assert max(abs(a-b) for a,b in zip(xy,center)) < 0.01, (name,xy)
                        page.screenshot(path=str(OUT / f"{engine}-{orientation}-{name}.png"))
                    page.evaluate("V175.focusSector(1,2)")
                    before = page.evaluate("""() => V175.screenToSource(
                      document.querySelector('#map').clientWidth/2,
                      document.querySelector('#map').clientHeight/2)""")
                    page.evaluate("V175.setTier(3)")
                    after = page.evaluate("""() => V175.screenToSource(
                      document.querySelector('#map').clientWidth/2,
                      document.querySelector('#map').clientHeight/2)""")
                    assert max(abs(a-b) for a,b in zip(before,after)) < 1e-6
                    assert not errors, errors
                    # Forged approval must be rejected before any image is accepted.
                    bad = browser.new_page(viewport={"width": width, "height": height},
                                           is_mobile=True, has_touch=True)
                    def tamper(route):
                        altered = dict(modern)
                        altered["productionApproved"] = True
                        route.fulfill(json=altered)
                    bad.route("**/qa/v169-modern-source-L/manifest.json", tamper)
                    bad.goto(url, wait_until="domcontentloaded", timeout=30000)
                    bad.wait_for_function("window.V175?.failure", timeout=20000)
                    assert bad.evaluate("!V175.ready && V175.failure.includes('Unapproved claim')")
                    bad.close()
                    results[f"{engine}-{orientation}"] = {
                        "three_real_source_centers": True,
                        "four_tier_zoom_anchor": True,
                        "unknown_and_modern_holes_stay_transparent": True,
                        "forged_approval_rejected": True,
                        "game_art_approved": False,
                        "physical_iPhone_approved": False,
                    }
                    page.close()
            finally:
                browser.close()
finally:
    server.shutdown()

assert len(results) == 4
(OUT / "report.json").write_text(json.dumps({
    "version":175,"source":"modern basemap.at L with exclusions",
    "results":results,"gameArtApproved":False,"physicalIPhoneApproved":False,
    "sourceToV123TransformVerified":False,"historicalRoadsVerified":False,
}, indent=2) + "\n")
print("V175 PASS: 4/4 simulated iPhone layouts; 12 authentic masked source center views, 4 whole-L views; NOT game-art acceptance")

#!/usr/bin/env python3
"""V177: four phone-browser A/B comparisons of real masked SOURCE vs tonal candidate.
Never a historical game-art, V123 road, bridge or physical iPhone acceptance test.
Requires genuine 18-JPEG source + modern exclusion + V174 LOD outputs in CI.
"""
import http.server
import json
import threading
from pathlib import Path

from PIL import Image, ImageChops
from v176_source_tonal_candidate import verify as verify_tonal
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
MODERN = ROOT / "qa/v169-modern-source-L"
LOD = ROOT / "qa/v174-source-lod"
TONAL = ROOT / "qa/v176-tonal-candidate"
OUT = ROOT / "qa/v177-source-tonal-phone"
OUT.mkdir(parents=True, exist_ok=True)

verify_tonal(MODERN, LOD, TONAL)
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
url = f"http://127.0.0.1:{server.server_port}/v177-source-tonal-ab-review.html"
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
                    page.wait_for_function("window.V177?.ready === true", timeout=30000)
                    assert page.evaluate("""() => V177.sourceOnly &&
                      !V177.productionApproved && !V177.periodArtComplete &&
                      !V177.historic1780Certified && !V177.v123RoadsGeoregistered &&
                      !V177.bridgeBanksVerified && !V177.physicalIPhoneApproved""")
                    assert page.evaluate("V177.manifest.sourceMosaicSha256 === V177.lod.sourceMosaicSha256")
                    assert page.evaluate("V177.lod.retainedPixelsByBlockRowMajor.length") == 1536
                    assert page.evaluate("V177.tonalManifest.gameArtEligible") is False
                    assert page.evaluate("V177.tonalManifest.sourceStudySha256 === V177.manifest.studySha256")
                    assert page.evaluate("V177.pixelEvidence.retained > 900000 && V177.pixelEvidence.altered > 100000")
                    assert page.evaluate("V177.sampleAlpha(0,700)") == 0
                    assert page.evaluate("V177.sampleAlpha(1100,400)") == 0
                    assert page.evaluate("V177.sampleAlpha(100,200)") == 255
                    assert page.evaluate("V177.sampleAlpha(1200,200)") == 255
                    assert page.evaluate("V177.sampleAlpha(900,700)") == 255
                    page.evaluate("V177.setTier(0)")
                    for mode in ("original","tonal"):
                        assert page.evaluate("([mode]) => V177.switchMode(mode)", [mode])
                        page.screenshot(path=str(OUT / f"{engine}-{orientation}-whole-L-{mode}.png"))
                    for i, (name, center) in enumerate((
                        ("west", (384,256)), ("center", (1152,256)), ("south", (1152,768))
                    )):
                        assert page.evaluate("([i]) => V177.focusSector(i,3)", [i])
                        xy = page.evaluate("""() => V177.screenToSource(
                          document.querySelector('#map').clientWidth/2,
                          document.querySelector('#map').clientHeight/2)""")
                        assert max(abs(a-b) for a,b in zip(xy,center)) < 0.01, (name,xy)
                        for mode in ("original","tonal"):
                            assert page.evaluate("([mode]) => V177.switchMode(mode)", [mode])
                            page.screenshot(path=str(OUT / f"{engine}-{orientation}-{name}-{mode}.png"))
                        original = Image.open(OUT / f"{engine}-{orientation}-{name}-original.png").convert("RGB")
                        tonal = Image.open(OUT / f"{engine}-{orientation}-{name}-tonal.png").convert("RGB")
                        # Compare actual canvas pixels, excluding mode text in the header.
                        canvas_region = (0, 208, original.width, original.height - 52)
                        assert ImageChops.difference(original.crop(canvas_region),
                                                     tonal.crop(canvas_region)).getbbox(), name
                    page.evaluate("V177.focusSector(1,2)")
                    before = page.evaluate("""() => V177.screenToSource(
                      document.querySelector('#map').clientWidth/2,
                      document.querySelector('#map').clientHeight/2)""")
                    page.evaluate("V177.setTier(3)")
                    after = page.evaluate("""() => V177.screenToSource(
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
                    bad.wait_for_function("window.V177?.failure", timeout=20000)
                    assert bad.evaluate("!V177.ready && V177.failure.includes('Unapproved claim')")
                    bad.close()
                    forged = browser.new_page(viewport={"width": width, "height": height},
                                              is_mobile=True, has_touch=True)
                    def tamper_candidate(route):
                        changed = json.loads((TONAL / "manifest.json").read_text())
                        changed["gameArtEligible"] = True
                        route.fulfill(json=changed)
                    forged.route("**/qa/v176-tonal-candidate/manifest.json", tamper_candidate)
                    forged.goto(url, wait_until="domcontentloaded", timeout=30000)
                    forged.wait_for_function("window.V177?.failure", timeout=20000)
                    assert forged.evaluate("!V177.ready && V177.failure.includes('Unapproved tonal candidate')")
                    forged.close()
                    results[f"{engine}-{orientation}"] = {
                        "three_real_source_centers": True,
                        "source_tonal_pair_per_center": True,
                        "candidate_alpha_and_provenance_verified": True,
                        "forged_candidate_rejected": True,
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
    "version":177,"source":"masked modern basemap.at SOURCE L vs V176 tonal candidate; not game",
    "results":results,"gameArtApproved":False,"physicalIPhoneApproved":False,
    "sourceToV123TransformVerified":False,"historicalRoadsVerified":False,
}, indent=2) + "\n")
print("V177 PASS: 4/4 simulated phone layouts; 24 paired sector and 8 whole-L screenshots; NOT game-art acceptance")

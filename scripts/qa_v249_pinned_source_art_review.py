#!/usr/bin/env python3
"""V249: four real browsers exercise SHA-pinned two-image URL review (ART RED).

Fixtures are previously REJECTED V224 photographs. Passing is a transport,
pixel-visibility and immutable-gameplay test, NOT an artwork or history pass.
"""
import hashlib
import http.server
import json
import threading
from pathlib import Path
from urllib.parse import urlencode

from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "qa/v249-pinned-source-review"
CONFIGS = (("chromium", "portrait", 390, 844),
           ("chromium", "landscape", 844, 390),
           ("webkit", "portrait", 390, 844),
           ("webkit", "landscape", 844, 390))
FILES = {"west": ROOT / "terrain-v224/assets/west.webp",
         "south": ROOT / "terrain-v224/assets/south.webp"}


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def log_message(self, *args):
        pass


def query(south_hash_override=None):
    hashes = {tile: hashlib.sha256(path.read_bytes()).hexdigest()
              for tile, path in FILES.items()}
    if south_hash_override:
        hashes["south"] = south_hash_override
    return urlencode({
        "reviewCapture": "1",
        "westSrc": "/terrain-v224/assets/west.webp",
        "southSrc": "/terrain-v224/assets/south.webp",
        "westSha256": hashes["west"],
        "southSha256": hashes["south"],
    }), hashes


def run():
    OUT.mkdir(parents=True, exist_ok=True)
    for path in FILES.values():
        with Image.open(path) as image:
            assert image.size == (1536, 1024), path
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{server.server_port}/v249-pinned-source-art-review.html?"
    good_query, expected_hashes = query()
    bad_query, _ = query("0" * 64)
    report = {
        "version": 249, "purpose": "PINNED_IPHONE_OPENABLE_UNAPPROVED_ART_REVIEW",
        "fixture": "V224 REJECTED SUHEJLO CC BY 4.0, NOT PERIOD OR ROAD VERIFIED",
        "sourceRegisteredToV123": False, "bridgeBanksVerified": False,
        "historicalRoadsVerified": False, "productionApproved": False,
        "humanVisualApproval": False, "physicalIPhoneApproved": False,
        "configurations": {}, "negativeShaRejected": False,
    }
    try:
        with sync_playwright() as playwright:
            for browser_name, orientation, width, height in CONFIGS:
                key = browser_name + "-" + orientation
                browser = getattr(playwright, browser_name).launch(headless=True)
                page = browser.new_page(viewport={"width": width, "height": height},
                                        device_scale_factor=1, is_mobile=True,
                                        has_touch=True)
                errors = []
                page.on("pageerror", lambda e: errors.append(str(e)))
                try:
                    page.goto(base + good_query, wait_until="domcontentloaded", timeout=30000)
                    page.wait_for_function(
                        "window.V192?.ready && V192.pinnedSourceReview.state==='loaded'",
                        timeout=180000)
                    review = page.evaluate("V192.pinnedSourceReview")
                    assert len(review["sources"]) == 2, (key, review)
                    assert {x["id"]: x["sha256"] for x in review["sources"]} == expected_hashes
                    assert page.evaluate("V192.rawArtReview") is True
                    assert page.evaluate("V192.productionApproved") is False
                    assert page.evaluate("V192.physicalIPhoneApproved") is False
                    assert page.evaluate("V192.orderTo('south')") is False
                    assert page.evaluate("V192.v227ArtImport.productionApproved") is False
                    assert all(not c["licenseVerified"] and not c["sourceRegisteredToV123"]
                               for c in page.evaluate("V192.v227ArtImport.cells"))
                    for tile in ("west", "matrei", "south"):
                        assert page.evaluate("(id)=>V192.focusTile(id)", tile)
                        page.evaluate("V192.zoomTo(3.3)")
                        assert page.evaluate("V192.snapshotForReview()")
                        page.screenshot(path=str(OUT / f"{key}-{tile}-close.png"),
                                        animations="disabled")
                    assert page.evaluate("V192.setRawArtReview(false)") is True
                    assert page.evaluate("V192.orderTo('south')") is True
                    for f in (.25, .55, .85):
                        point = page.evaluate("(f)=>V192.progress(f)", f)
                        assert page.evaluate("(p)=>V192.roadDistance(p)", point) < .001
                    assert not errors, (key, errors)
                    report["configurations"][key] = {
                        "twoExactByteShaPinsMatched": True,
                        "sourceRoadReviewEnabled": True,
                        "MatreiProtected": True,
                        "V123RoutingRestored": True,
                        "productionApproved": False,
                    }
                finally:
                    page.close()
                    browser.close()
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 390, "height": 844})
            try:
                page.goto(base + bad_query, wait_until="domcontentloaded")
                page.wait_for_function(
                    "window.V192?.ready && V192.pinnedSourceReview.state==='rejected'",
                    timeout=180000)
                assert page.evaluate("V192.rawArtReview") is False
                assert all(c is None for c in page.evaluate("V192.v227ArtImport.cells"))
                report["negativeShaRejected"] = True
            finally:
                page.close()
                browser.close()
    finally:
        server.shutdown()
    imgs = [OUT / f"webkit-portrait-{tile}-close.png"
            for tile in ("west", "matrei", "south")]
    if all(p.exists() for p in imgs):
        sheet = Image.new("RGB", (1170, 680), "#14241e")
        pen = ImageDraw.Draw(sheet)
        for i, (tile, path) in enumerate(zip(("west", "matrei", "south"), imgs)):
            with Image.open(path) as im:
                sheet.paste(im.convert("RGB").resize((390, 650)), (i * 390, 30))
            pen.text((i * 390 + 8, 8), tile.upper() + " SHA-PINNED RAW SOURCE (REJECTED)", fill="white")
        sheet.save(OUT / "actual-webkit-pinned-source-UNAPPROVED.jpg", quality=85)
    report["technicalPassed"] = len(report["configurations"]) == 4 and report["negativeShaRejected"]
    (OUT / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2), flush=True)
    assert report["technicalPassed"]


if __name__ == "__main__":
    run()

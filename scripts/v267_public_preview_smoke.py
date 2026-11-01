#!/usr/bin/env python3
"""Nonblocking public CDN smoke check of the exact iPhone review link.

A successful local WebKit test does NOT prove raw.githack's cached URL works.
Do not promote candidate status based on this smoke test alone.
"""
import json
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"terrain-grid/v267-original-art-batch-01"
URL=("https://raw.githack.com/wayfinderandco0-cell/century-of-empires/"
     "terrain-v267-three-original-art-prototype-20261028/index.html"
     "?originalArtPilot=v267-new&autoOpen=1")
report={"schema":"coe-v267-public-safari-smoke/v1",
        "url":URL,"publicPreviewRendered":False,
        "source":"raw.githack.com (public branch URL, not local server)",
        "browser":"Playwright WebKit 390x844 @2x",
        "notes":"Public CDN is a separate check from successful local WebKit rendering"}
try:
    with sync_playwright() as pw:
        browser=pw.webkit.launch(headless=True)
        page=browser.new_page(viewport={"width":390,"height":844},
                              device_scale_factor=2,is_mobile=True,has_touch=True)
        errors=[]
        page.on("pageerror",lambda error:errors.append(str(error)))
        page.goto(URL,wait_until="domcontentloaded",timeout=35000)
        page.wait_for_function("""() => {
          const a=window.COEAtlas,im=document.getElementById('atlasRidgeDomFallback');
          return a&&a.loaded&&a.shown&&a.originalNeighborVisible&&im&&
            im.complete&&im.naturalWidth===1536&&im.naturalHeight===1024;
        }""",timeout=45000)
        page.wait_for_timeout(300)
        rect=page.locator("#atlasRidgeDomFallback").bounding_box()
        if not rect or rect["width"]<150 or rect["height"]<100:
            raise RuntimeError("Ridge image is decoded but outside usable viewport")
        if rect["x"]>=390 or rect["x"]+rect["width"]<=0 or rect["y"]>=844 or rect["y"]+rect["height"]<=0:
            raise RuntimeError("Ridge image does not intersect the viewport")
        screenshot=OUT/"actual-webkit-public-githack-ridge.png"
        page.screenshot(path=str(screenshot))
        if screenshot.stat().st_size<30000:
            raise RuntimeError("Public screenshot unexpectedly small")
        report["publicPreviewRendered"]=True
        report["ridgeImageBoxCssPx"]={k:round(v,1) for k,v in rect.items()}
        report["screenshot"]=str(screenshot.relative_to(ROOT))
        report["pageErrors"]=errors[:5]
        browser.close()
except Exception as exc:
    report["error"]=str(exc)[:450]
finally:
    (OUT/"public-githack-smoke.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report))

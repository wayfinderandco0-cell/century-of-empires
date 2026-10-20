#!/usr/bin/env python3
"""Render and test V99 closest zoom in a mobile Chromium browser."""
import base64, io, json, time
from pathlib import Path
from PIL import Image, ImageStat
from playwright.sync_api import sync_playwright

output=Path("terrain-v99")
output.mkdir(exist_ok=True)
errors=[]
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,args=["--no-sandbox"])
    page=browser.new_page(viewport={"width":393,"height":852},device_scale_factor=1,
                         is_mobile=True,has_touch=True)
    page.on("pageerror",lambda err:errors.append(str(err)))
    page.goto("http://127.0.0.1:8765/v99-brenner-real-trees-streams.html",wait_until="domcontentloaded",timeout=35000)
    page.locator("button[data-level='3']").click()
    try:page.wait_for_function("""() => [...document.querySelectorAll('#tileLayer img')]
                            .filter(im=>im.complete&&im.naturalWidth>0).length>=3
                            && document.querySelectorAll('#streamLayer path').length>=4
                            """,timeout=45000)
    except Exception as e:
        print("TILES OR STREAMS NOT LOADED",str(e)[:160],flush=True)
    page.wait_for_timeout(1700)
    tally=page.evaluate("""() => ({loaded:[...document.querySelectorAll('#tileLayer img')].filter(x=>x.complete&&x.naturalWidth>0).length,
      failed:[...document.querySelectorAll('#tileLayer img')].filter(x=>x.complete&&!x.naturalWidth).length,
      total:document.querySelectorAll('#tileLayer img').length,
      riverPaths:document.querySelectorAll('#streamLayer path').length,
      photoVisible:getComputedStyle(document.querySelector('#photoStage')).display!=='none',
      status:document.querySelector('#photoStatus').innerText,
      label:document.querySelector('#levelName').innerText
    })""")
    png=page.screenshot(full_page=True)
    browser.close()
im=Image.open(io.BytesIO(png)).convert("RGB")
stats=ImageStat.Stat(im.crop((20,140,370,690)))
report={"browserErrors":errors,"tileStatus":tally,"colorVariance":stats.var,"width":im.width,"height":im.height}
print("V99 MOBILE QA:",json.dumps(report),flush=True)
(output/"qa-mobile-report.json").write_text(json.dumps(report,indent=2)+"\n")
resized=im.resize((393,round(393*im.height/im.width)))
out=io.BytesIO();resized.save(out,format="WEBP",quality=65,method=4)
(output/"qa-mobile-base64.txt").write_text(base64.b64encode(out.getvalue()).decode("ascii"))
assert not errors,"Browser JavaScript failed"
assert tally["loaded"]>=3,"Real photographic map tiles did not load"
assert tally["riverPaths"]>=4,"Real stream linework missing from photo map"
assert tally["photoVisible"],"Photo layer hidden at zoom level 4"
assert max(stats.var)>150,"Screenshot is visually flat/blank"
print("V99 REAL MOBILE BROWSER RENDER VERIFIED",flush=True)

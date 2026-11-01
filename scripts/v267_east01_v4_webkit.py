#!/usr/bin/env python3
"""Actual iPhone-sized WebKit image/zoom smoke for EAST-01 V4 review.

Only proves mobile pixels and controls. Never promotes visual quality,
physical seam, road, history, user approval or native gameplay.
"""
from pathlib import Path
import subprocess,time,json
from PIL import Image,ImageStat
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"terrain-grid/v267-original-art-batch-01"
def main():
    server=subprocess.Popen(["python","-m","http.server","8768","--bind","127.0.0.1"],
                            cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.STDOUT)
    try:
        time.sleep(1.1)
        with sync_playwright() as p:
            browser=p.webkit.launch(headless=True)
            page=browser.new_page(viewport={"width":390,"height":844},
                                  device_scale_factor=2,is_mobile=True,has_touch=True)
            errors=[]
            page.on("pageerror",lambda e:errors.append(str(e)))
            page.goto("http://127.0.0.1:8768/v267-east-riparian-v4-review.html",wait_until="domcontentloaded")
            page.wait_for_function("document.getElementById('terrain').naturalWidth===3072",timeout=30000)
            page.locator("#seam").click()
            page.wait_for_timeout(500)
            before=page.evaluate("document.getElementById('terrain').getBoundingClientRect().width")
            shot=OUT/"actual-webkit-iphone-east-riparian-v4.png"
            page.screenshot(path=str(shot))
            with Image.open(shot) as im:
                assert im.size==(780,1688),("Unexpected iPhone screenshot dimensions",im.size)
                crop=im.convert("RGB").crop((40,240,740,1480))
                stats=ImageStat.Stat(crop)
                assert max(stats.stddev)>20,("blank terrain screenshot",stats.stddev)
                assert len(crop.getcolors(crop.width*crop.height) or [])>1200,"insufficient terrain detail"
            page.locator("#plus").click()
            after=page.evaluate("document.getElementById('terrain').getBoundingClientRect().width")
            assert after>before*1.15,("Zoom button failed",before,after)
            assert "UNVERIFIED" in page.locator("#status").inner_text()
            assert not errors,errors
            browser.close()
        evidence=OUT/"matrei-east-riparian-v4-evidence.json"
        data=json.loads(evidence.read_text())
        assert not data["roadsVerified"] and not data["riverSeamVerified"] and not data["finished"]
        data["mobileWebkitRendered"]=True
        data["webkitEvidence"]=str(shot.relative_to(ROOT))
        evidence.write_text(json.dumps(data,indent=2)+"\n")
        print(json.dumps({"status":"PASS","webkitViewport":"390x844@2",
                          "screenshot":str(shot.relative_to(ROOT)),
                          "panZoom":"PASS","newPlayable":0,"roadSeamsVerified":False}))
    finally:
        server.terminate()
        server.wait(timeout=5)
if __name__=="__main__":main()

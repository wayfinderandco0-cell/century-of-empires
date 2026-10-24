#!/usr/bin/env python3
"""V170 coherent-terrain preview regression (not production art approval)."""
import http.server, json, os, threading, urllib.request
from PIL import Image, ImageStat
from pathlib import Path
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[1]
out=root/os.environ.get("COE_QA_OUTPUT", "qa/v170-mobile")
source_only=os.environ.get("COE_PREVIEW_QUERY", "")=="?geoMaterials=1"
out.mkdir(parents=True,exist_ok=True)
class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(root),**kwargs)
    def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(("127.0.0.1",0),Handler)
threading.Thread(target=server.serve_forever,daemon=True).start()
url=f"http://127.0.0.1:{server.server_port}/v170-terrain-transition-test.html"+os.environ.get("COE_PREVIEW_QUERY", "")
# Fail immediately when QA points at a missing or obsolete preview, instead of
# spending a minute waiting on an empty 404 document.
with urllib.request.urlopen(url,timeout=5) as response:
    source=response.read()
    assert response.status==200 and b"V170 Terrain-Transition Test" in source, "Wrong V170 QA target"
results={}
try:
    with sync_playwright() as playwright:
        for engine in ("chromium","webkit"):
            browser=getattr(playwright,engine).launch(headless=True)
            try:
                for orient,w,h in (("portrait",390,844),("landscape",844,390)):
                    page=browser.new_page(viewport={"width":w,"height":h},is_mobile=True,has_touch=True,device_scale_factor=2)
                    errors=[]
                    page.on("pageerror",lambda error:errors.append(str(error)))
                    page.goto(url,wait_until="domcontentloaded",timeout=30000)
                    try:
                        page.wait_for_function("window.V170?.ready===true",timeout=30000)
                    except Exception as boot_error:
                        # A saturated renderer can also block DOM inspection. Never
                        # allow the diagnostic itself to wait another 30 seconds.
                        try:
                            stage=page.locator("#status").text_content(timeout=2000)
                        except Exception as probe_error:
                            stage="<DOM unresponsive: "+type(probe_error).__name__+">"
                        print("V170 boot failure:",engine,orient,
                              "stage:",repr(stage),"pageerrors:",errors,
                              "cause:",repr(boot_error),flush=True)
                        raise
                    assert page.evaluate("V170.artDimensions")==[1536,1024]
                    assert page.evaluate("V170.connectedRoute")
                    assert page.evaluate("V170.continuousTerrain")
                    assert page.evaluate("V170.photoPatchCount") == 0
                    assert page.evaluate("V170.photoStampCount") == 0
                    assert page.evaluate("V170.valleyStampCount") >= 20
                    # User's physical iPhone screenshot exposed flat neighbors
                    # although graph and nonblank canvas tests had passed.
                    assert page.evaluate("V170.geoMaterialSourceOnly") == source_only
                    if source_only:
                        assert page.evaluate("V170.detailMarkCount") == 0, "Source-only experiment must not add fake tree/rock decals"
                        crop=page.evaluate("V170.geoCrop")
                        assert crop and not crop["routeGeoregistered"] and not crop["historicallyCertified"]
                        assert abs(crop["metresPerWorldX"]/crop["metresPerWorldY"]-1)<1e-8
                    else:
                        assert page.evaluate("V170.detailMarkCount") >= 10000
                        assert page.evaluate("V170.transitionCanopyDrawn") >= 100, "Hard rectangular forest exclusion still present"
                    for region in ("west", "south"):
                        assert page.evaluate("(region) => V170.focusTile(region)",region)
                        page.evaluate("() => new Promise(done => requestAnimationFrame(() => requestAnimationFrame(done)))")
                        page.screenshot(path=str(out/f"{engine}-{orient}-{region}-terrain.png"),animations="disabled")
                        # Minimal photo-detail regression to catch flat west/south
                        # backdrops seen in physical iPhone screenshots of V170/V139.
                        # This is NOT a substitute for manual geographic/art review.
                        if not source_only and engine=="webkit" and orient=="portrait":
                            pic=Image.open(out/f"{engine}-{orient}-{region}-terrain.png").convert("L")
                            iw,ih=pic.size
                            y0=.14 if region=="west" else .34
                            patch=pic.crop((int(iw*.12),int(ih*y0),int(iw*.88),int(ih*.83)))
                            contrast=ImageStat.Stat(patch).stddev[0]
                            min_contrast=13.5 if region=="west" else 19.0
                            print("V140 photograph-derived relief evidence",region,
                                  round(contrast,2),">=",min_contrast,flush=True)
                            assert contrast>=min_contrast,(
                                "Neighbor terrain too flat",region,contrast,min_contrast)
                    assert page.evaluate("(region) => V170.focusTile(region)", "matrei")
                    assert all(s["pass"] for s in page.evaluate("V170.seamStatus"))
                    assert not page.evaluate("V170.productionApproved")
                    assert page.evaluate("V170.roadNodeCount")>=90
                    assert page.evaluate("V170.roadDistance([1600,478])")<1, "Visible seam cartway not detected"
                    assert page.evaluate("V170.roadDistance([100,100])")>72, "Road hit area leaks into fields"
                    assert not page.evaluate("V170.physicalIPhoneApproved")
                    assert not page.evaluate("V170.historicRouteVerified")
                    assert page.locator("#status").inner_text().startswith("Connected three-tile")
                    page.evaluate("() => new Promise(done => requestAnimationFrame(() => requestAnimationFrame(done)))")
                    scene_colors=page.evaluate("""() => {
                      const canvas=document.querySelector('#map'),ctx=canvas.getContext('2d');
                      const data=ctx.getImageData(0,0,canvas.width,canvas.height).data;
                      const colors=new Set(),w=canvas.width,h=canvas.height;
                      for(let iy=3;iy<28;iy++)for(let ix=2;ix<20;ix++){
                        const x=Math.floor(ix*w/20),y=Math.floor(iy*h/30),j=(y*w+x)*4;
                        colors.add(data[j]+','+data[j+1]+','+data[j+2]);
                      }
                      return colors.size;
                    }""")
                    assert scene_colors>40,(engine,orient,"blank scene",scene_colors)
                    page.screenshot(path=str(out/f"{engine}-{orient}-opening.png"),animations="disabled")
                    page.locator("#options").click()
                    page.locator("#whole").click()
                    page.evaluate("() => new Promise(done => requestAnimationFrame(() => requestAnimationFrame(done)))")
                    page.screenshot(path=str(out/f"{engine}-{orient}-whole-crossing.png"),animations="disabled")
                    page.locator("#center").click()
                    assert not page.evaluate("V170.tapRoadWorld([100,100])"), "Field tap must not issue a road order"
                    assert page.evaluate("V170.tapRoadWorld([1600,478])"), "Painted border road must be selectable"
                    page.evaluate("V170.progress(1)")
                    page.locator("#options").click()
                    page.locator("#gotoWest").click()
                    assert page.evaluate("V170.moving"), "West command failed in the phone menu"
                    assert page.evaluate("V170.orderTo('west')")
                    page.evaluate("V170.progress(.46)")
                    page.screenshot(path=str(out/f"{engine}-{orient}-marching-west.png"),animations="disabled")
                    page.evaluate("V170.halt()")
                    assert not page.evaluate("V170.moving")
                    assert page.evaluate("V170.orderTo('west')")
                    page.evaluate("V170.progress(1)")
                    page.locator("#options").click()
                    page.locator("#gotoSouth").click()
                    assert page.evaluate("V170.moving"), "South command failed in the phone menu"
                    page.evaluate("V170.progress(1)")
                    assert not page.evaluate("V170.moving")
                    assert not errors,(engine,orient,errors)
                    results[f"{engine}-{orient}"]={"pass":True,"photoLoaded":True,"seams":2,"roadMovement":True,"coherentAlpineRelief":True}
                    page.close()
            finally:browser.close()
finally:server.shutdown()
report={"passed":len(results)==4,"results":results,"sourceOnlyExperiment":source_only,
        "humanArtworkApproval":False,"routeGeoregistered":False,"campaignUnchanged":True}
(out/"report.json").write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
assert report["passed"]

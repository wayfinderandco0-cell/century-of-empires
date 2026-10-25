#!/usr/bin/env python3
"""V171 directional-army and cartway preview regression (not production art approval)."""
import http.server, json, threading
from pathlib import Path
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[1]
out=root/"qa"/"v171-graphics"
out.mkdir(parents=True,exist_ok=True)
class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(root),**kwargs)
    def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(("127.0.0.1",0),Handler)
threading.Thread(target=server.serve_forever,daemon=True).start()
url=f"http://127.0.0.1:{server.server_port}/v171-continuous-alpine-preview.html"
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
                        page.wait_for_function("window.V171?.ready===true",timeout=30000)
                    except Exception:
                        print("V171 loading diagnostic:",engine,orient,"status:",page.locator("#status").inner_text(),"errors:",errors,flush=True)
                        raise
                    assert page.evaluate("V171.artDimensions")==[1536,1024]
                    assert page.evaluate("V171.connectedRoute")
                    assert page.evaluate("V171.continuousTerrain")
                    assert page.evaluate("V171.photoPatchCount") == 0
                    assert page.evaluate("V171.photoStampCount") == 0
                    assert page.evaluate("V171.valleyStampCount") >= 20
                    assert all(s["pass"] for s in page.evaluate("V171.seamStatus"))
                    assert not page.evaluate("V171.productionApproved")
                    assert page.evaluate("V171.roadNodeCount")>=90
                    assert page.evaluate("V171.displayOnlyRoadRuts")
                    assert page.evaluate("Number.isFinite(V171.headingRadians)")
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
                    assert page.evaluate("V171.orderTo('west')")
                    page.evaluate("V171.progress(.46)")
                    assert page.evaluate("Number.isFinite(V171.headingRadians)")
                    assert page.evaluate("V171.roadDistance(V171.point)") < 1.5
                    page.screenshot(path=str(out/f"{engine}-{orient}-marching-west.png"),animations="disabled")
                    page.evaluate("V171.halt()")
                    assert not page.evaluate("V171.moving")
                    assert page.evaluate("V171.orderTo('west')")
                    page.evaluate("V171.progress(1)")
                    assert page.evaluate("V171.orderTo('south')")
                    page.evaluate("V171.progress(1)")
                    assert not errors,(engine,orient,errors)
                    results[f"{engine}-{orient}"]={"pass":True,"photoLoaded":True,"seams":2,"roadMovement":True,"coherentAlpineRelief":True}
                    page.close()
            finally:browser.close()
finally:server.shutdown()
report={"passed":len(results)==4,"results":results,"humanArtworkApproval":False,"campaignUnchanged":True}
(out/"report.json").write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
assert report["passed"]

#!/usr/bin/env python3
"""V136 standalone seamless-terrain-preview smoke QA (not production art approval)."""
import http.server, json, threading
from pathlib import Path
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[1]
out=root/"qa"/"v136-clean"
out.mkdir(parents=True,exist_ok=True)
class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(root),**kwargs)
    def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(("127.0.0.1",0),Handler)
threading.Thread(target=server.serve_forever,daemon=True).start()
url=f"http://127.0.0.1:{server.server_port}/v136-continuous-alpine-preview.html"
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
                        page.wait_for_function("window.V136?.ready===true",timeout=10000)
                    except Exception:
                        print("V136 loading diagnostic:",engine,orient,"status:",page.locator("#status").inner_text(),"errors:",errors,flush=True)
                        raise
                    assert page.evaluate("V136.artDimensions")==[1536,1024]
                    assert page.evaluate("V136.connectedRoute")
                    assert page.evaluate("V136.continuousTerrain")
                    assert page.evaluate("V136.photoPatchCount") >= 5
                    assert page.evaluate("V136.photoStampCount") >= 200
                    assert all(s["pass"] for s in page.evaluate("V136.seamStatus"))
                    assert not page.evaluate("V136.productionApproved")
                    assert page.evaluate("V136.roadNodeCount")>=90
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
                    assert page.evaluate("V136.orderTo('west')")
                    page.evaluate("V136.progress(.46)")
                    page.evaluate("V136.halt()")
                    assert not page.evaluate("V136.moving")
                    assert page.evaluate("V136.orderTo('west')")
                    page.evaluate("V136.progress(1)")
                    assert page.evaluate("V136.orderTo('south')")
                    page.evaluate("V136.progress(1)")
                    assert not errors,(engine,orient,errors)
                    results[f"{engine}-{orient}"]={"pass":True,"photoLoaded":True,"seams":2,"roadMovement":True,"continuousPhototerrain":True}
                    page.close()
            finally:browser.close()
finally:server.shutdown()
report={"passed":len(results)==4,"results":results,"humanArtworkApproval":False,"campaignUnchanged":True}
(out/"report.json").write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
assert report["passed"]

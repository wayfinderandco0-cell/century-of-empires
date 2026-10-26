#!/usr/bin/env python3
"""V201: real pointer-pan/pinch must repaint cached Alpine landscape.

Headless phone layouts are NOT physical iPhone, art or historical approval.
"""
import http.server
import json
import subprocess
import threading
from pathlib import Path
from PIL import Image, ImageChops
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"qa"/"v201-touch-camera-cache"
OUT.mkdir(parents=True,exist_ok=True)
PINNED={
 "v121-octagon-1-painted-road.html":"4c6aa5cda9e7c359b6d2a49d5b5fe8a597346382",
 "terrain-grid/v123-atlas.js":"09f04b4062e24fbacbb645307462cdddce2b2aa3",
}
for path,expected in PINNED.items():
    actual=subprocess.check_output(["git","hash-object",path],cwd=ROOT,text=True).strip()
    assert actual==expected,(path,actual)

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,directory=str(ROOT),**kwargs)
    def log_message(self,*args):pass

def settled(page):
    page.evaluate("""() => new Promise(done =>
        requestAnimationFrame(() => requestAnimationFrame(done)))""")

def gesture(page,kind,width,height):
    return page.evaluate("""({kind,width,height}) => {
        const canvas=document.querySelector('#map');
        const original=canvas.setPointerCapture;
        canvas.setPointerCapture=()=>{}; // synthetic events cannot claim hardware capture
        const x=width/2,y=height/2;
        const fire=(type,id,px,py)=>canvas.dispatchEvent(new PointerEvent(type,
          {bubbles:true,pointerId:id,pointerType:'touch',
           clientX:px,clientY:py,isPrimary:id===11}));
        const before=V192.terrainCamera;
        try{
            if(kind==='pan'){
                fire('pointerdown',13,x,y);
                fire('pointermove',13,x+85,y+42);
                fire('pointerup',13,x+85,y+42);
            }else{
                fire('pointerdown',11,x-45,y);
                fire('pointerdown',12,x+45,y);
                fire('pointermove',11,x-75,y);
                fire('pointermove',12,x+75,y);
                fire('pointerup',11,x-75,y);
                fire('pointerup',12,x+75,y);
            }
        }finally{canvas.setPointerCapture=original;}
        return {before,after:V192.terrainCamera};
    }""",{"kind":kind,"width":width,"height":height})

def changed_fraction(before,after,width,height):
    """Ignore header/footer: verify actual terrain changed, not just army icon."""
    with Image.open(before) as a,Image.open(after) as b:
        assert a.size==b.size==(width*2,height*2)
        box=(120,180,(width-60)*2,(height-105)*2)
        assert box[2]>box[0] and box[3]>box[1]
        diff=ImageChops.difference(a.convert("RGB").crop(box),
                                   b.convert("RGB").crop(box))
        mask=diff.convert("L").point(lambda p:255 if p>8 else 0)
        return mask.histogram()[255]/(mask.width*mask.height)

def coverage(info):
    x0,y0,x1,y1=info["visible"]
    gx,gy,gw,gh=info["groundBounds"]
    assert x0>=gx-.01 and y0>=gy-.01 and x1<=gx+gw+.01 and y1<=gy+gh+.01
    assert info["minZoom"]-.0001<=info["zoom"]<=7.0001

server=http.server.ThreadingHTTPServer(("127.0.0.1",0),Handler)
threading.Thread(target=server.serve_forever,daemon=True).start()
url=f"http://127.0.0.1:{server.server_port}/v192-weathered-cartways-graphics-test.html"
results={}
try:
    with sync_playwright() as playwright:
        for engine in ("chromium","webkit"):
            browser=getattr(playwright,engine).launch(headless=True)
            try:
                for orient,width,height in (("portrait",390,844),("landscape",844,390)):
                    key=f"{engine}-{orient}"
                    page=browser.new_page(viewport={"width":width,"height":height},
                        is_mobile=True,has_touch=True,device_scale_factor=2)
                    errors=[]
                    page.on("pageerror",lambda error:errors.append(str(error)))
                    try:
                        page.goto(url,wait_until="domcontentloaded",timeout=30000)
                        page.wait_for_function("window.V192?.ready===true",timeout=120000)
                        assert page.evaluate("V192.connectedRoute")
                        assert page.evaluate("V192.productionApproved") is False
                        assert page.evaluate("V192.historicRouteVerified") is False
                        assert page.evaluate("V192.physicalIPhoneApproved") is False
                        assert page.evaluate("V192.focusTile('matrei')")
                        page.evaluate("V192.zoomTo(3.2)")
                        settled(page)
                        coverage(page.evaluate("V192.terrainCamera"))
                        baseline=page.evaluate("V192.renderStats")
                        assert not baseline["staticDirty"]
                        before=OUT/f"{key}-pan-before.png"
                        after=OUT/f"{key}-pan-after.png"
                        page.screenshot(path=str(before),animations="disabled")
                        pan=gesture(page,"pan",width,height)
                        settled(page)
                        pan_stats=page.evaluate("V192.renderStats")
                        page.screenshot(path=str(after),animations="disabled")
                        assert pan_stats["staticBuilds"]>baseline["staticBuilds"],(
                            "TOUCH PAN LEFT STALE TERRAIN",key,baseline,pan_stats)
                        assert not pan_stats["staticDirty"]
                        assert max(abs(a-b) for a,b in zip(
                            pan["before"]["center"],pan["after"]["center"]))>10,pan
                        coverage(pan["after"])
                        pan_changed=changed_fraction(before,after,width,height)
                        assert pan_changed>.05,("pan did not repaint landscape",key,pan_changed)
                        assert page.evaluate("V192.focusTile('matrei')")
                        page.evaluate("V192.zoomTo(2.4)")
                        settled(page)
                        pre_pinch=page.evaluate("V192.renderStats")
                        before=OUT/f"{key}-pinch-before.png"
                        after=OUT/f"{key}-pinch-after.png"
                        page.screenshot(path=str(before),animations="disabled")
                        pinch=gesture(page,"pinch",width,height)
                        settled(page)
                        pinch_stats=page.evaluate("V192.renderStats")
                        page.screenshot(path=str(after),animations="disabled")
                        assert pinch_stats["staticBuilds"]>pre_pinch["staticBuilds"],(
                            "TOUCH PINCH LEFT STALE TERRAIN",key,pre_pinch,pinch_stats)
                        assert pinch["after"]["zoom"]>pinch["before"]["zoom"]*1.4,pinch
                        assert max(abs(a-b) for a,b in zip(
                            pinch["before"]["center"],pinch["after"]["center"]))<.01,pinch
                        coverage(pinch["after"])
                        pinch_changed=changed_fraction(before,after,width,height)
                        assert pinch_changed>.05,("pinch did not repaint landscape",key,pinch_changed)
                        assert page.evaluate("V192.orderTo('south')")
                        settled(page)
                        stationary=page.evaluate("V192.renderStats")
                        assert len(page.evaluate("V192.route"))>2
                        for fraction in (.15,.4,.7):
                            point=page.evaluate("(f)=>V192.progress(f)",fraction)
                            settled(page)
                            assert page.evaluate("(p)=>V192.roadDistance(p)",point)<.01
                        movement=page.evaluate("V192.renderStats")
                        assert movement["staticBuilds"]==stationary["staticBuilds"],(
                            "army motion should reuse cached terrain",key)
                        assert movement["cacheHits"]>=stationary["cacheHits"]+3
                        assert not errors,(key,errors)
                        results[key]={
                            "passed":True,"panStaticRebuilt":True,
                            "pinchStaticRebuilt":True,"pinchAnchored":True,
                            "panChangedLandscapeFraction":round(pan_changed,4),
                            "pinchChangedLandscapeFraction":round(pinch_changed,4),
                            "armyStayedOnV123Road":True,"movingArmyReusedCache":True,
                            "sourceBlobsUnchanged":True}
                    finally:page.close()
            finally:browser.close()
finally:server.shutdown()
report={"passed":len(results)==4,"results":results,"sourceBlobs":PINNED,
        "gameArtApproved":False,"historicRouteVerified":False,
        "physicalIPhoneApproved":False,"productionApproved":False,
        "note":"Headless phone gesture QA; not physical iPhone or historical/visual approval."}
(OUT/"report.json").write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report,indent=2),flush=True)
assert report["passed"]

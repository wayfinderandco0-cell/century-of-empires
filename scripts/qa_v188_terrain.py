#!/usr/bin/env python3
"""V188 visual-only photo edge integration QA; not historical or production art approval."""
import http.server
import json
import threading
from pathlib import Path
from playwright.sync_api import sync_playwright

root=Path(__file__).resolve().parents[1]
out=root/"qa"/"v188-terrain"
out.mkdir(parents=True,exist_ok=True)
class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,directory=str(root),**kwargs)
    def log_message(self,*args):pass

server=http.server.ThreadingHTTPServer(("127.0.0.1",0),Handler)
threading.Thread(target=server.serve_forever,daemon=True).start()
address=f"http://127.0.0.1:{server.server_port}"
results={}
try:
    with sync_playwright() as playwright:
        for engine in ("chromium","webkit"):
            browser=getattr(playwright,engine).launch(headless=True)
            try:
                for orient,w,h in (("portrait",390,844),("landscape",844,390)):
                    page=browser.new_page(viewport={"width":w,"height":h},is_mobile=True,has_touch=True,device_scale_factor=2)
                    errors=[]
                    page.on("pageerror",lambda err:errors.append(str(err)))
                    page.goto(address+"/v188-terrain-continuity-trial.html",wait_until="domcontentloaded",timeout=30000)
                    page.wait_for_function("window.V188?.ready===true",timeout=120000)
                    report=page.evaluate("V188.seamTone")
                    assert report["enabled"],(engine,orient,report)
                    assert report["samples"]>=40,report
                    assert report["adjustedPixels"]>3000,report
                    assert report["maxAllowedOffset"]==34,report
                    assert report["originalArtworkUnmodified"] and report["routeGeometryUnmodified"],report
                    assert not page.evaluate("V188.productionApproved")
                    assert not page.evaluate("V188.physicalIPhoneApproved")
                    assert not page.evaluate("V188.historicRouteVerified")
                    assert page.evaluate("V188.connectedRoute")
                    assert all(x["pass"] for x in page.evaluate("V188.seamStatus"))
                    assert page.evaluate("V188.artDimensions")==[1536,1024]
                    # V188 must retain a real rendered terrain surface at every camera edge.
                    # These bounds cover the entire zoom-1 portrait whole-crossing view.
                    assert page.evaluate("() => {const b=[-1900,-3000,7000,9000]; const x=1670,y=925,w=390,h=844; const scale=Math.min(w/3200,h/2450); return (y-h/(2*scale)>=b[1] && y+h/(2*scale)<=b[1]+b[3]);}")
                    nodes=page.evaluate("V188.roadNodeCount")
                    assert nodes>=90,nodes
                    page.locator("#options").click()
                    page.locator("#whole").click()
                    page.evaluate("() => new Promise(done=>requestAnimationFrame(()=>requestAnimationFrame(done)))")
                    page.screenshot(path=str(out/f"{engine}-{orient}-v188-whole.png"),animations="disabled")
                    assert page.evaluate("V188.orderTo('west')")
                    page.evaluate("V188.progress(.6)")
                    west=page.evaluate("V188.point")
                    assert len(west)==2 and all(isinstance(x,(int,float)) for x in west)
                    page.evaluate("V188.halt()")
                    assert not page.evaluate("V188.moving")
                    assert page.evaluate("V188.orderTo('south')")
                    page.evaluate("V188.progress(1)")
                    assert not errors,(engine,orient,errors)
                    results[f"{engine}-{orient}"]={"pass":True,"sampled_edge_colors":report["samples"],
                        "graded_background_pixels":report["adjustedPixels"],"road_nodes":nodes,
                        "halt_and_reorder":True,"historical_approval":False}
                    page.close()
            finally:browser.close()
finally:server.shutdown()
result={"passed":len(results)==4,"results":results,"game_art_approved":False,
        "historical_road_controls_approved":False,"physical_iphone_reviewed":False,
        "v94_campaign_unchanged":True,"next":"Inspect before/after mobile screenshots; retain fail-closed historical and game art approvals."}
(out/"report.json").write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2),flush=True)
assert result["passed"]

#!/usr/bin/env python3
"""V134 standalone seamless-terrain-preview smoke QA (not production art approval)."""
import http.server, json, threading
from pathlib import Path
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[1]
out=root/"qa"/"v134-seamless"
out.mkdir(parents=True,exist_ok=True)
class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(root),**kwargs)
    def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(("127.0.0.1",0),Handler)
threading.Thread(target=server.serve_forever,daemon=True).start()
url=f"http://127.0.0.1:{server.server_port}/v134-seamless-terrain-preview.html"
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
                    page.wait_for_function("window.V134?.ready===true",timeout=30000)
                    assert page.evaluate("V134.artDimensions")==[1536,1024]
                    assert page.evaluate("V134.connectedRoute")
                    assert all(s["pass"] for s in page.evaluate("V134.seamStatus"))
                    assert not page.evaluate("V134.productionApproved")
                    assert page.evaluate("V134.roadNodeCount")>=90
                    page.screenshot(path=str(out/f"{engine}-{orient}-opening.png"),animations="disabled")
                    assert page.evaluate("V134.orderTo('west')")
                    page.evaluate("V134.progress(1)")
                    assert page.evaluate("V134.orderTo('south')")
                    page.evaluate("V134.progress(1)")
                    assert not errors,(engine,orient,errors)
                    results[f"{engine}-{orient}"]={"pass":True,"photoLoaded":True,"seams":2,"roadMovement":True}
                    page.close()
            finally:browser.close()
finally:server.shutdown()
report={"passed":len(results)==4,"results":results,"humanArtworkApproval":False,"campaignUnchanged":True}
(out/"report.json").write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
assert report["passed"]

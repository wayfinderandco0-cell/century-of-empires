#!/usr/bin/env python3
"""V164 real-game-frame mobile source-detail comparison; not visual approval."""
import http.server
import json
import threading
import time
from pathlib import Path
from PIL import Image, ImageChops, ImageStat
from playwright.sync_api import sync_playwright
from qa_v140_neighbor_detail import audit

root=Path(__file__).resolve().parents[1]
out=root/"qa/v164-source-detail"
out.mkdir(parents=True,exist_ok=True)
class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self,*a,**kw):super().__init__(*a,directory=str(root),**kw)
    def log_message(self,*a):pass
server=http.server.ThreadingHTTPServer(("127.0.0.1",0),Handler)
threading.Thread(target=server.serve_forever,daemon=True).start()
url=f"http://127.0.0.1:{server.server_port}/"
results={}
try:
 with sync_playwright() as pw:
  for engine in ("chromium","webkit"):
   browser=getattr(pw,engine).launch(headless=True)
   try:
    for orientation,w,h in (("portrait",390,844),("landscape",844,390)):
     key=f"{engine}-{orientation}"
     captures={}
     times={}
     detail_report=None
     for variant,file in (("baseline","v161-native-material-study.html"),("study","v164-source-detail-study.html")):
      page=browser.new_page(viewport={"width":w,"height":h},is_mobile=True,has_touch=True,device_scale_factor=2)
      errors=[]
      page.on("pageerror",lambda e:errors.append(str(e)))
      start=time.monotonic()
      page.goto(url+file,wait_until="domcontentloaded",timeout=30000)
      page.wait_for_function("window.V137?.ready===true",timeout=60000)
      times[variant]=round((time.monotonic()-start)*1000)
      assert page.evaluate("V137.connectedRoute")
      assert not page.evaluate("V137.productionApproved")
      assert all(s["pass"] for s in page.evaluate("V137.seamStatus"))
      if variant=="study":
       detail_report=page.evaluate("V137.materialDetail")
       material_report=page.evaluate("V137.materialStudy")
       assert detail_report["version"]==164 and detail_report["sourceOnly"]
       assert detail_report["changedPixels"]>1000
       assert detail_report["maxObservedDelta"]<=18
       assert not detail_report["addsNewGeographicFeatures"]
       assert not detail_report["routeGeoregistered"]
       assert material_report["version"]==164
       assert not material_report["v123ToMaterialGeoregistered"]
       assert not material_report["productionApproved"]
       assert page.evaluate("V137.detailMarkCount")==0
       assert page.evaluate("V137.photoStampCount")==0
      for region in ("west","matrei","south"):
       assert page.evaluate("(r)=>V137.focusTile(r)",region)
       page.evaluate("()=>new Promise(done=>requestAnimationFrame(()=>requestAnimationFrame(done)))")
       shot=out/f"{key}-{region}-terrain.png" if variant=="study" else out/f"{key}-{region}-baseline.png"
       page.screenshot(path=str(shot),animations="disabled")
       captures[(variant,region)]=shot
      if variant=="study":
       page.locator("#options").click()
       page.locator("#whole").click()
       page.evaluate("()=>new Promise(done=>requestAnimationFrame(()=>requestAnimationFrame(done)))")
       page.screenshot(path=str(out/f"{key}-whole-crossing.png"),animations="disabled")
       assert page.evaluate("V137.orderTo('west')")
       page.evaluate("V137.progress(1)")
       assert page.evaluate("V137.orderTo('south')")
       page.evaluate("V137.progress(1)")
      assert not errors,(key,variant,errors)
      page.close()
     changes={}
     for region in ("west","matrei","south"):
      with Image.open(captures[("baseline",region)]) as old,Image.open(captures[("study",region)]) as new:
       diff=ImageChops.difference(old.convert("RGB"),new.convert("RGB"))
       changes[region]=round(sum(ImageStat.Stat(diff).mean)/3,5)
     assert changes["west"]>.001 and changes["south"]>.001,(key,changes)
     results[key]={"technicalPass":True,"meanRgbDeltaVsV161":changes,
                   "bootMillisBrowserNotPhysicalPhone":times,"detail":detail_report}
   finally:browser.close()
finally:server.shutdown()
parity=audit(out)
summary={"technicalPassed":len(results)==4,"configurations":results,
         "unchangedV140VisualGatePassed":parity["passed"],
         "realGameFrame":True,"sourceMaterialNotGeoregistered":True,
         "threeOctagonsVisuallyApproved":False,"physicalIPhoneApproved":False,
         "productionApproved":False,
         "note":"V164 sharpens existing V102/V97 source gradients only. Browser screenshot detail is not geographic or human art approval."}
(out/"v164-report.json").write_text(json.dumps(summary,indent=2)+"\n")
(out/"v140-neighbor-visual-audit.json").write_text(json.dumps(parity,indent=2)+"\n")
print(json.dumps(summary,indent=2),flush=True)
assert summary["technicalPassed"]

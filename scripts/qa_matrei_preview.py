from pathlib import Path
import os,http.server,socketserver,threading,json
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
class Quiet(http.server.SimpleHTTPRequestHandler):
 def __init__(self,*a,**kw):super().__init__(*a,directory=str(ROOT),**kw)
 def log_message(self,*a):pass
class S(socketserver.TCPServer):allow_reuse_address=True
server=S(("127.0.0.1",0),Quiet);threading.Thread(target=server.serve_forever,daemon=True).start()
url=f"http://127.0.0.1:{server.server_address[1]}/v107-matrei-terrain-study.html"
reports={}
try:
 with sync_playwright() as p:
  for engineName in ["chromium","webkit"]:
   b=getattr(p,engineName).launch(headless=True)
   try:
    page=b.new_page(viewport={"width":390,"height":844},device_scale_factor=2,is_mobile=True,has_touch=True)
    errors=[];page.on("pageerror",lambda e:errors.append(str(e)))
    page.goto(url,wait_until="domcontentloaded")
    page.wait_for_function("window.matreiStudy?.ready === true",timeout=40000)
    checks={}
    checks["ready"]=page.evaluate("window.matreiStudy.ready")
    checks["nodeCount"]=page.evaluate("window.matreiStudy.routeNodes === 27")
    checks["routingOff"]=page.evaluate("window.matreiStudy.graphEnabled === false")
    checks["debugOff"]=page.evaluate("window.matreiStudy.debug === false")
    checks["portraitFits"]=page.evaluate("document.documentElement.scrollWidth<=innerWidth+1 && document.documentElement.scrollHeight<=innerHeight+1")
    page.locator("#debug").click()
    checks["toggleOn"]=page.evaluate("window.matreiStudy.debug===true")
    page.locator("#debug").click()
    checks["toggleOff"]=page.evaluate("window.matreiStudy.debug===false")
    page.locator("[data-span='420']").click()
    checks["terrainZoom"]=page.evaluate("window.matreiStudy.span===420")
    page.locator("#reset").click()
    checks["reset"]=page.evaluate("window.matreiStudy.span===1120")
    page.set_viewport_size({"width":844,"height":390});page.wait_for_timeout(300)
    checks["landscapeFits"]=page.evaluate("document.documentElement.scrollWidth<=innerWidth+1 && document.documentElement.scrollHeight<=innerHeight+1")
    checks["noErrors"]=len(errors)==0
    reports[engineName]={"checks":checks,"errors":errors,"passed":all(checks.values())}
   finally:b.close()
finally:server.shutdown()
out=ROOT/"terrain-puzzle"/"wipptal-matrei"
report={"passed":all(x["passed"] for x in reports.values()),"browsers":reports,"on_real_iphone":False}
(out/"matrei-v107-browser-qa.json").write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report,indent=2))
if not report["passed"]:raise SystemExit(1)

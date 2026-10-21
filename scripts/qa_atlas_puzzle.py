"""Independent test for the two-octagon geographic assembly preview.
Renders actual screenshots in phone-sized Chromium and WebKit. No gameplay writes.
"""
import base64,io,json,pathlib,http.server,socketserver,threading,time
from PIL import Image
from playwright.sync_api import sync_playwright
ROOT=pathlib.Path(__file__).resolve().parents[1]
OUT=ROOT/"terrain-puzzle"/"evidence"
OUT.mkdir(exist_ok=True,parents=True)
class Quiet(http.server.SimpleHTTPRequestHandler):
    def __init__(self,*a,**kw):super().__init__(*a,directory=str(ROOT),**kw)
    def log_message(self,*a):pass
class Reuse(socketserver.TCPServer):allow_reuse_address=True
server=Reuse(("127.0.0.1",0),Quiet)
threading.Thread(target=server.serve_forever,daemon=True).start()
url=f"http://127.0.0.1:{server.server_address[1]}/v106-atlas-puzzle-proof.html"
report={"purpose":"Two-piece geographically registered atlas; candidate routes disabled", "browsers":{},"physicalIPhoneTested":False}
try:
 with sync_playwright() as p:
  for name in ["chromium","webkit"]:
   browser=None
   x={"checks":{},"errors":[],"failedRequests":[]}
   report["browsers"][name]=x
   try:
    engine=getattr(p,name)
    browser=engine.launch(headless=True)
    page=browser.new_page(viewport={"width":390,"height":844},device_scale_factor=2,is_mobile=True,has_touch=True)
    page.on("pageerror",lambda e:x["errors"].append(str(e)))
    page.on("requestfailed",lambda req:x["failedRequests"].append(req.url))
    page.goto(url,wait_until="domcontentloaded")
    page.wait_for_function("window.atlasPuzzle?.ready === true",timeout=30000)
    page.wait_for_timeout(900)
    x["checks"]["ready"]=page.evaluate("window.atlasPuzzle.ready")
    x["checks"]["twoOctagons"]=page.evaluate("window.atlasPuzzle.counts.cells===2")
    x["checks"]["connector"]=page.evaluate("window.atlasPuzzle.counts.connectors===1")
    x["checks"]["hiddenInitially"]=page.evaluate("window.atlasPuzzle.debug===false")
    x["checks"]["routeCounts"]=page.evaluate("window.atlasPuzzle.counts.nodes===43 && window.atlasPuzzle.counts.edges===40")
    x["checks"]["fitPortrait"]=page.evaluate("document.documentElement.scrollWidth <= innerWidth+1 && document.documentElement.scrollHeight <= innerHeight+1")
    page.screenshot(path=str(OUT/(name+"-clean-portrait.png")))
    page.locator("#debug").click();page.wait_for_timeout(200)
    x["checks"]["toggleOn"]=page.evaluate("window.atlasPuzzle.debug===true")
    x["checks"]["ariaOn"]=page.locator("#debug").get_attribute("aria-pressed")=="true"
    page.screenshot(path=str(OUT/(name+"-hidden-network.png")))
    page.locator("#debug").click()
    x["checks"]["toggleOff"]=page.evaluate("window.atlasPuzzle.debug===false")
    page.locator('[data-level="3"]').click()
    x["checks"]["terrainZoom"]=page.evaluate("Math.abs(window.atlasPuzzle.camera.span-1350)<2")
    page.locator("#home").click()
    x["checks"]["homeReset"]=page.evaluate("Math.abs(window.atlasPuzzle.camera.x-500)<.01 && window.atlasPuzzle.camera.span===2600")
    page.set_viewport_size({"width":844,"height":390})
    page.wait_for_timeout(300)
    x["checks"]["fitLandscape"]=page.evaluate("document.documentElement.scrollWidth <= innerWidth+1 && document.documentElement.scrollHeight <= innerHeight+1")
    page.screenshot(path=str(OUT/(name+"-clean-landscape.png")))
    x["checks"]["noErrors"]=not x["errors"]
    x["checks"]["noFailedRequests"]=not x["failedRequests"]
    x["passed"]=all(x["checks"].values())
   except Exception as e:
    x["errors"].append(str(e));x["passed"]=False
   finally:
    if browser:browser.close()
finally:
 server.shutdown()
report["passed"]=all(x["passed"] for x in report["browsers"].values())
(OUT/"qa-report.json").write_text(json.dumps(report,indent=2)+"\n")
for path in list(OUT.glob("*.png")):
 with Image.open(path) as im:
  im.thumbnail((420,820))
  buf=io.BytesIO()
  im.convert("RGB").save(buf,format="JPEG",quality=75,optimize=True)
  (OUT/(path.stem+"-preview.jpeg.base64.txt")).write_text(base64.b64encode(buf.getvalue()).decode())
print(json.dumps(report,indent=2))
if not report["passed"]:raise SystemExit(1)

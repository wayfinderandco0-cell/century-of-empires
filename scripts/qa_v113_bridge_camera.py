"""V113 close-zoom, bridge-geometry, army-march iPhone-sized browser smoke test."""
import http.server,threading,socketserver,json
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"qa"/"v113"
OUT.mkdir(parents=True,exist_ok=True)
class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self,*args,**kw): super().__init__(*args,directory=str(ROOT),**kw)
    def log_message(self,*args): pass
class Server(socketserver.TCPServer): allow_reuse_address=True
server=Server(("127.0.0.1",0),Handler)
threading.Thread(target=server.serve_forever,daemon=True).start()
url=f"http://127.0.0.1:{server.server_address[1]}/v113-bridge-camera-repair.html"
results={}
try:
 with sync_playwright() as playwright:
  for engine in ("chromium","webkit"):
   browser=getattr(playwright,engine).launch(headless=True)
   errors=[]
   try:
    page=browser.new_page(viewport={"width":390,"height":844},device_scale_factor=2,is_mobile=True,has_touch=True)
    page.on("pageerror",lambda err:errors.append(str(err)))
    page.goto(url,wait_until="domcontentloaded")
    page.wait_for_function("window.centuryV113?.ready===true",timeout=45000)
    checks={}
    checks["all_images_loaded"]=page.evaluate("centuryV113.assetErrors.length===0")
    checks["protected_art"]=page.evaluate("centuryV113.path.length>=40")
    checks["bridge_no_second_crossing"]=page.evaluate("centuryV113.routeAvoidsSecondCrossing===true")
    page.locator('[data-view="town"]').click()
    page.wait_for_function("centuryV113.currentSpan<0.32",timeout=7000)
    checks["town_clamped"]=page.evaluate("centuryV113.cameraInArt===true")
    page.screenshot(path=str(OUT/f"{engine}-town.png"))
    page.locator("#bridge").click()
    checks["bridge_selected"]=page.evaluate("centuryV113.currentRoute==='bridge'")
    page.locator("#hiddenDots").click()
    checks["route_visible"]=page.evaluate("centuryV113.debug===true")
    page.screenshot(path=str(OUT/f"{engine}-bridge-route.png"))
    page.locator("#march").click()
    page.wait_for_timeout(750)
    checks["moving"]=page.evaluate("centuryV113.moving===true")
    page.locator("#march").click()
    checks["halted"]=page.evaluate("centuryV113.moving===false")
    page.locator('[data-view="pass"]').click()
    page.wait_for_function("centuryV113.currentSpan>10",timeout=7000)
    checks["zoom_to_pass"]=page.evaluate("centuryV113.currentSpan>10")
    page.screenshot(path=str(OUT/f"{engine}-pass.png"))
    checks["no_page_errors"]=not errors
    results[engine]={"passed":all(checks.values()),"checks":checks,"errors":errors}
   except Exception as err:results[engine]={"passed":False,"error":str(err),"errors":errors}
   finally:browser.close()
finally:server.shutdown()
result={"passed":all(e["passed"] for e in results.values()),"browsers":results,"physical_iPhone_tested":False,"historical_georeferencing_verified":False}
(OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")
print(json.dumps(result,indent=2))
if not result["passed"]:raise SystemExit(1)

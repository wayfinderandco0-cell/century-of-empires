"""V114 mobile camera coverage and bridge bank routing smoke test."""
import http.server,threading,socketserver,json
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"qa"/"v114";OUT.mkdir(parents=True,exist_ok=True)
class H(http.server.SimpleHTTPRequestHandler):
 def __init__(self,*a,**kw):super().__init__(*a,directory=str(ROOT),**kw)
 def log_message(self,*a):pass
class S(socketserver.TCPServer):allow_reuse_address=True
server=S(("127.0.0.1",0),H)
threading.Thread(target=server.serve_forever,daemon=True).start()
url=f"http://127.0.0.1:{server.server_address[1]}/v114-town-camera-bridge-safety.html"
result={}
try:
 with sync_playwright() as p:
  for engine in ("chromium","webkit"):
   browser=getattr(p,engine).launch(headless=True)
   try:
    page=browser.new_page(viewport={"width":390,"height":844},device_scale_factor=2,is_mobile=True,has_touch=True)
    errors=[];page.on("pageerror",lambda x:errors.append(str(x)))
    page.goto(url,wait_until="domcontentloaded")
    page.wait_for_function("window.centuryV114?.ready===true",timeout=45000)
    page.locator('[data-view="town"]').click()
    page.wait_for_function("centuryV114.currentSpan<0.32",timeout=8000)
    checks={}
    checks["portrait_image_covers"]=page.evaluate("centuryV114.townArtCoverage>=1.05")
    checks["camera_in_art"]=page.evaluate("centuryV114.cameraInArt")
    checks["no_fake_east_extension"]=page.evaluate("centuryV114.bridgeEndsAtBank && centuryV114.bridgeRouteFinish[0]===704")
    page.screenshot(path=str(OUT/f"{engine}-town.png"))
    page.locator("#bridge").click()
    checks["bridge_selected"]=page.evaluate("centuryV114.currentRoute==='bridge'")
    page.locator("#hiddenDots").click()
    page.screenshot(path=str(OUT/f"{engine}-bridge-debug.png"))
    page.locator("#march").click()
    page.wait_for_timeout(700)
    checks["moves"]=page.evaluate("centuryV114.moving")
    page.locator("#march").click()
    checks["halts"]=page.evaluate("!centuryV114.moving")
    page.mouse.move(160,370);page.mouse.down();page.mouse.move(160,110,steps=15);page.mouse.up()
    checks["pan_stays_in_art"]=page.evaluate("centuryV114.cameraInArt")
    page.screenshot(path=str(OUT/f"{engine}-town-after-pan.png"))
    page.set_viewport_size({"width":844,"height":390});page.wait_for_timeout(250)
    checks["landscape_camera_in_art"]=page.evaluate("centuryV114.cameraInArt")
    checks["no_js_errors"]=not errors
    page.screenshot(path=str(OUT/f"{engine}-landscape.png"))
    result[engine]={"passed":all(checks.values()),"checks":checks,"errors":errors}
   except Exception as e:result[engine]={"passed":False,"error":str(e)}
   finally:browser.close()
finally:server.shutdown()
output={"passed":all(v["passed"] for v in result.values()),"browsers":result,"real_iPhone_confirmed":False}
(OUT/"result.json").write_text(json.dumps(output,indent=2)+"\n")
print(json.dumps(output,indent=2))
if not output["passed"]:raise SystemExit(1)

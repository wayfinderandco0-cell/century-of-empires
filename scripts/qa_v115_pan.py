"""V115 real rendered camera and controls QA (iPhone-size Chromium and WebKit)."""
import http.server, socketserver, threading, json
from pathlib import Path
from playwright.sync_api import sync_playwright
BASE=Path(__file__).resolve().parents[1]
OUT=BASE/"qa"/"v115"; OUT.mkdir(parents=True,exist_ok=True)
class Serve(http.server.SimpleHTTPRequestHandler):
 def __init__(self,*a,**kw):super().__init__(*a,directory=str(BASE),**kw)
 def log_message(self,*a):pass
class S(socketserver.TCPServer): allow_reuse_address=True
server=S(("127.0.0.1",0),Serve)
threading.Thread(target=server.serve_forever,daemon=True).start()
address=f"http://127.0.0.1:{server.server_address[1]}/v115-town-pan-controls.html"
results={}
try:
 with sync_playwright() as playwright:
  for name in ("chromium","webkit"):
   browser=getattr(playwright,name).launch(headless=True)
   problems=[]
   try:
    page=browser.new_page(viewport={"width":390,"height":844},device_scale_factor=2,is_mobile=True,has_touch=True)
    page.on("pageerror",lambda e:problems.append(str(e)))
    page.goto(address,wait_until="domcontentloaded")
    page.wait_for_function("window.centuryV115?.ready===true",timeout=45000)
    checks={}
    checks["compact_start"]=page.evaluate("centuryV115.toolbarCompact")
    checks["original_artwork"]=page.evaluate("centuryV115.path.length>=40")
    page.locator("#toggleMap").click()
    page.locator('[data-view="town"]').click()
    page.wait_for_function("centuryV115.currentSpan<0.20",timeout=8000)
    checks["town_zoom"]=page.evaluate("centuryV115.currentSpan<0.20 && centuryV115.townArtCoverage>1.5")
    checks["map_not_cut"]=page.evaluate("centuryV115.cameraInArt")
    page.screenshot(path=str(OUT/f"{name}-town-compact.png"))
    pos1=page.evaluate("centuryV115.camera")
    page.mouse.move(172,620)
    page.mouse.down()
    page.mouse.move(172,315,steps=14)
    page.mouse.up()
    pos2=page.evaluate("centuryV115.camera")
    checks["vertical_drag_moves_camera"]=abs(pos2["y"]-pos1["y"])>0.025
    checks["camera_stays_inside_art"]=page.evaluate("centuryV115.cameraInArt")
    page.screenshot(path=str(OUT/f"{name}-panned.png"))
    page.locator("#focusBridge").click()
    pos3=page.evaluate("centuryV115.camera")
    checks["bridge_focus_moves_camera"]=abs(pos3["y"]-pos2["y"])>0.003
    page.screenshot(path=str(OUT/f"{name}-bridge-focus.png"))
    page.locator("#toggleActions").click()
    checks["orders_drawer_open"]=page.evaluate("!document.getElementById('actions').hidden")
    page.locator("#toggleMap").click()
    checks["views_drawer_open"]=page.evaluate("document.getElementById('actions').hidden && !document.getElementById('presets').hidden")
    page.locator("#focusArmy").click()
    checks["close_drawers_on_focus"]=page.evaluate("centuryV115.toolbarCompact")
    checks["no_JavaScript_errors"]=not problems
    results[name]={"passed":all(checks.values()),"checks":checks,"errors":problems}
   except Exception as e:
    results[name]={"passed":False,"error":str(e),"errors":problems}
   finally:browser.close()
finally:server.shutdown()
output={"passed":all(v["passed"] for v in results.values()),"tests":results,"physical_iPhone_approved":False,"full_gameplay_integrated":False}
(OUT/"results.json").write_text(json.dumps(output,indent=2)+"\n")
print(json.dumps(output,indent=2))
if not output["passed"]:raise SystemExit(1)

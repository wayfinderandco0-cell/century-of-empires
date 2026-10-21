"""V111 zoom continuity smoke test: iPhone-sized Chromium and WebKit."""
import json, http.server, socketserver, threading
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"qa"/"v111"
OUT.mkdir(parents=True,exist_ok=True)
class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs): super().__init__(*args,directory=str(ROOT),**kwargs)
    def log_message(self,*_): pass
class Server(socketserver.TCPServer): allow_reuse_address=True
server=Server(("127.0.0.1",0),Handler)
threading.Thread(target=server.serve_forever,daemon=True).start()
url=f"http://127.0.0.1:{server.server_address[1]}/v111-bridge-junction.html"
tests={}
try:
 with sync_playwright() as p:
  for engine in ("chromium","webkit"):
   browser=getattr(p,engine).launch(headless=True)
   errs=[]
   try:
    page=browser.new_page(viewport={"width":390,"height":844},device_scale_factor=2,is_mobile=True,has_touch=True)
    page.on("pageerror",lambda e: errs.append(str(e)))
    page.goto(url,wait_until="domcontentloaded")
    page.wait_for_function("window.centuryV111?.ready===true",timeout=45000)
    checks={}
    checks["assets"]=page.evaluate("centuryV111.assetErrors.length===0")
    checks["path"]=page.evaluate("centuryV111.path.length===39")
    checks["initial_europe"]=page.evaluate("centuryV111.scene==='europe'")
    checks["screen_fits"]=page.evaluate("document.documentElement.scrollWidth<=innerWidth+1 && document.documentElement.scrollHeight<=innerHeight+1")
    page.screenshot(path=str(OUT/f"{engine}-europe.png"))
    for key in ("region","pass","town"):
     page.locator(f'button[data-view="{key}"]').click()
     page.wait_for_function("(target)=>window.centuryV111?.scene===target",arg=key,timeout=6500)
     page.wait_for_timeout(280)
     checks[f"view_{key}"]=page.evaluate("(target)=>centuryV111.scene===target",key)
     page.screenshot(path=str(OUT/f"{engine}-{key}.png"))
    page.locator("#bridge").click()
    checks["branch_selected"]=page.evaluate("centuryV111.currentRoute==='bridge'")
    checks["junction_shared"]=page.evaluate("centuryV111.bridgePath.length>centuryV111.path.length && centuryV111.junction[0]===447 && centuryV111.bridgePassable")
    page.screenshot(path=str(OUT/f"{engine}-bridge-selected.png"))
    page.locator("#hiddenDots").click()
    checks["debug_mode"]=page.evaluate("centuryV111.debug===true")
    page.screenshot(path=str(OUT/f"{engine}-town-dots.png"))
    page.locator("#march").click()
    page.wait_for_timeout(800)
    checks["marches"]=page.evaluate("centuryV111.moving&&centuryV111.progress>.48")
    page.locator("#march").click()
    checks["halts"]=page.evaluate("!centuryV111.moving")
    pos=page.evaluate("centuryV111._visibleArmy")
    if 0<pos[0]<390 and 0<pos[1]<844:
     page.mouse.click(*pos)
     checks["army_selected"]=page.evaluate("document.getElementById('inspector').hidden===false")
    else: checks["army_selected"]=False
    page.set_viewport_size({"width":844,"height":390})
    page.wait_for_timeout(200)
    checks["landscape_fit"]=page.evaluate("document.documentElement.scrollWidth<=innerWidth+1 && document.documentElement.scrollHeight<=innerHeight+1")
    checks["no_js_errors"]=not errs
    page.screenshot(path=str(OUT/f"{engine}-landscape.png"))
    tests[engine]={"passed":all(checks.values()),"checks":checks,"errors":errs}
   except Exception as err: tests[engine]={"passed":False,"error":str(err),"errors":errs}
   finally: browser.close()
finally: server.shutdown()
result={"passed":all(t["passed"] for t in tests.values()),"engine_results":tests,"real_iPhone_tested":False,"full_gameplay_integrated":False}
(OUT/"result.json").write_text(json.dumps(result,indent=2)+"\n")
print(json.dumps(result,indent=2))
if not result["passed"]: raise SystemExit(1)

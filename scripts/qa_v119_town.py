"""V119 isolated iPhone browser QA: town anchoring, portrait map coverage, bridge route.
Does not certify the historical road, artwork restoration, or production readiness.
"""
import http.server, socketserver, threading, json
from pathlib import Path
from playwright.sync_api import sync_playwright
BASE=Path(__file__).resolve().parents[1]
OUT=BASE/"qa"/"v119"; OUT.mkdir(parents=True,exist_ok=True)
class Serve(http.server.SimpleHTTPRequestHandler):
    def __init__(self,*a,**kw): super().__init__(*a,directory=str(BASE),**kw)
    def log_message(self,*a): pass
class S(socketserver.TCPServer): allow_reuse_address=True
server=S(("127.0.0.1",0),Serve)
threading.Thread(target=server.serve_forever,daemon=True).start()
url=f"http://127.0.0.1:{server.server_address[1]}/v119-matrei-town-label.html"
results={}
try:
    with sync_playwright() as playwright:
        for engine in ("chromium","webkit"):
            b=getattr(playwright,engine).launch(headless=True)
            for orientation,viewport in (("portrait",{"width":390,"height":844}),("landscape",{"width":844,"height":390})):
                errs=[]; key=f"{engine}-{orientation}"
                try:
                    page=b.new_page(viewport=viewport,device_scale_factor=2,is_mobile=True,has_touch=True)
                    page.on("pageerror", lambda e, errors=errs: errors.append(str(e)))
                    page.goto(url,wait_until="domcontentloaded")
                    page.wait_for_function("window.centuryV116Proof?.ready===true && window.centuryV119Proof?.name==='Matrei am Brenner'",timeout=45000)
                    checks={}
                    checks["art_anchor"]=page.evaluate("JSON.stringify(centuryV119Proof.artAnchor)==='[452,283]'")
                    checks["old_route_integrity"]=page.evaluate("centuryV118Proof.movementOnInk === true")
                    checks["east_bridge_endpoint"]=page.evaluate("JSON.stringify(centuryV118Proof.eastExit)==='[1100,704]' && JSON.stringify(centuryV118Proof.neighborEntry)==='[0,704]'")
                    checks["no_production_claim"]=page.evaluate("centuryV119Proof.productionReady === false")
                    page.locator("#focusTown").click()
                    checks["village_art_coverage"]=page.evaluate("centuryV119Proof.cameraWithinImage === true")
                    before=page.evaluate("centuryV119Proof.screenAnchor")
                    checks["label_above_town_visible"]=0<before[0]<viewport["width"] and 0<before[1]<viewport["height"]
                    page.screenshot(path=str(OUT/f"{key}-village.png"))
                    page.mouse.move(viewport["width"]*.55,viewport["height"]*.45)
                    page.mouse.down()
                    page.mouse.move(viewport["width"]*.30,viewport["height"]*.45,steps=12)
                    page.mouse.up()
                    after=page.evaluate("centuryV119Proof.screenAnchor")
                    checks["label_follows_map_pan"]=abs(after[0]-before[0])>5
                    checks["still_covered_after_pan"]=page.evaluate("centuryV119Proof.cameraWithinImage === true")
                    page.screenshot(path=str(OUT/f"{key}-panned.png"))
                    page.locator("#focusBridge").click()
                    checks["bridge_art_coverage"]=page.evaluate("centuryV119Proof.cameraWithinImage === true")
                    checks["bridge_path_unchanged"]=page.evaluate("centuryV118Proof.movementOnInk === true")
                    checks["no_runtime_errors"]=not errs
                    page.screenshot(path=str(OUT/f"{key}-bridge.png"))
                    results[key]={"passed":all(checks.values()),"checks":checks,"errors":errs,"screen_anchor_before":before,"after":after}
                    page.close()
                except Exception as e:
                    results[key]={"passed":False,"error":str(e),"errors":errs}
            b.close()
finally:
    server.shutdown()
report={"passed":all(x["passed"] for x in results.values()),"tests":results,
        "physical_iPhone_approved":False,"historical_road_verified":False,
        "old_baked_label_removed":False,"production_octagon_ready":False}
(OUT/"results.json").write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report,indent=2))
if not report["passed"]: raise SystemExit(1)

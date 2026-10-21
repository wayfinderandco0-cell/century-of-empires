#!/usr/bin/env python3
"""Real browser smoke + screenshots for isolated V117 coupled road artwork.

Uses original embedded V115 JPEG, not the synthetic texture from earlier QA.
A passing browser test does not establish historical GIS accuracy or iPhone Safari.
"""
import http.server
import json
import base64
import threading
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"qa/v117"
OUT.mkdir(parents=True,exist_ok=True)
class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,directory=str(ROOT),**kwargs)
    def log_message(self,*args):pass

server=http.server.ThreadingHTTPServer(("127.0.0.1",0),Handler)
thread=threading.Thread(target=server.serve_forever,daemon=True)
thread.start()
url=f"http://127.0.0.1:{server.server_port}/v117-coupled-cart-road-proof.html"
report={"page":"v117-coupled-cart-road-proof.html",
        "source":"actual 1100x842 V115 embedded painting + candidate cart-track overlay",
        "productionGameModified":False,
        "physicalIphoneSafariTested":False,
        "historicRoadVerified":False,
        "farBankRoadContinuationVerified":False,
        "cases":{}}
try:
    with sync_playwright() as p:
        for engine in ("chromium","webkit"):
            browser=getattr(p,engine).launch(headless=True)
            try:
                for shape,viewport in (
                    ("portrait",{"width":390,"height":844}),
                    ("landscape",{"width":844,"height":390})):
                    page=browser.new_page(viewport=viewport,device_scale_factor=2,
                                         is_mobile=True,has_touch=True)
                    page_errors=[]
                    page.on("pageerror",lambda e:page_errors.append(str(e)))
                    key=f"{engine}-{shape}"
                    try:
                        response=page.goto(url,wait_until="domcontentloaded",timeout=30000)
                        assert response and response.status==200,(key,"HTTP failure")
                        page.wait_for_function(
                            "() => window.centuryV116Proof && window.centuryV116Proof.ready",
                            timeout=15000)
                        app=page.evaluate("""() => {
                           const a=window.centuryV116Proof;
                           return {tiles:a.index.tiles.length,
                              transformError:a.sharedTransformError,
                              approvedForProduction:a.graph.approvedForProduction,
                              farBankEnd:a.graph.endpoints.bridgeStop,
                              bridgeLength:a.graph.length('bridge')};
                        }""")
                        assert app["tiles"]==48,key
                        assert app["transformError"] < 1e-6,(key,app)
                        assert app["approvedForProduction"] is False,key
                        paired=page.evaluate("""() => ({
                           synced:centuryV117Proof.synced,cartTrack:centuryV117Proof.cartTrack,
                           bridgeEnd:centuryV117Proof.bridgeEnd,productionReady:centuryV117Proof.productionReady,
                           marked:centuryV117Proof.artisticDeviationMeasured
                        })""")
                        if engine=="chromium" and shape=="portrait":
                            dataurl=page.evaluate("() => originalArt")
                            assert dataurl.startswith("data:image/jpeg;base64,"),key
                            (OUT/"original-v115-art.jpg").write_bytes(
                                base64.b64decode(dataurl.split(",",1)[1]))
                        assert paired["synced"] is True,(key,paired)
                        assert paired["cartTrack"] is True,(key,paired)
                        assert paired["productionReady"] is False,(key,paired)
                        assert paired["bridgeEnd"]==[699,799],(key,paired)
                        assert paired["marked"] is False,(key,paired)
                        page.locator("#bridgeRoute").click()
                        assert page.evaluate("centuryV116Proof.route")=="bridge",key
                        assert not page.locator("#views").is_visible(),key
                        assert not page.locator("#status").is_visible(),key
                        page.locator("#focusBridge").click()
                        camera_inside=page.evaluate("""() => {
                          const a=window.centuryV116Proof,b=a.index.artBoxWorldPx,c=a.snapshot.cam;
                          return c[0]>=b[0]-1e-9 && c[2]<=b[2]+1e-9 &&
                            c[1]>=b[1]-1e-9 && c[3]<=b[3]+1e-9;
                        }""")
                        assert camera_inside,(key,"Bridge camera exposed off-art blank band")
                        position=page.evaluate("""() => {
                          const a=window.centuryV116Proof;
                          return a.qaSetDistance('bridge',a.graph.forkDistance+150);
                        }""")
                        assert len(position)==2,key
                        assert page.locator("#south").is_disabled(),key
                        blocked=page.evaluate("centuryV116Proof.chooseRoute('south')")
                        assert blocked is False,key
                        observed=page.evaluate("centuryV116Proof.snapshot")
                        assert observed["position"]==position,key
                        page.wait_for_timeout(150)
                        screenshot=OUT/f"bridge-{engine}-{shape}.png"
                        page.screenshot(path=str(screenshot),full_page=True,animations="disabled")
                        # Verify touch/pointer pan works and never moves the army's world point.
                        prior=page.evaluate("centuryV116Proof.snapshot")
                        x,y=viewport["width"]*.45,viewport["height"]*.45
                        page.mouse.move(x,y);page.mouse.down()
                        page.mouse.move(x+30,y+23,steps=5);page.mouse.up()
                        later=page.evaluate("centuryV116Proof.snapshot")
                        assert prior["position"]==later["position"],(key,"army moved with camera")
                        assert prior["cam"]!=later["cam"],(key,"camera did not pan")
                        page.locator("#resetArmy").click()
                        assert not page.locator("#south").is_disabled(),key
                        page.locator("#south").click()
                        assert page.evaluate("centuryV116Proof.route")=="south",key
                        assert page.evaluate("centuryV116Proof.snapshot.distancePx")==0,key
                        page.locator("#audit").click()
                        assert page.locator("#cartRoad").is_visible(),key
                        page.locator("#cartRoad").click()
                        assert page.evaluate("centuryV117Proof.cartTrack") is False,key
                        page.screenshot(path=str(OUT/f"original-underlay-{key}.png"),
                                        full_page=True,animations="disabled")
                        page.locator("#cartRoad").click()
                        assert page.evaluate("centuryV117Proof.cartTrack") is True,key
                        assert page.evaluate("centuryV117Proof.synced") is True,key
                        assert not page_errors,(key,page_errors)
                        report["cases"][key]={"passed":True,"scriptErrors":page_errors,"cartRoadCoupled":True,"cartTrackToggleWorks":True,
                            "viewport":viewport,"tiles":48,"sharedTransformErrorArtPx":app["transformError"],
                            "paintedBridgeScreenshot":str(screenshot.relative_to(ROOT)),
                            "positionStayedFixedUnderPan":True,"bridgeCameraWithinSourceArt":True,"forkBlocksTeleport":True,
                            "visibleBridgeStop":app["farBankEnd"]}
                    finally:
                        page.close()
            finally:
                browser.close()
finally:
    server.shutdown()
report["passed"]=len(report["cases"])==4 and all(x["passed"] for x in report["cases"].values())
(OUT/"report.json").write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report,indent=2))
if not report["passed"]:raise SystemExit(1)

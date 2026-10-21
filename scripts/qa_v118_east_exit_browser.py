#!/usr/bin/env python3
"""Chromium and WebKit smoke test for V118 portrait/landscape artwork/road/army."""
import http.server
import json
import threading
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"qa/v118"
OUT.mkdir(parents=True,exist_ok=True)
class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,directory=str(ROOT),**kwargs)
    def log_message(self,*args):pass

server=http.server.ThreadingHTTPServer(("127.0.0.1",0),Handler)
threading.Thread(target=server.serve_forever,daemon=True).start()
url=f"http://127.0.0.1:{server.server_port}/v118-connected-bridge-exit.html"
results={}
try:
    with sync_playwright() as p:
        for engine in ("chromium","webkit"):
            browser=getattr(p,engine).launch(headless=True)
            try:
                for orientation,(w,h) in (("portrait",(390,844)),("landscape",(844,390))):
                    name=f"{engine}-{orientation}"
                    page=browser.new_page(viewport={"width":w,"height":h},
                                          device_scale_factor=2,is_mobile=True,has_touch=True)
                    errors=[]
                    page.on("pageerror",lambda e:errors.append(str(e)))
                    try:
                        response=page.goto(url,wait_until="domcontentloaded",timeout=30000)
                        assert response and response.status==200,name
                        page.wait_for_function("() => window.centuryV118Proof && window.centuryV116Proof.ready",timeout=25000)
                        original=page.evaluate("""() => ({
                         edge:centuryV118Proof.eastExit,
                         entry:centuryV118Proof.neighborEntry,
                         synced:centuryV118Proof.movementOnInk,
                         tileCount:centuryV116Proof.index.tiles.length,
                         approved:centuryV116Proof.graph.approvedForProduction,
                         terminal:centuryV116Proof.graph.bridgeTerminal,
                         routeLength:centuryV116Proof.graph.length("bridge")
                        })""")
                        assert original["edge"]==[1100,704],(name,original)
                        assert original["entry"]==[0,704],(name,original)
                        assert original["tileCount"]==48,name
                        assert original["synced"] is True,name
                        assert original["approved"] is False,name
                        assert original["terminal"]=="authored-east-edge-only",name

                        page.locator("#forkArmy").click()
                        assert page.evaluate("centuryV118Proof.atFork") is True,name
                        page.locator("#march").click()
                        page.wait_for_timeout(250)
                        assert page.evaluate("""() => centuryV116Proof.snapshot.distancePx>
                            centuryV116Proof.graph.forkDistance"""),name
                        page.locator("#march").click()

                        # Sample every portion of the source cart road on the real canvas.
                        for fraction in (.0,.20,.50,.76,.90,1):
                            position=page.evaluate("""f => {
                              const g=centuryV116Proof.graph;
                              centuryV116Proof.qaSetDistance("bridge",g.length("bridge")*f);
                              return [centuryV116Proof.snapshot.position,
                                      centuryV117Proof.synced];
                            }""",fraction)
                            assert position[1] is True,(name,fraction)
                        page.locator("#audit").click()
                        page.locator("#focusEast").click()
                        page.locator("#audit").click()
                        page.screenshot(path=str(OUT/f"{name}-east.png"),animations="disabled")
                        assert not errors,(name,errors)
                        results[name]={"passed":True,"roadEnd":original["edge"],
                          "neighborEntry":original["entry"],"scriptErrors":errors,
                          "physicalIphoneSafariTested":False,
                          "historicSourceRoadVerified":False,
                          "neighboringArtworkCompleted":False}
                    finally:
                        page.close()
            finally:
                browser.close()
finally:
    server.shutdown()
assert len(results)==4,results
(OUT/"report.json").write_text(json.dumps(results,indent=2)+"\n")
print(json.dumps(results,indent=2))

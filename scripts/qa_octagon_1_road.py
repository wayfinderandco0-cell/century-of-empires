#!/usr/bin/env python3
"""Octagon 1 source-art authoring browser checks.
Pass = mechanics work, NOT art/historical accuracy or completed octagon.
"""
import json
import http.server
import threading
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"qa"/"octagon-1"
OUT.mkdir(parents=True,exist_ok=True)
class H(http.server.SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,directory=str(ROOT),**kwargs)
    def log_message(self,*args):pass

srv=http.server.ThreadingHTTPServer(("127.0.0.1",0),H)
threading.Thread(target=srv.serve_forever,daemon=True).start()
url=f"http://127.0.0.1:{srv.server_port}/octagon-1-road-authoring.html"
results={}
try:
    with sync_playwright() as p:
        for engine in ("chromium","webkit"):
            browser=getattr(p,engine).launch(headless=True)
            for orient,viewport in (("portrait",{"width":390,"height":844}),("landscape",{"width":844,"height":390})):
                name=f"{engine}-{orient}"
                page=browser.new_page(viewport=viewport,is_mobile=True,has_touch=True,device_scale_factor=2)
                errors=[]
                page.on("pageerror",lambda e,out=errors:out.append(str(e)))
                try:
                    page.goto(url,wait_until="domcontentloaded",timeout=30000)
                    page.wait_for_function("window.Octagon1Proof?.ready===true",timeout=25000)
                    proof=page.evaluate("""() => ({
                        bridge:Octagon1Proof.bridgeEndpoint, exit:Octagon1Proof.eastEdge,
                        next:Octagon1Proof.nextCellEntry,
                        matching:Octagon1Proof.routeAndInkSame,
                        unapproved:Octagon1Proof.productionReady===false,
                        bakedLabel:Octagon1Proof.sourceLabelStillBaked,
                        routeLength:Octagon1Proof.route.length,
                        selected:Octagon1Proof.activeRoute,
                        southExit:Octagon1Proof.southExit,
                        noHairpin:Octagon1Proof.landBankCandidateHasHairpin===false,
                        sourceImageReady:image.complete && image.naturalWidth===1100 && image.naturalHeight===842,
                        sourceImageExternal:image.currentSrc.includes("/terrain-grid/octagon-1-v119-source.jpg"),
                        exportGate:Octagon1Proof.exportCandidate.connectionGate
                    })""")
                    assert proof["bridge"]==[699,799],(name,proof)
                    assert proof["exit"]==[1100,704],(name,proof)
                    assert proof["next"]==[0,704],(name,proof)
                    assert proof["matching"] and proof["unapproved"] and proof["bakedLabel"],(name,proof)
                    assert proof["selected"]=="bridge" and proof["southExit"]==[315,842] and proof["noHairpin"],(name,proof)
                    assert proof["sourceImageReady"] and proof["sourceImageExternal"],(name,proof)
                    assert proof["exportGate"]["traversable"] is False,(name,proof)
                    assert "authoring_export_requires_independent_approval" in proof["exportGate"]["reasons"],(name,proof)
                    page.locator("#east").click()
                    page.screenshot(path=str(OUT/(name+"-east.png")),animations="disabled")
                    page.locator("#menu").click()
                    page.locator("#raw").click()
                    assert page.evaluate("Octagon1Proof.rawArtOnly") is True,name
                    page.screenshot(path=str(OUT/(name+"-raw-source.png")),animations="disabled")
                    page.locator("#raw").click()
                    assert page.evaluate("Octagon1Proof.rawArtOnly") is False,name
                    page.locator("#menu").click()
                    page.locator("#edit").click()
                    assert page.evaluate("Octagon1Proof.editMode") is True,name
                    page.screenshot(path=str(OUT/(name+"-editor.png")),animations="disabled")
                    # Changing a road waypoint MUST change both rendered geometry and unit movement.
                    before=page.evaluate("Octagon1Proof.route")
                    after=page.evaluate("""() => {
                        const p=Octagon1Proof.eastPoints;
                        p[6][1]-=3;
                        Octagon1Proof.setRoadCandidate(p);
                        return {route:Octagon1Proof.route,matching:Octagon1Proof.routeAndInkSame};
                    }""")
                    assert after["matching"] is True,name
                    assert before!=after["route"],name
                    assert after["route"][51+6][1]==before[51+6][1]-3,name
                    # The former east-bank road loop should be absent.
                    assert page.evaluate("Octagon1Proof.landBankCandidateHasHairpin === false"),name
                    # Both branch alternatives share one fork and can each receive valid movement orders.
                    page.locator("#edit").click()
                    page.locator("#menu").click()
                    page.locator("#forkStart").click()
                    fork_before=page.evaluate("Octagon1Proof.movementPoint")
                    page.locator("#chooseSouth").click()
                    south=page.evaluate("""() => ({
                      route:Octagon1Proof.activeRoute,
                      exit:Octagon1Proof.southExit,
                      matched:Octagon1Proof.routeAndInkSame,
                      length:Octagon1Proof.route.length,
                      pos:Octagon1Proof.movementPoint
                    })""")
                    assert south["route"]=="south" and south["exit"]==[315,842] and south["matched"],(name,south)
                    assert south["pos"]==fork_before,(name,south)
                    assert south["length"]==43,(name,south)
                    south_finish=page.evaluate("Octagon1Proof.setArmyProgress(1)")
                    assert south_finish==[315,842],(name,south_finish)
                    page.locator("#chooseBridge").click()
                    bridge=page.evaluate("""fork => ({
                      route:Octagon1Proof.activeRoute,matched:Octagon1Proof.routeAndInkSame,
                      atFork:Math.hypot(...Octagon1Proof.movementPoint.map((n,i)=>n-fork[i]))<1e-6
                    })""",fork_before)
                    assert bridge["route"]=="bridge" and bridge["matched"] and bridge["atFork"],(name,bridge)
                    page.locator("#menu").click()
                    page.screenshot(path=str(OUT/(name+"-two-routes.png")),animations="disabled")
                    for f in [0,.2,.5,.8,1]:
                        pos=page.evaluate("f => Octagon1Proof.setArmyProgress(f)",f)
                        assert 0<=pos[0]<=1100 and 0<=pos[1]<=842,(name,f,pos)
                    assert not errors,(name,errors)
                    results[name]={"passed":True,"checks":proof,"changed_waypoint":True,"errors":errors}
                finally:
                    page.close()
            browser.close()
finally:
    srv.shutdown()
report={"passed":len(results)==4 and all(x["passed"] for x in results.values()),
        "results":results,
        "physical_iPhone_approved":False,
        "source_water_bank_review_complete":False,
        "original_art_repaired":False,
        "historical_road_verified":False,
        "neighboring_octagon_built":False,
        "production_octagon_ready":False}
(OUT/"report.json").write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report,indent=2))
if not report["passed"]:raise SystemExit(1)

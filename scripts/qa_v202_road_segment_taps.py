#!/usr/bin/env python3
"""V202: road taps select the closest painted V123 SEGMENT, not a global vertex.

Phone-layout Chromium/WebKit tests; not physical iPhone, historical, or art approval.
"""
import http.server
import json
import math
import subprocess
import threading
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"qa"/"v202-road-segment-taps"
OUT.mkdir(parents=True,exist_ok=True)
PINNED={
    "v121-octagon-1-painted-road.html":"4c6aa5cda9e7c359b6d2a49d5b5fe8a597346382",
    "terrain-grid/v123-atlas.js":"09f04b4062e24fbacbb645307462cdddce2b2aa3",
}
for path,sha in PINNED.items():
    assert subprocess.check_output(["git","hash-object",path],cwd=ROOT,text=True).strip()==sha,path

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,directory=str(ROOT),**kwargs)
    def log_message(self,*args):pass

def closest_segment(point,tiles):
    """Independent geometry oracle; tie-breaking matches atlas tile/road order."""
    best=None
    for tile in tiles:
        ox,oy=tile["origin"]
        for road,points in tile["roads"].items():
            for index,(a,b) in enumerate(zip(points,points[1:])):
                ax,ay=a[0]+ox,a[1]+oy
                bx,by=b[0]+ox,b[1]+oy
                dx,dy=bx-ax,by-ay
                den=dx*dx+dy*dy
                assert den>0
                t=max(0,min(1,((point[0]-ax)*dx+(point[1]-ay)*dy)/den))
                distance=math.hypot(point[0]-ax-t*dx,point[1]-ay-t*dy)
                if best is None or distance<best["distance"]:
                    local=a if t<=.5 else b
                    best={"distance":distance,"tile":tile["id"],"road":road,
                          "index":index,"target":[local[0]+ox,local[1]+oy]}
    return best

def test_points(tiles):
    result=[]
    for tile in tiles:
        for road,points in tile["roads"].items():
            if tile["id"]=="matrei":
                # Matrei's original painting is not reauthored or surveyed.
                # A few internal segment clicks still exercise its routing.
                indices=[max(0,len(points)//3-1)]
            else:
                indices=[2,min(6,len(points)-2),len(points)-2]
            for index in sorted(set(indices)):
                a,b=points[index:index+2]
                for t in (.22,.78):
                    result.append({"point":[tile["origin"][0]+a[0]+t*(b[0]-a[0]),
                                            tile["origin"][1]+a[1]+t*(b[1]-a[1])],
                                   "sourceTile":tile["id"],"road":road})
    return result

server=http.server.ThreadingHTTPServer(("127.0.0.1",0),Handler)
threading.Thread(target=server.serve_forever,daemon=True).start()
url=f"http://127.0.0.1:{server.server_port}/v192-weathered-cartways-graphics-test.html"
results={}
try:
    with sync_playwright() as playwright:
        for engine in ("chromium","webkit"):
            browser=getattr(playwright,engine).launch(headless=True)
            try:
                for orientation,width,height in (("portrait",390,844),("landscape",844,390)):
                    key=f"{engine}-{orientation}"
                    page=browser.new_page(viewport={"width":width,"height":height},
                        is_mobile=True,has_touch=True,device_scale_factor=2)
                    errors=[]
                    page.on("pageerror",lambda error:errors.append(str(error)))
                    try:
                        page.goto(url,wait_until="domcontentloaded",timeout=30000)
                        page.wait_for_function("window.V192?.ready===true",timeout=120000)
                        tiles=page.evaluate("""async () => {
                            const html=await(await fetch('v121-octagon-1-painted-road.html')).text();
                            const m=html.match(/const ROADS=(\\{[^\\r\\n]+\\});/);
                            if(!m)throw Error('Missing pinned V121 road controls');
                            return V123Atlas.create(JSON.parse(m[1]),{experimentalSeams:true}).tiles
                                .map(t=>({id:t.id,origin:t.origin,roads:t.roads}));
                        }""")
                        samples=test_points(tiles)
                        assert len(samples)>=14,len(samples)
                        checked=0
                        for sample in samples:
                            p=sample["point"]
                            expected=closest_segment(p,tiles)
                            assert expected["distance"]<1e-6,(sample,expected)
                            assert page.evaluate("(p)=>V192.tapRoadWorld(p)",p),(key,p)
                            route=page.evaluate("V192.route")
                            assert route,(key,sample)
                            assert math.dist(route[-1],expected["target"])<1e-5,(
                                "tap snapped to wrong road vertex",key,sample,expected,route[-1])
                            assert page.evaluate("(p)=>V192.roadDistance(p)",p)<.001
                            assert page.evaluate("V192.productionApproved") is False
                            checked+=1
                        # Independently located V121 bridge-neighborhood cases:
                        # old global-nearest-node snapping chose an adjacent
                        # road vertex instead of the closest painted segment.
                        # Both lie within the original mobile tap tolerance.
                        for point,target,wrong_old_vertex in (
                            ([2072,496],[2054,519],[2052,491]),
                            ([2080,488],[2102,508],[2052,491]),
                        ):
                            assert page.evaluate("(p)=>V192.tapRoadWorld(p)",point),(key,point)
                            selected=page.evaluate("V192.route")[-1]
                            assert math.dist(selected,target)<1e-5,(key,point,selected,target)
                            assert math.dist(selected,wrong_old_vertex)>1,(key,point)
                        # No invisible path outside the two unverified terminal
                        # vertices: these clicks are far beyond the tap tolerance.
                        limits=page.evaluate("V192.surveyLimits")
                        assert len(limits["markers"])==2
                        assert all(m["onwardRoadVerified"] is False for m in limits["markers"])
                        for p in ([80,615],[3010,1700],[100,100]):
                            before=page.evaluate("V192.route")
                            assert page.evaluate("(p)=>V192.tapRoadWorld(p)",p) is False,(key,p)
                            assert page.evaluate("V192.route")==before
                        # Halting mid-edge and reissuing must never leave V123 paint.
                        assert page.evaluate("V192.orderTo('south')")
                        point=page.evaluate("V192.progress(.43)")
                        assert page.evaluate("(p)=>V192.roadDistance(p)",point)<.001
                        page.evaluate("V192.halt()")
                        assert page.evaluate("V192.orderTo('west')")
                        for fraction in (.1,.35,.7):
                            point=page.evaluate("(f)=>V192.progress(f)",fraction)
                            assert page.evaluate("(p)=>V192.roadDistance(p)",point)<.001
                        assert page.evaluate("V192.focusTile('west')")
                        page.evaluate("V192.zoomTo(6)")
                        page.evaluate("() => new Promise(done=>requestAnimationFrame(()=>requestAnimationFrame(done)))")
                        page.screenshot(path=str(OUT/f"{key}-west.png"),animations="disabled")
                        assert page.evaluate("V192.focusTile('south')")
                        page.evaluate("V192.zoomTo(6)")
                        page.evaluate("() => new Promise(done=>requestAnimationFrame(()=>requestAnimationFrame(done)))")
                        page.screenshot(path=str(OUT/f"{key}-south.png"),animations="disabled")
                        assert not errors,(key,errors)
                        results[key]={"passed":True,"roadTapSamples":checked,
                            "outsideSurveyedGraphRejected":True,
                            "midEdgeHaltAndReorderOnPaint":True,
                            "sourceBlobsUnchanged":True}
                    finally:page.close()
            finally:browser.close()
finally:server.shutdown()

report={"passed":len(results)==4,"results":results,
        "gameArtApproved":False,"historicRoadVerified":False,
        "physicalIPhoneApproved":False,"productionApproved":False,
        "note":"Segment-safe phone-layout tap routing; not an art/historical acceptance."}
(OUT/"report.json").write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report,indent=2),flush=True)
assert report["passed"]

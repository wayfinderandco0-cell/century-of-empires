#!/usr/bin/env python3
"""V123 standalone scene mobile smoke and route-halt continuity QA."""
import http.server
import json
import math
import threading
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "qa" / "v123-three-octagons"
OUT.mkdir(parents=True, exist_ok=True)

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)
    def log_message(self, *_args):
        pass

server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
threading.Thread(target=server.serve_forever, daemon=True).start()
URL = "http://127.0.0.1:%s/v123-three-octagon-preview.html" % server.server_port
report = {}
try:
    with sync_playwright() as p:
        for engine in ("chromium", "webkit"):
            browser = getattr(p, engine).launch(headless=True)
            try:
                for orient, w, h in (("portrait",390,844),("landscape",844,390)):
                    key = engine + "-" + orient
                    page = browser.new_page(viewport={"width":w,"height":h}, has_touch=True, is_mobile=True, device_scale_factor=2)
                    errors = []
                    page.on("pageerror", lambda e, arr=errors: arr.append(str(e)))
                    try:
                        page.goto(URL,wait_until="domcontentloaded",timeout=30000)
                        page.wait_for_function("window.V123?.ready === true",timeout=30000)
                        before = page.evaluate("""() => ({
                          dims:V123.artDimensions,
                          graphSize:V123.roadNodeCount,
                          exits:V123.seamStatus,
                          production:V123.productionApproved,
                          route:V123.connectedRoute,
                          army:V123.point,
                          experimental:V123.experimental,
                        })""")
                        assert before["dims"] == [1536,1024], (key,before)
                        assert before["graphSize"] >= 90, (key,before)
                        assert before["route"], (key,before)
                        assert len(before["exits"])==2 and all(t["pass"] for t in before["exits"])
                        assert not before["production"] and before["experimental"]
                        closed = page.evaluate("() => V123.testTapWorld([1536+1049,208.5])")
                        assert not closed["ok"] and not closed["moving"], (key,closed)
                        assert "Road closed" in closed["status"], (key,closed)
                        assert math.dist(closed["point"],before["army"])<0.001,(key,closed)
                        page.screenshot(path=str(OUT/(key+"-opening.png")),animations="disabled")
                        assert page.evaluate("V123.orderTo('west')"),key
                        mid = page.evaluate("V123.progress(.38)")
                        assert page.evaluate("V123.moving"),key
                        page.evaluate("V123.halt()")
                        halted = page.evaluate("V123.point")
                        assert math.dist(mid,halted)<0.0001, (key,mid,halted)
                        assert page.evaluate("V123.orderTo('south')"),key
                        changed = page.evaluate("V123.route")
                        assert len(changed)>=4 and math.dist(changed[0],halted)<0.001,(key,changed[:2],halted)
                        for f in (0,.12,.4,.7,1):
                            sample=page.evaluate("f => V123.progress(f)",f)
                            assert sample and all(math.isfinite(n) for n in sample), (key,f,sample)
                        assert math.dist(page.evaluate("V123.point"),[2806,1629])<0.01,key
                        page.evaluate("V123.inspect()")
                        page.screenshot(path=str(OUT/(key+"-road-debug.png")),animations="disabled")
                        page.evaluate("V123.inspect()")
                        assert not errors,(key,errors)
                        report[key]={"passed":True,"roadNodes":before["graphSize"],"paintedSource":before["dims"],"seams":len(before["exits"]),"midroadHaltPreserved":True,"closedRoadTapRejected":True}
                    finally:
                        page.close()
            finally:
                browser.close()
finally:
    server.shutdown()
out={"pass":len(report)==4,"results":report,"physicalIphoneApproved":False,"historicallyVerified":False,"campaignIntegrated":False}
(OUT/"report.json").write_text(json.dumps(out,indent=2)+"\n")
print(json.dumps(out,indent=2))
assert out["pass"]

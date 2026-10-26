#!/usr/bin/env python3
"""V193: mobile camera/pinch bounds; visual and historical approval remain separate."""
import http.server
import json
import subprocess
import threading
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "qa" / "v193-camera-coverage"
OUT.mkdir(parents=True, exist_ok=True)
# Git blob identities are pinned from the unchanged V192 parent. These protect
# the original painted road image and immutable V123 path graph from silent edits.
SOURCE_BLOBS = {
    "v121-octagon-1-painted-road.html": "4c6aa5cda9e7c359b6d2a49d5b5fe8a597346382",
    "terrain-grid/v123-atlas.js": "09f04b4062e24fbacbb645307462cdddce2b2aa3",
}

for path, expected in SOURCE_BLOBS.items():
    actual = subprocess.check_output(
        ["git", "hash-object", path], cwd=ROOT, text=True
    ).strip()
    if actual != expected:
        raise AssertionError(f"Immutable V121/V123 source drift: {path}: {actual}")

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)
    def log_message(self, *args):
        pass

def check_coverage(info):
    x0, y0, x1, y1 = info["visible"]
    gx, gy, gw, gh = info["groundBounds"]
    eps = 0.001
    assert x0 >= gx - eps and y0 >= gy - eps, info
    assert x1 <= gx + gw + eps and y1 <= gy + gh + eps, info
    assert .7 <= info["zoom"] <= 7.00001, info
    assert info["zoom"] + eps >= info["minZoom"], info

def dispatch_gesture(page, kind, width, height):
    return page.evaluate("""({kind,width,height}) => {
        const canvas = document.querySelector('#map');
        const original = canvas.setPointerCapture;
        // Synthetic pointer events cannot claim browser hardware capture.
        // The real app handler still processes exactly the same event stream.
        canvas.setPointerCapture = () => {};
        const x = width / 2, y = height / 2;
        const fire = (type, id, px, py) => canvas.dispatchEvent(
          new PointerEvent(type, {bubbles:true, pointerId:id,
            pointerType:'touch', clientX:px, clientY:py, isPrimary:id===11}));
        const before = V192.terrainCamera;
        try {
          if(kind === 'pinch'){
            fire('pointerdown',11,x-45,y);
            fire('pointerdown',12,x+45,y);
            fire('pointermove',11,x-75,y);
            fire('pointermove',12,x+75,y);
            fire('pointerup',11,x-75,y);
            fire('pointerup',12,x+75,y);
          } else {
            fire('pointerdown',13,x,y);
            fire('pointermove',13,x+5000,y+5000);
            fire('pointerup',13,x+5000,y+5000);
          }
        } finally { canvas.setPointerCapture = original; }
        return {before,after:V192.terrainCamera};
    }""", {"kind":kind, "width":width, "height":height})

server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
threading.Thread(target=server.serve_forever, daemon=True).start()
address = f"http://127.0.0.1:{server.server_port}/v192-weathered-cartways-graphics-test.html"
results = {}
try:
    with sync_playwright() as playwright:
        for engine in ("chromium", "webkit"):
            browser = getattr(playwright, engine).launch(headless=True)
            try:
                for orient, width, height in (("portrait",390,844),("landscape",844,390)):
                    page = browser.new_page(viewport={"width":width,"height":height},
                        is_mobile=True, has_touch=True, device_scale_factor=2)
                    errors = []
                    page.on("pageerror", lambda err: errors.append(str(err)))
                    try:
                        page.goto(address, wait_until="domcontentloaded", timeout=30000)
                        page.wait_for_function("window.V192?.ready===true", timeout=120000)
                        assert page.evaluate("V192.connectedRoute")
                        assert not page.evaluate("V192.productionApproved")
                        assert not page.evaluate("V192.historicRouteVerified")
                        check_coverage(page.evaluate("V192.terrainCamera"))
                        for region in ("west","matrei","south"):
                            assert page.evaluate("(name) => V192.focusTile(name)",region)
                            page.evaluate("V192.zoomTo(6)")
                            check_coverage(page.evaluate("V192.terrainCamera"))
                        # Deliberate overscroll: the camera must not reveal blank canvas.
                        drag = dispatch_gesture(page, "drag", width, height)
                        check_coverage(drag["after"])
                        # Return to an unclamped center before testing pinch anchoring.
                        assert page.evaluate("V192.focusTile('matrei')")
                        page.evaluate("V192.zoomTo(2.4)")
                        pinch = dispatch_gesture(page, "pinch", width, height)
                        check_coverage(pinch["after"])
                        assert pinch["after"]["zoom"] > pinch["before"]["zoom"] * 1.4, pinch
                        before, after = pinch["before"], pinch["after"]
                        assert max(abs(a-b) for a,b in zip(before["center"],after["center"])) < .01, pinch
                        page.screenshot(path=str(OUT/f"{engine}-{orient}-pinch.png"), animations="disabled")
                        # Deliberate zoom-out beyond minimum: clamp to painted extent.
                        page.evaluate("V192.zoomTo(.01)")
                        whole = page.evaluate("V192.terrainCamera")
                        check_coverage(whole)
                        assert abs(whole["zoom"] - whole["minZoom"]) < .0001, whole
                        page.evaluate("() => new Promise(done => requestAnimationFrame(() => requestAnimationFrame(done)))")
                        page.screenshot(path=str(OUT/f"{engine}-{orient}-minimum-zoom.png"), animations="disabled")
                        assert not errors, (engine, orient, errors)
                        results[f"{engine}-{orient}"] = {
                            "passed":True,"minimumZoom":round(whole["minZoom"],4),
                            "pinchAnchored":True,"overscrollClamped":True,
                            "sourceBlobsUnmodified":True}
                    finally:
                        page.close()
            finally:
                browser.close()
finally:
    server.shutdown()

report = {"passed":len(results)==4,"results":results,
    "sourceBlobs":SOURCE_BLOBS,
    "historicalRoadVerified":False,"gameArtApproved":False,
    "physicalIPhoneApproved":False,"productionApproved":False,
    "performanceBenchmarked":False,
    "note":"Browser gesture simulation is not physical iPhone acceptance; no new roads or imagery."}
(OUT/"report.json").write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report,indent=2),flush=True)
assert report["passed"]

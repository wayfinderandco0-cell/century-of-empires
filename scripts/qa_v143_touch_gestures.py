#!/usr/bin/env python3
"""iPhone-sized pan and two-pointer pinch regression for the V140 experimental scene.

Synthetic DOM PointerEvents test camera math in both Chromium and WebKit. They
are NOT physical iPhone multitouch, geographic validation, or art acceptance.
"""
import http.server
import json
import threading
import urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'qa' / 'v143-gestures'
OUT.mkdir(parents=True, exist_ok=True)

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)
    def log_message(self, *args):
        pass

server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), Handler)
threading.Thread(target=server.serve_forever, daemon=True).start()
url = f'http://127.0.0.1:{server.server_port}/v137-coherent-alpine-preview.html'
with urllib.request.urlopen(url, timeout=5) as response:
    assert response.status == 200 and b'V137 Three-Octagon Route Preview' in response.read()

JS_GESTURES = r'''() => {
  const c = document.querySelector('#map');
  const savedCapture = c.setPointerCapture;
  // Browser-generated pointer capture requires a physical active pointer.
  // Stub ONLY that browser primitive; exercise the actual game's listeners.
  c.setPointerCapture = () => {};
  const event = (kind,id,x,y) => c.dispatchEvent(new PointerEvent(kind, {
    bubbles:true, pointerId:id, pointerType:'touch', isPrimary:id===1,
    clientX:x, clientY:y, buttons:kind==='pointerup'?0:1
  }));
  const near = (a,b,epsilon=0.001) => Math.abs(a-b)<=epsilon;
  const midpoint = [width*.5,height*.5];
  const armyBefore = V137.point.slice();
  const routeBefore = JSON.stringify(V137.route);
  try {
    V137.focusTile('matrei');
    const start = {cam:cam.slice(),zoom,scale};
    event('pointerdown',1,midpoint[0],midpoint[1]);
    event('pointermove',1,midpoint[0]+60,midpoint[1]+35);
    event('pointerup',1,midpoint[0]+60,midpoint[1]+35);
    const pan = {cam:cam.slice(),zoom,scale};
    if(!near(pan.cam[0],start.cam[0]-60/start.scale) ||
       !near(pan.cam[1],start.cam[1]-35/start.scale))
      throw Error('Single-finger pan displaced world camera incorrectly');
    if(!near(pan.zoom,start.zoom))throw Error('Pan changed zoom');
    // Pinch expands around a midpoint which itself moves 30px to the right.
    // World location beneath the fingers' original midpoint must be preserved
    // beneath their new midpoint, even when zoom and pan happen together.
    const firstMid=[midpoint[0],midpoint[1]];
    const fixedWorld=world(firstMid);
    event('pointerdown',11,firstMid[0]-50,firstMid[1]);
    event('pointerdown',12,firstMid[0]+50,firstMid[1]);
    event('pointermove',11,firstMid[0]-40,firstMid[1]-20);
    event('pointermove',12,firstMid[0]+100,firstMid[1]+20);
    const finalMid=[firstMid[0]+30,firstMid[1]];
    const after=world(finalMid);
    const anchorError=Math.hypot(after[0]-fixedWorld[0],after[1]-fixedWorld[1]);
    const pinchZoom=zoom;
    event('pointerup',11,firstMid[0]-40,firstMid[1]-20);
    event('pointerup',12,firstMid[0]+100,firstMid[1]+20);
    if(anchorError>.001)throw Error('Pinch midpoint world anchor drift: '+anchorError);
    if(pinchZoom<=pan.zoom*1.1)throw Error('Two-finger pinch did not zoom');
    if(JSON.stringify(V137.point)!==JSON.stringify(armyBefore))
      throw Error('Camera gesture moved the army');
    if(JSON.stringify(V137.route)!==routeBefore)
      throw Error('Camera gesture changed route topology');
    if(pointers.size || gesture!==null)throw Error('Pointer gesture leaked active state');
    redraw();
    return {panDeltaWorld:[pan.cam[0]-start.cam[0],pan.cam[1]-start.cam[1]],
      zoomBefore:pan.zoom,zoomAfter:pinchZoom,anchorErrorWorld:anchorError,
      armyUnaffected:true,routeUnaffected:true};
  } finally {c.setPointerCapture=savedCapture;}
}'''

results = {}
try:
    with sync_playwright() as playwright:
        for engine in ('chromium','webkit'):
            browser = getattr(playwright,engine).launch(headless=True)
            try:
                for orientation,w,h in (('portrait',390,844),('landscape',844,390)):
                    page=browser.new_page(viewport={'width':w,'height':h},
                        is_mobile=True,has_touch=True,device_scale_factor=2)
                    errors=[]
                    page.on('pageerror',lambda error: errors.append(str(error)))
                    page.goto(url,wait_until='domcontentloaded',timeout=30000)
                    page.wait_for_function('window.V137?.ready===true',timeout=30000)
                    result=page.evaluate(JS_GESTURES)
                    assert not errors,(engine,orientation,errors)
                    assert result['armyUnaffected'] and result['routeUnaffected']
                    assert result['anchorErrorWorld']<=.001
                    page.screenshot(path=str(OUT/f'{engine}-{orientation}-after-pan-pinch.png'),
                                    animations='disabled')
                    results[f'{engine}-{orientation}']=result
                    page.close()
            finally:
                browser.close()
finally:
    server.shutdown()
report={'passed':len(results)==4,'results':results,
        'realHardwareTouchVerified':False,'artAccepted':False,
        'geographicRoadAlignmentVerified':False}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
assert report['passed']

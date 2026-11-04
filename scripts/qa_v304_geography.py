"""V304: mobile WebKit + Chromium proof for passive geographical terrain."""
import functools
import http.server
import pathlib
import threading
from playwright.sync_api import sync_playwright

ROOT=pathlib.Path(__file__).resolve().parents[1]
OUT=ROOT/'qa'/'v304'
OUT.mkdir(parents=True,exist_ok=True)

class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*args): pass

# Test fixture only: an artificial land mask avoids relying on the remote
# historical boundary API. It is not used as game geography.
MASK={"type":"FeatureCollection","features":[{
    "type":"Feature","properties":{"NAME":"Austria","SUBJECTO":"Austria"},
    "geometry":{"type":"Polygon","coordinates":[[
      [-14,26],[49,26],[49,75],[-14,75],[-14,26]]]}}]}

def run(browser_type,name,url):
    browser=browser_type.launch(headless=True)
    context=browser.new_context(viewport={"width":390,"height":844},device_scale_factor=2,
                                has_touch=True,is_mobile=True)
    page=context.new_page()
    errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.route("**/world_1783.geojson",lambda r:r.fulfill(json=MASK))
    response=page.goto(url,wait_until="load",timeout=45000)
    assert response and response.status==200
    page.wait_for_function("""() => window.COEMapArt?.debug?.overviewPresent &&
      document.querySelector('#historicalMaskPaths path')""",timeout=20000)
    geo=page.evaluate("window.COEMapArt.debug.project(11.5,47)")
    assert abs(geo['x']-(42+(11.5+15)*25.3))<.0001,geo
    assert abs(geo['y']-(34+(73-47)*25.2))<.0001,geo
    assert page.locator('#map #coeg-overview').count()==1
    page.locator('#startBtn').click()
    assert page.locator('#startOverlay').is_hidden()
    assert page.locator('#marchBtn').count()==1  # unchanged original orders
    assert page.locator('#mapZoomIn').count()==1
    state=page.evaluate("window.COEMapArt.debug")
    assert state['renderOnly'] and state['tileCount']==0,state
    page.screenshot(path=str(OUT/f'{name}-overview.png'))
    page.locator('#mapZoomIn').click()
    page.locator('#mapZoomIn').click()
    page.wait_for_function("""() => window.COEMapArt.debug.viewMode==='detail'
      && window.COEMapArt.debug.tileCount>0""",timeout=10000)
    page.wait_for_function("window.COEMapArt.debug.loadedTiles>0",timeout=15000)
    before=page.evaluate("window.COEMapArt.debug.tileKeys")
    page.screenshot(path=str(OUT/f'{name}-detail.png'))
    page.locator('#mapZoomOut').click()
    page.locator('#mapZoomOut').click()
    page.wait_for_function("window.COEMapArt.debug.viewMode==='overview'",timeout=10000)
    assert page.evaluate("window.COEMapArt.debug.tileCount")==0
    assert page.locator('#map #coeg-overview').count()==1
    assert not errors,errors
    print(f"PASS {name}: overview+{len(before)} viewport-local high resolution tiles; original campaign intact; no JS errors")
    context.close();browser.close()

def main():
    server=http.server.ThreadingHTTPServer(('127.0.0.1',0),
             functools.partial(Quiet,directory=str(ROOT)))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    try:
        url=f'http://127.0.0.1:{server.server_port}/index.html'
        with sync_playwright() as pw:
            for browser in ('webkit','chromium'):
                run(getattr(pw,browser),browser,url)
    finally:
        server.shutdown();server.server_close()

if __name__=='__main__': main()

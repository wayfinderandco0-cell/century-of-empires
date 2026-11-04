"""V305 mobile browsers: real source image, streams, geography and campaign invariance."""
import functools
import http.server
import pathlib
import threading
from playwright.sync_api import sync_playwright

ROOT=pathlib.Path(__file__).resolve().parents[1]
OUT=ROOT/'qa'/'v305'
OUT.mkdir(parents=True,exist_ok=True)

class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*args): pass

HISTORICAL_POLYGON={"type":"FeatureCollection","features":[{
 "type":"Feature","properties":{"NAME":"Austria","SUBJECTO":"Austria"},
 "geometry":{"type":"Polygon","coordinates":[[
 [-14,26],[49,26],[49,75],[-14,75],[-14,26]
 ]]}}]}

def test(browser_type,name,base):
    browser=browser_type.launch(headless=True)
    ctx=browser.new_context(viewport={"width":390,"height":844},device_scale_factor=2,
                            has_touch=True,is_mobile=True)
    page=ctx.new_page()
    errors=[]
    page.on("pageerror",lambda e:errors.append(str(e)))
    response=page.goto(base+'/brenner-corridor.html?year=1780',wait_until='load')
    assert response.status==200
    page.wait_for_function("window.COEBrenner && window.COEBrenner.ready",timeout=30000)
    q=page.evaluate("""() => ({
      count: COEBrenner.streams,year:COEBrenner.year,geo:COEBrenner.geoToPixel(11.45366,47.13125),
      roundtrip: COEBrenner.pixelToGeo(...Object.values(COEBrenner.geoToPixel(11.45366,47.13125))),
      roadsGeoregistered: COEBrenner.roadsHistoricallyGeoreferenced,
      campaignPreserved: COEBrenner.campaignPreserved,
      width:document.querySelector('#geo').width,
      frames:COEBrenner.frames
    })""")
    assert q['count']>30,q
    assert q['year']==1780 and not q['roadsGeoregistered'] and q['campaignPreserved']
    assert abs(q['roundtrip']['lon']-11.45366)<1e-6
    assert abs(q['roundtrip']['lat']-47.13125)<1e-6
    assert q['width']==780 and q['frames']>0,q
    page.screenshot(path=str(OUT/(name+'-brenner.png')))
    scale=page.evaluate("COEBrenner.scale")
    page.locator('#in').click()
    assert page.evaluate("COEBrenner.scale")>scale
    page.locator('#all').click()
    assert page.evaluate("COEBrenner.scale")<scale*1.001
    page.locator('#art').click()
    assert page.locator('#photo').is_visible()
    assert page.locator('#photo img').count()==4
    page.locator('#closePhoto').click()
    assert not page.locator('#photo').is_visible()
    page.goto(base+'/index.html',wait_until='load',timeout=60000)
    page.route('**/world_1783.geojson',lambda r:r.fulfill(json=HISTORICAL_POLYGON))
    page.locator('#startBtn').click()
    page.wait_for_timeout(350)
    original=page.evaluate("JSON.stringify(Object.assign({},localStorage))")
    assert page.locator('#marchBtn').count()==1
    assert page.locator('#brennerLensPin').count()==1
    page.locator('#brennerLensBtn').click()
    frame=page.frame_locator('#brennerLensFrame')
    frame.locator('#geo').wait_for(state='visible',timeout=30000)
    frame.locator('#status').wait_for(state='visible')
    page.wait_for_function("""() => {
      const f=document.querySelector('#brennerLensFrame')?.contentWindow;
      return !!f?.COEBrenner?.ready
    }""",timeout=30000)
    year=frame.locator('#era').inner_text()
    assert '1780' in year,year
    page.screenshot(path=str(OUT/(name+'-in-campaign.png')))
    page.locator('#brennerLensClose').click()
    assert page.locator('#brennerLens').is_hidden()
    assert page.locator('#marchBtn').count()==1
    assert page.evaluate("JSON.stringify(Object.assign({},localStorage))")==original
    assert not errors,errors
    print(f'PASS {name}: {q["count"]} real local streams, geo roundtrip, iPhone map, original campaign and saves unchanged')
    ctx.close();browser.close()

def main():
    server=http.server.ThreadingHTTPServer(('127.0.0.1',0),
       functools.partial(Quiet,directory=str(ROOT)))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    try:
        root=f'http://127.0.0.1:{server.server_port}'
        with sync_playwright() as pw:
            for name in ('webkit','chromium'):
                test(getattr(pw,name),name,root)
    finally:server.shutdown();server.server_close()

if __name__=='__main__':main()

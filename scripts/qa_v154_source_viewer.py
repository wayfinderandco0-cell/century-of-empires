#!/usr/bin/env python3
"""V154: four browser/mobile layouts validate source identity and distinct sector rendering.
Synthetic source fixture offline; CI also uses the real 27-JPEG V153 source mosaic.
This is NOT V123 road registration or game visual approval.
"""
import hashlib
import http.server
import json
import os
import threading
from pathlib import Path
from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'qa/v154-source-viewer'
OUT.mkdir(parents=True, exist_ok=True)
SOURCE = ROOT / 'qa/v153-geographic-strip'
SOURCE.mkdir(parents=True, exist_ok=True)

# Offline mode: a distinct color in each sector exposes blank/duplicated areas.
if not (SOURCE / 'manifest.json').exists():
    image = Image.new('RGB', (2304,768))
    for sector, rgb in enumerate(((188,57,50),(40,169,78),(54,85,197))):
        image.paste(rgb, (sector*768,0,(sector+1)*768,768))
    image.save(SOURCE/'modern-source-strip.png')
    m={'version':153,'crs':'EPSG:3857','provider':'basemap.at',
       'requiredAttribution':'Datenquelle: basemap.at','grid':[3,9],
       'pixelDimensions':[2304,768],'mosaicFile':'modern-source-strip.png',
       'mosaicSha256':hashlib.sha256((SOURCE/'modern-source-strip.png').read_bytes()).hexdigest(),
       'sectors':[{'name':f'source-{name}','pixelBounds':[i*768,0,(i+1)*768,768]}
                  for i,name in enumerate(('west','center','east'))],
       'samples':[{'gridRow':r,'gridCol':c,'tileXYZ':[7000+c,5000+r,17]}
                  for r in range(3) for c in range(9)]}
    for key in ('gameOctagonCentersCertified','gameRouteGeoregistered',
                'historic1780Certified','navigableRouteCertified','bridgeBanksVerified','productionApproved'):
        m[key]=False
    (SOURCE/'manifest.json').write_text(json.dumps(m))
    mode='synthetic'
else:
    mode='authentic'

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self,*a,**kw):super().__init__(*a,directory=str(ROOT),**kw)
    def log_message(self,*args):pass

server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler)
threading.Thread(target=server.serve_forever,daemon=True).start()
url=f'http://127.0.0.1:{server.server_port}/v154-geographic-source-review.html'
results={}
try:
    with sync_playwright() as p:
        for engine in (('chromium',) if os.environ.get('V154_CHROMIUM_ONLY') else ('chromium','webkit')):
            browser=getattr(p,engine).launch(headless=True,**({'executable_path':'/usr/bin/chromium'} if os.environ.get('V154_CHROMIUM_ONLY') else {}))
            try:
                for orientation,w,h in (('portrait',390,844),('landscape',844,390)):
                    page=browser.new_page(viewport={'width':w,'height':h},is_mobile=True,
                                          has_touch=True,device_scale_factor=2)
                    errors=[]
                    page.on('pageerror',lambda e:errors.append(str(e)))
                    page.goto(url,wait_until='domcontentloaded',timeout=30000)
                    page.wait_for_function('window.V154?.ready === true',timeout=30000)
                    assert page.evaluate('V154.sourceOnly && !V154.productionApproved && !V154.gameRouteGeoregistered')
                    assert page.evaluate('V154.manifest.samples.length')==27
                    page.evaluate('V154.setTier(0)')
                    page.screenshot(path=str(OUT/f'{engine}-{orientation}-overview.png'))
                    centers=[]
                    for idx,name in enumerate(('west','center','east')):
                        assert page.evaluate('([i])=>V154.focusSector(i,3)',[idx])
                        assert page.evaluate('V154.tier')==3
                        xy=page.evaluate('V154.screenToSource(document.querySelector("#map").clientWidth/2,document.querySelector("#map").clientHeight/2)')
                        assert abs(xy[0]-(384+idx*768))<1e-5 and abs(xy[1]-384)<1e-5,(engine,orientation,name,xy)
                        sample=page.evaluate('''() => {const c=document.querySelector('#map');
                            return [...c.getContext('2d').getImageData(Math.floor(c.width/2),Math.floor(c.height/2),1,1).data];}''')
                        assert sample[3]==255 and len(sample)==4
                        if mode=='synthetic':
                            expected=((188,57,50),(40,169,78),(54,85,197))[idx]
                            assert all(abs(sample[k]-expected[k])<=2 for k in range(3)),(name,sample)
                        centers.append(sample[:3])
                        page.screenshot(path=str(OUT/f'{engine}-{orientation}-{name}.png'))
                    if mode=='authentic':
                        # Three independent camera centers must not render an identical raster.
                        assert len({tuple(rgb) for rgb in centers})==3,(engine,orientation,centers)
                    # Anchored zoom preserves the source point under the screen center.
                    page.evaluate('V154.focusSector(1,2)')
                    before=page.evaluate('V154.screenToSource(document.querySelector("#map").clientWidth/2,document.querySelector("#map").clientHeight/2)')
                    page.evaluate('V154.setTier(3)')
                    after=page.evaluate('V154.screenToSource(document.querySelector("#map").clientWidth/2,document.querySelector("#map").clientHeight/2)')
                    assert max(abs(a-b) for a,b in zip(before,after))<1e-6
                    assert not errors,(engine,orientation,errors)
                    # A modified source claim must fail before any image is displayed.
                    bad=browser.new_page(viewport={'width':w,'height':h},is_mobile=True,has_touch=True)
                    def tamper(route):
                        m=json.loads((SOURCE/'manifest.json').read_text())
                        m['productionApproved']=True
                        route.fulfill(json=m)
                    bad.route('**/qa/v153-geographic-strip/manifest.json',tamper)
                    bad.goto(url,wait_until='domcontentloaded',timeout=30000)
                    bad.wait_for_function('window.V154?.failure',timeout=15000)
                    assert bad.evaluate('!V154.ready && V154.failure.includes("cannot certify")')
                    bad.close()
                    results[f'{engine}-{orientation}']={'three_distinct_centers':True,
                        'zoom_anchor_preserved':True,'source_mode':mode,'physical_iPhone_approved':False}
                    page.close()
            finally:browser.close()
finally:server.shutdown()
assert len(results)==(2 if os.environ.get('V154_CHROMIUM_ONLY') else 4)
(OUT/'report.json').write_text(json.dumps({'results':results,'productionApproved':False,
    'gameOctagonCentersCertified':False,'historic1780Certified':False},indent=2)+'\n')
print(f'V154 PASS: {len(results)}/4 Chromium/WebKit phone layouts, {len(results)*3} distinct sector center views, {len(results)} anchored zoom checks ({mode} source); no game art approval')

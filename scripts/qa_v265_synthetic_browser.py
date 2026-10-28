#!/usr/bin/env python3
"""V265 four-browser FUNCTIONAL test using SYNTHETIC art only; never V203 approval."""
import hashlib,http.server,importlib.util,json,threading
from pathlib import Path
import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'qa/v265-synthetic-browser'
CONFIGS=(('chromium','portrait',390,844),('chromium','landscape',844,390),
         ('webkit','portrait',390,844),('webkit','landscape',844,390))
def load(name):
    spec=importlib.util.spec_from_file_location(name,ROOT/'scripts'/f'{name}.py')
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self,*a,**k):super().__init__(*a,directory=str(OUT),**k)
    def log_message(self,*a):pass

def run():
    OUT.mkdir(parents=True,exist_ok=True)
    v263=load('v263_offline_exact_art_playable');v265=load('v265_native_south_shadow_detail')
    y,x=np.mgrid[0:1024,0:1536]
    g=(40+20*np.sin(x/37)+15*np.cos(y/31)).clip(0,255).astype('uint8')
    w=OUT/'synthetic-west.png';s=OUT/'synthetic-south.png'
    Image.fromarray(np.stack([g,g,g],2)).save(w)
    Image.fromarray(np.stack([g,g//2,g//3],2)).save(s)
    pins={k:hashlib.sha256(p.read_bytes()).hexdigest() for k,p in [('west',w),('south',s)]}
    v263.PINS=pins;v265.ORIGINAL_WEST_SHA=pins['west']
    base=OUT/'v263-SYNTHETIC.html';out=OUT/'v265-SYNTHETIC.html'
    v263.build(ROOT,w,s,base)
    v265.build(base,s,OUT/'synthetic-south-recovered.png',out,expected_south=pins['south'])
    out.write_text(out.read_text().replace('V265 SOUTH SHADOW DETAIL RECOVERY - UNAPPROVED',
                                     'SYNTHETIC V265 FUNCTIONAL TEST - NOT REAL ART'))
    server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler)
    threading.Thread(target=server.serve_forever,daemon=True).start()
    report={'source':'SYNTHETIC_ONLY','originalArtTested':False,'strictV203Passed':False,
            'historicalGeographyVerified':False,'userVisualApproval':False,
            'productionApproved':False,'configs':{}}
    try:
        with sync_playwright() as pw:
            for engine,orient,width,height in CONFIGS:
                browser=getattr(pw,engine).launch(headless=True)
                page=browser.new_page(viewport={'width':width,'height':height},
                                      device_scale_factor=2,is_mobile=True,has_touch=True)
                errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
                try:
                    page.goto(f'http://127.0.0.1:{server.server_port}/{out.name}',wait_until='domcontentloaded',timeout=60000)
                    page.wait_for_function('window.V192?.v263ExactArtLoaded===true',timeout=180000)
                    assert page.evaluate('V192.connectedRoute && !V192.productionApproved')
                    assert page.evaluate("V192.orderTo('south')")
                    distances=[]
                    for f in (.2,.5,.8):
                        p=page.evaluate('(f)=>V192.progress(f)',f)
                        distances.append(page.evaluate('(p)=>V192.roadDistance(p)',p))
                    assert max(distances)<.001,distances
                    for tile in ('west','matrei','south'):
                        assert page.evaluate('(tile)=>V192.focusTile(tile)',tile)
                        page.evaluate('V192.zoomTo(6)')
                        assert page.evaluate('V192.snapshotForReview()')
                        page.screenshot(path=str(OUT/f'{engine}-{orient}-{tile}-SYNTHETIC.png'))
                    assert not errors,errors
                    report['configs'][f'{engine}-{orient}']={'screenshots':3,'maxGraphDeviation':max(distances),'pageErrors':errors}
                finally:page.close();browser.close()
    finally:server.shutdown()
    report['fourBrowserSyntheticFunctionalPass']=len(report['configs'])==4
    (OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
    assert report['fourBrowserSyntheticFunctionalPass']
if __name__=='__main__':run()

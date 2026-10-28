#!/usr/bin/env python3
"""V263 CI: real Chromium/WebKit gameplay with SYNTHETIC placeholder images.
Does not prove actual V258/V260 art, V203 detail, or human acceptance.
"""
import hashlib, http.server, importlib.util, json, tempfile, threading
from pathlib import Path
from PIL import Image
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('v263',ROOT/'scripts/v263_offline_exact_art_playable.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
CONFIGS=(('chromium','portrait',390,844),('chromium','landscape',844,390),
         ('webkit','portrait',390,844),('webkit','landscape',844,390))
OUT=ROOT/'qa/v263-synthetic-browser'
class Handler(http.server.SimpleHTTPRequestHandler):
 def __init__(self,*a,**k):super().__init__(*a,directory=str(OUT),**k)
 def log_message(self,*a):pass

def run():
 OUT.mkdir(parents=True,exist_ok=True)
 west=OUT/'synthetic-west.png';south=OUT/'synthetic-south.png'
 Image.new('RGB',(1536,1024),(52,83,64)).save(west)
 Image.new('RGB',(1536,1024),(101,82,57)).save(south)
 # Override only this ephemeral CI process, never the GitHub-pinned source hashes.
 mod.PINS={tile:hashlib.sha256(p.read_bytes()).hexdigest() for tile,p in [('west',west),('south',south)]}
 candidate=OUT/'synthetic-test-only.html'
 mod.build(ROOT,west,south,candidate)
 html=candidate.read_text().replace('V263 OFFLINE EXACT-ART PLAYABLE CANDIDATE',
   'SYNTHETIC CI FIXTURE - NOT ACTUAL V263 ART')
 candidate.write_text(html)
 server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler)
 threading.Thread(target=server.serve_forever,daemon=True).start()
 report={'version':263,'source':'SYNTHETIC_ONLY','actualOriginalArtTested':False,
  'historicalGeographyVerified':False,'strictV203Passed':False,
  'userApproved':False,'productionApproved':False,'configs':{}}
 try:
  with sync_playwright() as pw:
   for engine,orientation,w,h in CONFIGS:
    key=engine+'-'+orientation
    browser=getattr(pw,engine).launch(headless=True)
    page=browser.new_page(viewport={'width':w,'height':h},device_scale_factor=2,
      is_mobile=True,has_touch=True)
    errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    try:
     page.goto(f'http://127.0.0.1:{server.server_port}/{candidate.name}',
       wait_until='domcontentloaded',timeout=60000)
     page.wait_for_function('window.V192?.v263ExactArtLoaded===true',timeout=180000)
     assert page.evaluate('V192.ready')
     assert page.evaluate('V192.connectedRoute')
     assert not page.evaluate('V192.rawArtReview')
     assert not page.evaluate('V192.productionApproved')
     assert page.evaluate("V192.orderTo('south')")
     errors_route=[]
     for f in (.2,.5,.8):
      point=page.evaluate('(f)=>V192.progress(f)',f)
      errors_route.append(page.evaluate('(p)=>V192.roadDistance(p)',point))
     assert max(errors_route)<.001,errors_route
     for tile in ('west','matrei','south'):
      assert page.evaluate('(t)=>V192.focusTile(t)',tile)
      page.evaluate('V192.zoomTo(6)')
      assert page.evaluate('V192.snapshotForReview()')
      page.screenshot(path=str(OUT/f'{key}-{tile}-SYNTHETIC.png'))
     assert not errors,errors
     report['configs'][key]={'source':'SYNTHETIC_ONLY','screenshots':3,
       'V123MovementPass':True,'maxGraphDeviation':max(errors_route),'pageErrors':errors}
    finally:page.close();browser.close()
 finally:server.shutdown()
 report['fourBrowserFunctionalPass']=len(report['configs'])==4
 (OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps(report,indent=2))
 assert report['fourBrowserFunctionalPass']
if __name__=='__main__':run()

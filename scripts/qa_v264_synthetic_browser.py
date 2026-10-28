#!/usr/bin/env python3
"""Four-browser V264 smoke tests with SYNTHETIC pixels, never original-art approval."""
import hashlib,http.server,importlib.util,json,threading
from pathlib import Path
from PIL import Image
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
def load(name):
 p=ROOT/'scripts'/f'{name}.py'
 spec=importlib.util.spec_from_file_location(name,p)
 m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
v263=load('v263_offline_exact_art_playable')
v264=load('v264_photo_edge_continuity')
CONFIGS=(('chromium','portrait',390,844),('chromium','landscape',844,390),
         ('webkit','portrait',390,844),('webkit','landscape',844,390))
OUT=ROOT/'qa/v264-synthetic-browser'
class Handler(http.server.SimpleHTTPRequestHandler):
 def __init__(self,*a,**k):super().__init__(*a,directory=str(OUT),**k)
 def log_message(self,*a):pass

def run():
 OUT.mkdir(parents=True,exist_ok=True)
 w=OUT/'synthetic-west.png';s=OUT/'synthetic-south.png'
 Image.new('RGB',(1536,1024),(52,83,64)).save(w)
 Image.new('RGB',(1536,1024),(101,82,57)).save(s)
 pins={k:hashlib.sha256(p.read_bytes()).hexdigest() for k,p in [('west',w),('south',s)]}
 # Override only ephemeral CI process. GitHub-pinned hashes remain unchanged.
 v263.PINS=pins;v264.EXPECTED=pins
 base=OUT/'v263-SYNTHETIC.html';candidate=OUT/'v264-SYNTHETIC.html'
 v263.build(ROOT,w,s,base);v264.build(base,w,s,candidate)
 candidate.write_text(candidate.read_text().replace(
  'V264 PHOTO-SEAM EXPERIMENT','SYNTHETIC V264 CI - NOT REAL ART'))
 server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler)
 threading.Thread(target=server.serve_forever,daemon=True).start()
 report={'version':264,'source':'SYNTHETIC_ONLY','originalArtTested':False,
         'strictV203Passed':False,'physicalIPhoneApproved':False,
         'userVisualApproval':False,'productionApproved':False,'configs':{}}
 try:
  with sync_playwright() as pw:
   for engine,orientation,width,height in CONFIGS:
    key=f'{engine}-{orientation}'
    browser=getattr(pw,engine).launch(headless=True)
    page=browser.new_page(viewport={'width':width,'height':height},
      device_scale_factor=2,is_mobile=True,has_touch=True)
    errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    try:
     page.goto(f'http://127.0.0.1:{server.server_port}/{candidate.name}',
       wait_until='domcontentloaded',timeout=60000)
     page.wait_for_function('window.V192?.v263ExactArtLoaded===true',timeout=180000)
     assert page.evaluate('V264_SEAM_UNDERLAY.complete && V264_SEAM_UNDERLAY.naturalWidth===1536')
     assert page.evaluate('V192.connectedRoute && V192.ready && !V192.productionApproved')
     assert page.evaluate("V192.orderTo('south')")
     distances=[]
     for f in (.2,.5,.8):
      point=page.evaluate('(f)=>V192.progress(f)',f)
      distances.append(page.evaluate('(p)=>V192.roadDistance(p)',point))
     assert max(distances)<.001,distances
     for tile in ('west','matrei','south'):
      assert page.evaluate('(t)=>V192.focusTile(t)',tile)
      page.evaluate('V192.zoomTo(6)')
      assert page.evaluate('V192.snapshotForReview()')
      page.screenshot(path=str(OUT/f'{key}-{tile}-SYNTHETIC.png'))
     assert not errors,errors
     report['configs'][key]={'source':'SYNTHETIC_ONLY','screenshots':3,
       'v264UnderlayLoaded':True,'V123MovementPass':True,
       'maxGraphDeviation':max(distances),'pageErrors':errors}
    finally:page.close();browser.close()
 finally:server.shutdown()
 report['fourBrowserFunctionalPass']=len(report['configs'])==4
 (OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps(report,indent=2))
 assert report['fourBrowserFunctionalPass']
if __name__=='__main__':run()

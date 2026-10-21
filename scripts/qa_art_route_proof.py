import http.server,threading,socketserver,json
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
out=ROOT/'terrain-puzzle'/'art-route-style-qa'
out.mkdir(parents=True,exist_ok=True)
class H(http.server.SimpleHTTPRequestHandler):
 def __init__(self,*a,**kw): super().__init__(*a,directory=str(ROOT),**kw)
 def log_message(self,*a):pass
class S(socketserver.TCPServer):allow_reuse_address=True
s=S(('127.0.0.1',0),H);threading.Thread(target=s.serve_forever,daemon=True).start()
url=f'http://127.0.0.1:{s.server_address[1]}/v108-art-route-proof.html'
checks={}
try:
 with sync_playwright() as p:
  for name in ('chromium','webkit'):
   b=getattr(p,name).launch(headless=True)
   try:
    pg=b.new_page(viewport={'width':390,'height':844},device_scale_factor=2,is_mobile=True,has_touch=True)
    errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto(url,wait_until='domcontentloaded');pg.wait_for_function('window.centuryArtDemo?.loaded===true',timeout=30000)
    chk={}
    chk['loaded']=pg.evaluate('window.centuryArtDemo.loaded')
    chk['routeNodes']=pg.evaluate('window.centuryArtDemo.routePoints===24')
    chk['notGeoreferenced']=pg.evaluate("window.centuryArtDemo.geographicAccuracy==='UNVERIFIED_STYLE_PROOF'")
    chk['initiallyHidden']=pg.evaluate('window.centuryArtDemo.debug===false')
    chk['portraitFits']=pg.evaluate('document.documentElement.scrollWidth<=innerWidth+1 && document.documentElement.scrollHeight<=innerHeight+1')
    pg.screenshot(path=str(out/(name+'-portrait-clean.png')))
    pg.locator('#debug').click();chk['dotsShow']=pg.evaluate('window.centuryArtDemo.debug===true')
    pg.screenshot(path=str(out/(name+'-portrait-dots.png')))
    pg.locator('#march').click();pg.wait_for_timeout(650)
    chk['moving']=pg.evaluate('window.centuryArtDemo.progress>0')
    pg.screenshot(path=str(out/(name+'-portrait-march.png')))
    pg.locator('#stop').click();chk['stopped']=pg.evaluate('window.centuryArtDemo.moving===false')
    pg.set_viewport_size({'width':844,'height':390});pg.wait_for_timeout(300)
    chk['landscapeFits']=pg.evaluate('document.documentElement.scrollWidth<=innerWidth+1 && document.documentElement.scrollHeight<=innerHeight+1')
    pg.screenshot(path=str(out/(name+'-landscape.png')))
    chk['noErrors']=not errs
    checks[name]={'checks':chk,'errors':errs,'passed':all(chk.values())}
   except Exception as exc:checks[name]={'passed':False,'error':str(exc)}
   finally:b.close()
finally:s.shutdown()
result={'passed':all(v.get('passed') for v in checks.values()),'browsers':checks,'physical_iPhone_tested':False}
(out/'qa.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
if not result['passed']:raise SystemExit(1)

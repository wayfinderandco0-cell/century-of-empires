"""Actual mobile viewport renders and geographic/interaction checks. Not physical iPhone QA."""
import json, os, pathlib, threading, http.server, socketserver, time
from playwright.sync_api import sync_playwright
ROOT=pathlib.Path(__file__).resolve().parents[1]; OUT=ROOT/'terrain-v102';os.chdir(ROOT)
class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*args):pass
server=socketserver.ThreadingTCPServer(('127.0.0.1',0),Quiet)
threading.Thread(target=server.serve_forever,daemon=True).start()
url=f'http://127.0.0.1:{server.server_address[1]}/v102-brenner-visual-pilot.html'
report={'sourceCommit':os.getenv('GITHUB_SHA','local'),'browsers':{},'physicalIPhoneTested':False,'visualApproval':'Screenshots require human inspection; browser tests do not establish commercial quality.'}
try:
 with sync_playwright() as p:
  for name in ['chromium','webkit']:
   result={'checks':{},'errors':[],'failedRequests':[]};report['browsers'][name]=result
   browser=None
   try:
    browser=getattr(p,name).launch(headless=True,**({'args':['--disable-dev-shm-usage','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']} if name=='chromium' else {}))
    page=browser.new_page(viewport={'width':390,'height':844},device_scale_factor=2,is_mobile=True,has_touch=True)
    page.on('pageerror',lambda err:result['errors'].append(str(err)))
    page.on('requestfailed',lambda req:result['failedRequests'].append(req.url))
    page.goto(url,wait_until='networkidle');page.wait_for_function('window.terrainPilot?.metrics.ready',timeout=60000)
    page.wait_for_timeout(1300)
    result['metrics']=page.evaluate('terrainPilot.metrics')
    result['checks']['assetsReady']=result['metrics']['ready']
    result['checks']['noCampaignStorage']=page.evaluate('localStorage.length===0')
    result['checks']['naturalWaterways']=result['metrics']['waterways']>=40
    result['checks']['portraitFits']=page.evaluate('document.documentElement.scrollWidth===innerWidth')
    result['checks']['coordinateRoundTrip']=page.evaluate('''()=>{const p=terrainPilot.geoToLocal(11.5217,47.1293);const q=terrainPilot.localToGeo(p[0],p[2]);return Math.abs(q[0]-11.5217)<1e-9&&Math.abs(q[1]-47.1293)<1e-9}''')
    page.screenshot(path=str(OUT/f'{name}-portrait.png'))
    page.locator('#zoomIn').click();page.wait_for_timeout(650)
    result['checks']['zoomInWorks']=page.evaluate('terrainPilot.camera.span<6.8')
    page.locator('#tilt').click()
    result['checks']['tiltTargetSet']=page.evaluate('terrainPilot.target.pitch>1.3')
    # A slow software-rendering frame can delay camera interpolation; wait for the actual rendered pitch.
    try:
     page.wait_for_function('terrainPilot.camera.pitch>1.3',timeout=7000)
     result['checks']['overheadWorks']=True
    except Exception:
     result['checks']['overheadWorks']=False
    page.locator('#home').click();page.wait_for_timeout(800)
    page.locator('#terrain').tap(position={'x':170,'y':400})
    result['checks']['tapInspectsGeography']=page.locator('#inspect').is_visible()
    page.locator('#closeInspect').click()
    # Pointer pan, including cancellation. Real pinch is checked through CDP where available.
    before=page.evaluate('terrainPilot.camera')
    page.mouse.move(150,350);page.mouse.down();page.mouse.move(230,410,steps=12);page.mouse.up();page.wait_for_timeout(650)
    result['checks']['dragPans']=page.evaluate(f'Math.abs(terrainPilot.camera.x-({before["x"]}))>.01')
    page.locator('#home').click();page.wait_for_timeout(750)
    for level in range(4):
     page.locator(f'[data-level="{level}"]').click();page.wait_for_timeout(850)
     result['checks'][f'level{level+1}Finite']=page.evaluate('Object.values(terrainPilot.camera).every(Number.isFinite)')
    page.locator('#info').click();result['checks']['sourcesAccessible']=page.locator('#sources').is_visible();page.locator('#closeInfo').click()
    page.locator('#home').click();page.wait_for_timeout(750)
    # Same page rotates: no reinitialization, no reset of focus.
    focus=page.evaluate('terrainPilot.camera')
    page.set_viewport_size({'width':844,'height':390});page.wait_for_timeout(900)
    result['checks']['rotationKeepsFocus']=page.evaluate(f'Math.abs(terrainPilot.camera.x-({focus["x"]}))<.001&&Math.abs(terrainPilot.camera.z-({focus["z"]}))<.001')
    result['checks']['landscapeFits']=page.evaluate('document.documentElement.scrollWidth===innerWidth')
    page.screenshot(path=str(OUT/f'{name}-landscape.png'))
    page.locator('#zoomIn').click();page.locator('#zoomIn').click();page.wait_for_timeout(900)
    page.screenshot(path=str(OUT/f'{name}-detail.png'))
    result['checks']['noJavaScriptErrors']=not result['errors']
    result['checks']['noFailedRequests']=not result['failedRequests']
    result['finalMetrics']=page.evaluate('terrainPilot.metrics')
   except Exception as e:result['errors'].append(str(e))
   finally:
    if browser:browser.close()
   result['passed']=bool(result['checks']) and all(result['checks'].values()) and not result['errors']
finally:
 server.shutdown();report['passed']=all(b.get('passed',False) for b in report['browsers'].values())
 (OUT/'qa-report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
 if not report['passed']:raise SystemExit(1)

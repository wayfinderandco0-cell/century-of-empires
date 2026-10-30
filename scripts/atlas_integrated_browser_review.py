#!/usr/bin/env python3
"""Real local-server browser screenshots of the integrated (not iframe) Alpine canvas.
This is browser-emulated iPhone WebKit, NOT a physical iPhone Safari assertion.
"""
import argparse,json,subprocess,sys,time,urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright

ap=argparse.ArgumentParser()
ap.add_argument("--browser",choices=["webkit","chromium"],required=True)
ap.add_argument("--orientation",choices=["portrait","landscape"],required=True)
ap.add_argument("--out",required=True)
args=ap.parse_args()
root=Path(__file__).resolve().parent.parent
out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
w,h=(390,844) if args.orientation=="portrait" else (844,390)
server=subprocess.Popen([sys.executable,"-m","http.server","8769","--bind","127.0.0.1"],cwd=root,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
errors=[]
try:
 for i in range(60):
  try:
   urllib.request.urlopen("http://127.0.0.1:8769/index.html",timeout=1).close()
   break
  except Exception:time.sleep(.1)
 else:raise RuntimeError("Local server failed")
 with sync_playwright() as pw:
  browser=getattr(pw,args.browser).launch(headless=True)
  context=browser.new_context(viewport={"width":w,"height":h},device_scale_factor=2,is_mobile=True,has_touch=True)
  page=context.new_page();page.on("pageerror",lambda e:errors.append(str(e)))
  page.goto("http://127.0.0.1:8769/index.html?photoBlock=carpathians",wait_until="domcontentloaded",timeout=60000)
  page.wait_for_function("window.COEAtlas && (COEAtlas.loaded || window.COEAtlasLoadError)",timeout=60000)
  assert not page.evaluate("window.COEAtlasLoadError"),page.evaluate("window.COEAtlasLoadError")
  before=page.evaluate("""() => ({
    storage:JSON.stringify(localStorage), clock:document.getElementById('clockTitle')?.textContent,
    nodes:COEAtlas.nodes,unique:COEAtlas.uniqueWorldNodes,seams:COEAtlas.seams,
    images:COEAtlas.imageSizes,route:COEAtlas.routeTo([2806,1629])
  })""")
  assert before["nodes"]==100 and before["unique"]==98,before
  assert len(before["seams"])==2 and all(s["pass"] and s["endpointGapPx"]==0 for s in before["seams"])
  assert all(size==[1536,1024] for size in before["images"].values()),before["images"]
  assert len(before["route"])>35 and [1536,478] in before["route"] and [2002,1024] in before["route"]
  page.locator("#atlasIntegratedOpen").click()
  assert page.locator("#atlasIntegratedLayer").is_visible()
  assert page.locator("#atlasIntegratedLayer iframe").count()==0,"This must be a native canvas, not iframe"
  page.locator("#atlasWhole").click()
  page.wait_for_timeout(250)
  page.screenshot(path=str(out/f"{args.browser}-{args.orientation}-whole.png"))
  page.locator("#atlasWest").click()
  page.wait_for_timeout(200)
  page.screenshot(path=str(out/f"{args.browser}-{args.orientation}-west.png"))
  point=page.evaluate("COEAtlas.screenFor([1536,478])")
  assert 0<=point[0]<=w and 0<=point[1]<=h,point
  page.touchscreen.tap(*point)
  assert page.evaluate("COEAtlas.moving"),"Touching the WEST/MATREI physical cartway must issue a route"
  page.locator("#atlasHalt").click()
  assert not page.evaluate("COEAtlas.moving")
  page.locator("#atlasMarch").click()
  route=page.evaluate("COEAtlas.route")
  assert len(route)>35 and [1536,478] in route and [2002,1024] in route,route
  arrived=page.evaluate("COEAtlas.finishMarch()")
  assert arrived==[2806,1629],arrived
  page.locator("#atlasSouth").click()
  page.wait_for_timeout(200)
  page.screenshot(path=str(out/f"{args.browser}-{args.orientation}-south.png"))
  z=page.evaluate("COEAtlas.zoom")
  page.locator("#atlasPlus").click()
  assert page.evaluate("COEAtlas.zoom")>z
  page.locator("#atlasMinus").click()
  # The same native canvas must fit the full eight-photo source block on a
  # 390px-wide phone. These remain source studies, not gameplay routes.
  page.locator("#atlasPhotoSources").click()
  page.wait_for_function("COEAtlas.photoMode && COEAtlas.photoCells===8",timeout=45000)
  assert page.locator("#atlasMarch").is_hidden(),"Photo-only cells must not expose army orders"
  assert page.locator("#atlasRoads").is_hidden(),"No unverified road trace may be presented as playable"
  page.locator("#atlasWhole").click()
  page.wait_for_function("COEAtlas.photoLoaded===8",timeout=60000)
  corners=page.evaluate("""() => ({
    a:COEAtlas.screenFor([10*1536,12*1024]),
    b:COEAtlas.screenFor([14*1536,14*1024]),
    zoom:COEAtlas.zoom
  })""")
  assert 0<=corners["a"][0] and corners["b"][0]<=w,corners
  assert 0<=corners["a"][1] and corners["b"][1]<=h,corners
  assert corners["zoom"]>=.15,corners
  page.wait_for_timeout(400)
  page.screenshot(path=str(out/f"{args.browser}-{args.orientation}-eight-photo-whole.png"))
  assert not page.evaluate("COEAtlas.tapWorld([10*1536+768,12*1024+512])"),"Unverified photo tile must not issue an army order"
  page.locator("#atlasPhotoSources").click()
  assert not page.evaluate("COEAtlas.photoMode")
  assert page.locator("#atlasMarch").is_visible(),"Original V123 controls must return"
  page.locator("#atlasClose").click()
  assert page.locator("#atlasIntegratedLayer").is_hidden()
  after=page.evaluate("""() => ({
    storage:JSON.stringify(localStorage),clock:document.getElementById('clockTitle')?.textContent,
    startOverlay:document.getElementById('startOverlay')?.hidden,
    iframe:document.getElementById('alpineArtFrame')?.getAttribute('src')
  })""")
  assert after["storage"]==before["storage"],"V94 save data mutated by art integration"
  assert after["clock"]==before["clock"],"V94 clock UI changed"
  assert after["iframe"] is None,"Legacy preview should not be activated"
  assert not errors,errors
  report={"browser":args.browser,"orientation":args.orientation,"viewport":[w,h],
          "nativeCanvas":True,"images":before["images"],"nodes":before["nodes"],
          "uniqueWorldNodes":before["unique"],"seams":before["seams"],
          "routePoints":len(route),"touchToMarch":True,"halt":True,"arrival":arrived,
          "zoom":True,"photoEightCellWholeVisible":True,"photoLoaded":8,"photoGameplayBlocked":True,"campaignStorageUnchanged":True,"pageErrors":errors}
  (out/f"{args.browser}-{args.orientation}.json").write_text(json.dumps(report,indent=2))
  print(json.dumps(report,indent=2))
  context.close();browser.close()
finally:
 server.terminate()
 try:server.wait(timeout=5)
 except subprocess.TimeoutExpired:server.kill()

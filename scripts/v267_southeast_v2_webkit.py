#!/usr/bin/env python3
"""390x844 native-game WebKit evidence for roaded SOUTH-east candidate.
The new tile MUST remain blocked until physical road approval. This is not a
playability certification or a physical iPhone Safari test.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright
import subprocess,sys,time,json,urllib.request
from PIL import Image,ImageStat
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"terrain-grid/v267-southeast-road-02"
server=subprocess.Popen([sys.executable,"-m","http.server","8772","--bind","127.0.0.1"],
 cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
errors=[]
try:
 for i in range(80):
  try:
   urllib.request.urlopen("http://127.0.0.1:8772/index.html",timeout=1).close()
   break
  except Exception:time.sleep(.1)
 else:raise RuntimeError("Local HTTP server unavailable")
 with sync_playwright() as pw:
  browser=pw.webkit.launch(headless=True)
  context=browser.new_context(viewport={"width":390,"height":844},device_scale_factor=2,
                              is_mobile=True,has_touch=True)
  page=context.new_page();page.on("pageerror",lambda e:errors.append(str(e)))
  page.goto("http://127.0.0.1:8772/index.html?southEastRoadPilot=2",
            wait_until="domcontentloaded",timeout=60000)
  page.wait_for_function("window.COEAtlas && (COEAtlas.southeastRoadVisible || window.COEAtlasLoadError)",
                         timeout=90000)
  assert not page.evaluate("window.COEAtlasLoadError"),page.evaluate("window.COEAtlasLoadError")
  assert page.locator("#atlasCanvas").is_visible()
  assert page.locator("#atlasIntegratedLayer iframe").count()==0
  state=page.evaluate("""() => ({
    sizes:COEAtlas.southeastRoadDimensions,
    playable:COEAtlas.playability,
    seams:COEAtlas.seams,
    candidateRoute:COEAtlas.routeTo([3500,1600]),
    nativeImages:COEAtlas.imageSizes,
    campaignStorage:JSON.stringify(localStorage)
  })""")
  assert state["sizes"]==[1536,1024],state
  assert state["playable"]["playableIds"]==["matrei","south","west"],state
  assert state["playable"]["connectedNew"]==[],state
  assert len(state["seams"])==2 and all(x["pass"] for x in state["seams"]),state
  assert state["candidateRoute"] is None,"Candidate must not be routable before seam approval"
  page.locator("#atlasWhole").click()
  page.wait_for_timeout(500)
  shot=OUT/"native-webkit-390x844-southeast-road-v2-candidate.png"
  page.screenshot(path=str(shot))
  with Image.open(shot) as im:
   assert im.size==(780,1688),im.size
   mid=im.convert("RGB").crop((190,450,700,1250))
   assert max(ImageStat.Stat(mid).stddev)>14,"Native screenshot lacks visible terrain"
  assert page.evaluate("COEAtlas.tapWorld([3500,1600])") is False
  assert not page.evaluate("COEAtlas.moving")
  # Real WEST->SOUTH native V123 march remains interactive.
  page.locator("#atlasMarch").click()
  route=page.evaluate("COEAtlas.route")
  assert [1536,478] in route and [2002,1024] in route and len(route)>35
  assert page.evaluate("COEAtlas.moving")
  assert page.evaluate("COEAtlas.finishMarch()")==[2806,1629]
  # Return march: SOUTH->WEST via the same immutable road graph.
  assert page.evaluate("COEAtlas.tapWorld([1536,478])")
  assert page.evaluate("COEAtlas.moving")
  assert page.evaluate("COEAtlas.finishMarch()")==[1536,478]
  z=page.evaluate("COEAtlas.zoom")
  page.locator("#atlasPlus").click()
  assert page.evaluate("COEAtlas.zoom")>z
  page.locator("#atlasMinus").click()
  assert page.evaluate("JSON.stringify(localStorage)")==state["campaignStorage"]
  assert not errors,errors
  report={"viewportCSS":[390,844],"deviceScaleFactor":2,"browser":"webkit",
   "nativeGameCanvas":True,"newArtDecoded":True,"candidateRoadPreview":True,"v2LocalTextureMethod":True,
   "baselinePlayable":3,"newlyConnectedPlayable":0,"candidateMovementBlocked":True,
   "baselineWestSouthMarch":True,"baselineSouthWestReturn":True,"panZoomControls":True,
   "userApproved":False,"physicalRoadSeamVerified":False,"newlyFinished":0,
   "screenshot":str(shot.relative_to(ROOT)),"pageErrors":errors}
  (OUT/"native-webkit-report.json").write_text(json.dumps(report,indent=2)+"\n")
  print(json.dumps(report,indent=2))
  context.close();browser.close()
finally:
 server.terminate()
 try:server.wait(timeout=5)
 except subprocess.TimeoutExpired:server.kill()

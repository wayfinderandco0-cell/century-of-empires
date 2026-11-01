#!/usr/bin/env python3
"""Real 390x844 WebKit visual gate for opt-in color-only V267 ridge seam grade.

No fake road, no new playable cell, no approval. Screenshot is pixel-tested,
not inferred from HTML success. Baseline V123 graph/movement is checked after exit.
"""
from pathlib import Path
from PIL import Image,ImageStat
from playwright.sync_api import sync_playwright
import subprocess,time,json,hashlib
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'terrain-grid/v267-original-art-batch-01'
ASSET=OUT/'matrei-east-ridge-graded.webp'
METRICS=OUT/'matrei-east-grade-metrics.json'
def main():
 metrics=json.loads(METRICS.read_text())
 assert hashlib.sha256(ASSET.read_bytes()).hexdigest()==metrics['assetSha256']
 assert metrics['afterMeanRGBDiff'] < metrics['beforeMeanRGBDiff']
 assert not any(metrics[k] for k in ('treesWarped','roadsAdded','sourcePixelsCopied','geometricSeamVerified','roadSeamVerified','finished'))
 server=subprocess.Popen(['python','-m','http.server','8765','--bind','127.0.0.1'],cwd=ROOT,
                         stdout=subprocess.DEVNULL,stderr=subprocess.STDOUT)
 try:
  time.sleep(1.2)
  with sync_playwright() as pw:
   browser=pw.webkit.launch(headless=True)
   page=browser.new_page(viewport={'width':390,'height':844},
                        device_scale_factor=2,is_mobile=True,has_touch=True)
   errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
   page.goto('http://127.0.0.1:8765/index.html?originalArtPilot=v267-new&ridgeGrade=1&autoOpen=1',
             wait_until='domcontentloaded')
   page.wait_for_function('window.COEAtlas && COEAtlas.loaded && COEAtlas.shown && COEAtlas.originalNeighborVisible && COEAtlas.originalNeighborCells===1',timeout=90000)
   page.wait_for_function("document.getElementById('atlasRidgeDomFallback').naturalWidth===1536",timeout=30000)
   assert page.evaluate('COEAtlas.approvedBaselineLocked') is True
   assert page.evaluate('COEAtlas.nodes')==100
   assert page.evaluate('COEAtlas.startMarch()') is False
   assert page.evaluate("document.getElementById('atlasRidgeDomFallback').src.includes('matrei-east-ridge-graded.webp')")
   # The direct-link camera may leave only a sliver of the ridge visible.
   # The old smoke test cropped its *offscreen* center; Pillow pads such
   # out-of-bounds crops with black, producing a false "blank ridge" failure.
   # Center the actual source tile before checking rendered viewport pixels.
   page.evaluate('COEAtlas.centerAt(3840,512,2.2)')
   page.wait_for_function("""() => {
     const el=document.getElementById('atlasRidgeDomFallback');
     const r=el.getBoundingClientRect();
     return el.complete && el.naturalWidth===1536 && r.width>180 && r.height>100 &&
       r.left<innerWidth*.3 && r.right>innerWidth*.7 &&
       r.top<innerHeight*.35 && r.bottom>innerHeight*.65;
   }""",timeout=30000)
   page.evaluate("() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))")
   page.wait_for_timeout(400)
   shot=OUT/'actual-webkit-iphone-ridge-graded.png'
   page.screenshot(path=str(shot))
   rect=page.evaluate("""() => {
     const r=document.getElementById('atlasRidgeDomFallback').getBoundingClientRect();
     return {left:r.left,top:r.top,width:r.width,height:r.height};
   }""")
   with Image.open(shot) as im:
    # Clamp BOTH endpoints to the real screenshot bounds. Never allow Pillow
    # to fabricate black pixels for a crop outside the mobile viewport.
    x0=max(0,min(im.width,int((rect['left']+rect['width']*.30)*2)))
    x1=max(0,min(im.width,int((rect['left']+rect['width']*.70)*2)))
    y0=max(0,min(im.height,int((rect['top']+rect['height']*.30)*2)))
    y1=max(0,min(im.height,int((rect['top']+rect['height']*.70)*2)))
    assert x1-x0>80 and y1-y0>80,('ridge center not on screen',rect,(x0,y0,x1,y1))
    crop=im.convert('RGB').crop((x0,y0,x1,y1))
    st=ImageStat.Stat(crop)
    assert max(st.stddev)>20,('blank ridge',crop.size,st.stddev)
    assert len(crop.getcolors(crop.width*crop.height) or [])>1200,'insufficient image detail'
   width0=rect['width']
   page.locator('#atlasPlus').click()
   page.wait_for_timeout(120)
   width1=page.evaluate("document.getElementById('atlasRidgeDomFallback').getBoundingClientRect().width")
   assert width1>width0*1.15,('zoom failed',width0,width1)
   page.locator('#atlasMinus').click()
   page.locator('#atlasOriginalNeighbors').click()
   assert page.evaluate('COEAtlas.originalNeighborVisible') is False
   assert page.evaluate('COEAtlas.startMarch()') is True
   assert not errors,errors
   print(json.dumps({'status':'PASS','screenshot':str(shot.relative_to(ROOT)),
     'ridgePixels':'nonblank','zoom':'PASS','V123ArmyMarch':'PASS',
     'gradedBorderRGBBefore':metrics['beforeMeanRGBDiff'],
     'gradedBorderRGBAfter':metrics['afterMeanRGBDiff'],
     'terrainSeamVerified':False,'newPlayable':0}))
   browser.close()
 finally:
  server.terminate();server.wait(timeout=5)
if __name__=='__main__':main()

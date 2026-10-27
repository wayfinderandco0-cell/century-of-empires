#!/usr/bin/env python3
"""V236 actual four-browser isolated authored Alpine art and movement screenshot QA.
Art is explicitly unapproved; V203 numeric gate and human review run separately.
"""
import http.server, json, threading
from pathlib import Path
from PIL import Image, ImageChops, ImageDraw
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'qa/v236-authored-alpine'
ENGINES=('chromium','webkit')
ORIENTATIONS=(('portrait',390,844),('landscape',844,390))
REGIONS=('west','matrei','south')
class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self,*a,**k):super().__init__(*a,directory=str(ROOT),**k)
    def log_message(self,*a):pass

def capture(page,region,target):
    assert page.evaluate('(id)=>V192.focusTile(id)',region)
    page.evaluate('V192.zoomTo(6)')
    assert page.evaluate('V192.snapshotForReview()')
    target.parent.mkdir(parents=True,exist_ok=True)
    page.screenshot(path=str(target),animations='disabled')
    return page.evaluate('V192.terrainCamera')

def same_matrei_region(a,b):
    with Image.open(a) as one,Image.open(b) as two:
        assert one.size==two.size
        w,h=one.size
        box=(int(w*.30),int(h*.28),int(w*.70),int(h*.68))
        return ImageChops.difference(one.crop(box),two.crop(box)).getbbox() is None

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler)
    threading.Thread(target=server.serve_forever,daemon=True).start()
    base=f'http://127.0.0.1:{server.server_port}/'
    report={'version':236,'technicalPassed':False,'productionApproved':False,
            'sourceRegisteredToV123':False,'historicRoadsVerified':False,
            'physicalIPhoneApproved':False,'humanVisualApproval':False,
            'configurations':{}}
    try:
        with sync_playwright() as pw:
            for engine in ENGINES:
                browser=getattr(pw,engine).launch(headless=True)
                try:
                    for orientation,w,h in ORIENTATIONS:
                        key=f'{engine}-{orientation}'
                        page=browser.new_page(viewport={'width':w,'height':h},
                                              is_mobile=True,has_touch=True,device_scale_factor=2)
                        baseline=browser.new_page(viewport={'width':w,'height':h},
                                                  is_mobile=True,has_touch=True,device_scale_factor=2)
                        errors=[]
                        page.on('pageerror',lambda e:errors.append(str(e)))
                        try:
                            page.goto(base+'v236-authored-alpine-playtest.html?reviewCapture=1',
                                      wait_until='domcontentloaded',timeout=30000)
                            page.wait_for_function('window.V192?.ready===true',timeout=180000)
                            m=page.evaluate('V192.v236Study')
                            assert m['version']==236 and m['productionApproved'] is False
                            assert m['kind']=='FICTIONAL_AUTHORED_ALPINE_STUDY'
                            assert m['sourceRegisteredToV123'] is False
                            assert m['gameArtApproved'] is False
                            nodes=page.evaluate('V192.roadNodeCount')
                            destinations=page.evaluate('V192.destinations()')
                            cams={}
                            for region in REGIONS:
                                cams[region]=capture(page,region,OUT/f'{key}-{region}-close.png')
                            baseline.goto(base+'v227-original-artwork-import-study.html?reviewCapture=1',
                                          wait_until='domcontentloaded',timeout=30000)
                            baseline.wait_for_function('window.V192?.ready===true',timeout=180000)
                            old_camera=capture(baseline,'matrei',OUT/f'{key}-matrei-original.png')
                            assert cams['matrei']==old_camera,('camera mismatch',key)
                            assert same_matrei_region(OUT/f'{key}-matrei-close.png',
                                                      OUT/f'{key}-matrei-original.png'),('Matrei changed',key)
                            assert page.evaluate('V192.roadNodeCount')==nodes
                            assert page.evaluate('V192.destinations()')==destinations
                            assert page.evaluate('V192.orderTo("south")') is True
                            for fraction in (.2,.5,.8):
                                p=page.evaluate('(f)=>V192.progress(f)',fraction)
                                assert page.evaluate('(p)=>V192.roadDistance(p)',p)<.001
                            assert not errors,(key,errors)
                            report['configurations'][key]={
                                'twoDistinctFictionalCompositionsRendered':True,
                                'sameMatreiCameraAndPixels':True,
                                'originalV123GraphAndArmyMovement':True,
                                'allHistoricalAndApprovalFlagsFalse':True}
                        finally:
                            baseline.close();page.close()
                finally:browser.close()
    finally:server.shutdown()
    sources=[OUT/f'webkit-portrait-{r}-close.png' for r in REGIONS]
    if all(p.exists() for p in sources):
        contact=Image.new('RGB',(1170,680),'#19271f')
        d=ImageDraw.Draw(contact)
        for i,(name,p) in enumerate(zip(REGIONS,sources)):
            with Image.open(p) as im:
                contact.paste(im.convert('RGB').resize((390,650),Image.Resampling.LANCZOS),(i*390,30))
            d.text((i*390+8,7),name.upper()+' / V236 FICTIONAL ART NOT APPROVED',fill='white')
        contact.save(OUT/'actual-webkit-three-authored-art.jpg',quality=82)
    report['technicalPassed']=len(report['configurations'])==4
    (OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
    assert report['technicalPassed']
if __name__=='__main__':main()

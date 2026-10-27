#!/usr/bin/env python3
"""V227 opt-in local art ingestion: actual 4-browser regression, NOT visual approval.
The two synthetic PNGs exist ONLY as test fixtures, never committed as game art.
"""
import http.server
import json
import threading
from pathlib import Path
from PIL import Image, ImageChops, ImageDraw
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'qa/v227-art-ingest'
ENGINES=('chromium','webkit')
ORIENTATIONS=(('portrait',390,844),('landscape',844,390))

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self,*a,**k):super().__init__(*a,directory=str(ROOT),**k)
    def log_message(self,*a):pass

def difference(a,b):
    with Image.open(a) as one,Image.open(b) as two:
        diff=ImageChops.difference(one.convert('RGB'),two.convert('RGB'))
        return sum(v>8 for v in diff.convert('L').getdata())

def make_fixture(tile,color):
    img=Image.new('RGB',(1536,1024),color)
    d=ImageDraw.Draw(img)
    d.text((75,95),'V227 SYNTHETIC QA FIXTURE ONLY - NOT GAME ART',fill='white')
    d.rectangle((100,200,1400,250),fill=(255,255,255))
    p=OUT/f'qa-only-{tile}.png'
    img.save(p)
    return p

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    fixtures={'west':make_fixture('west',(110,32,65)),
              'south':make_fixture('south',(36,92,145))}
    server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler)
    threading.Thread(target=server.serve_forever,daemon=True).start()
    base=f'http://127.0.0.1:{server.server_port}/'
    report={'artApproved':False,'productionApproved':False,'historicalRoadsVerified':False,
            'sourceRegisteredToV123':False,'physicalIPhoneApproved':False,
            'actualArtReplaced':False,'syntheticFixtureOnly':True,'configurations':{}}
    try:
        with sync_playwright() as pw:
            for engine in ENGINES:
                browser=getattr(pw,engine).launch(headless=True)
                try:
                    for orient,w,h in ORIENTATIONS:
                        key=f'{engine}-{orient}'
                        page=browser.new_page(viewport={'width':w,'height':h},
                            is_mobile=True,has_touch=True,device_scale_factor=2)
                        errors=[]
                        page.on('pageerror',lambda e:errors.append(str(e)))
                        try:
                            page.goto(base+'v227-original-artwork-import-study.html?reviewCapture=1',
                                      wait_until='domcontentloaded',timeout=30000)
                            page.wait_for_function('window.V192?.ready===true',timeout=180000)
                            assert page.evaluate('V192.productionApproved') is False
                            assert page.evaluate('V192.v227ArtImport.cells.every(c=>c===null)')
                            original_nodes=page.evaluate('V192.roadNodeCount')
                            original_dest=page.evaluate('V192.destinations()')
                            assert page.evaluate('V192.focusTile("matrei")')
                            page.evaluate('V192.zoomTo(6)')
                            assert page.evaluate('V192.snapshotForReview()')
                            matrei_before=OUT/f'{key}-matrei-before.png'
                            page.screenshot(path=str(matrei_before),animations='disabled')
                            for tile in ('west','south'):
                                assert page.evaluate('(x)=>V192.focusTile(x)',tile)
                                page.evaluate('V192.zoomTo(6)')
                                assert page.evaluate('V192.snapshotForReview()')
                                before=OUT/f'{key}-{tile}-before.png'
                                page.screenshot(path=str(before),animations='disabled')
                                page.locator('#'+tile+'Art').set_input_files(str(fixtures[tile]))
                                idx=0 if tile=='west' else 1
                                page.wait_for_function('(idx)=>V192.v227ArtImport.cells[idx]!==null',arg=idx,timeout=30000)
                                assert page.evaluate('V192.snapshotForReview()')
                                after=OUT/f'{key}-{tile}-after.png'
                                page.screenshot(path=str(after),animations='disabled')
                                assert difference(before,after)>1000,(key,tile,'image did not change')
                            assert page.evaluate('V192.focusTile("matrei")')
                            assert page.evaluate('V192.snapshotForReview()')
                            matrei_after=OUT/f'{key}-matrei-after.png'
                            page.screenshot(path=str(matrei_after),animations='disabled')
                            with Image.open(matrei_before) as a,Image.open(matrei_after) as b:
                                W,H=a.size;crop=(int(W*.30),int(H*.28),int(W*.70),int(H*.68))
                                assert ImageChops.difference(a.crop(crop),b.crop(crop)).getbbox() is None,('Matrei changed',key)
                            assert page.evaluate('V192.roadNodeCount')==original_nodes
                            assert page.evaluate('V192.destinations()')==original_dest
                            assert page.evaluate('V192.orderTo("south")') is True
                            for fraction in (.2,.5,.8):
                                pos=page.evaluate('(f)=>V192.progress(f)',fraction)
                                assert page.evaluate('(p)=>V192.roadDistance(p)',pos)<.001
                            snap=page.evaluate('V192.v227ArtImport')
                            assert len(snap['cells'])==2
                            assert all(c and not c['productionApproved'] and not c['licenseVerified']
                                       and not c['roadClearanceVerified'] for c in snap['cells'])
                            assert not errors,(key,errors)
                            report['configurations'][key]={
                                'twoIndependentLocalImagesImported':True,
                                'onlyWestSouthArtChanged':True,
                                'matreiCenterUnchanged':True,
                                'originalRoadGraphAndArmyMovementUnchanged':True,
                                'sourceAndApprovalFlagsRemainFalse':True}
                        finally:page.close()
                finally:browser.close()
    finally:server.shutdown()
    sources=[OUT/f'webkit-portrait-{t}-after.png' for t in ('west','matrei','south')]
    if all(p.exists() for p in sources):
        contact=Image.new('RGB',(1170,680),'#19271f')
        draw=ImageDraw.Draw(contact)
        for i,(name,p) in enumerate(zip(('WEST','MATREI','SOUTH'),sources)):
            with Image.open(p) as im:
                contact.paste(im.convert('RGB').resize((390,650),Image.Resampling.LANCZOS),(i*390,30))
            draw.text((i*390+8,7),name+' / QA FIXTURE NOT ART',fill='white')
        contact.save(OUT/'actual-webkit-art-import-QA-only.jpg',quality=82)
    report['technicalPassed']=len(report['configurations'])==4
    (OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
    assert report['technicalPassed']

if __name__=='__main__':main()

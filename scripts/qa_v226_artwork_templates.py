#!/usr/bin/env python3
"""V226 actual four-browser iPhone artwork-authoring overlay QA, NOT art approval."""
import http.server
import json
import threading
from pathlib import Path
from PIL import Image, ImageChops, ImageDraw
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'qa/v226-artwork-templates'
ENGINES=('chromium','webkit')
ORIENTATIONS=(('portrait',390,844),('landscape',844,390))

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,directory=str(ROOT),**kwargs)
    def log_message(self,*args):
        pass

def changed(a,b):
    with Image.open(a) as one, Image.open(b) as two:
        diff=ImageChops.difference(one.convert('RGB'),two.convert('RGB'))
        return sum(1 for v in diff.convert('L').getdata() if v>8)

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler)
    threading.Thread(target=server.serve_forever,daemon=True).start()
    base=f'http://127.0.0.1:{server.server_port}/'
    report={'productionApproved':False,'artApproved':False,
            'sourceRegisteredToV123':False,'historicRoadsVerified':False,
            'fourV100ZoomTiersApproved':False,'physicalIPhoneApproved':False,
            'configurations':{}}
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
                            page.goto(base+'v226-cartway-artwork-workbench.html?reviewCapture=1',
                                wait_until='domcontentloaded',timeout=30000)
                            page.wait_for_function('window.V192?.ready===true',timeout=180000)
                            m=page.evaluate('V192.v226ArtworkContract')
                            assert m['version']==226 and len(m['cells'])==2,m
                            assert all(not c['productionApproved'] and not c['onwardRoadVerified']
                                and not c['sourceRegisteredToV123'] for c in m['cells'])
                            assert page.evaluate('V192.productionApproved') is False
                            assert page.evaluate('V192.connectedRoute') is True
                            assert page.evaluate('V192.v226ArtGuide') is False
                            before_nodes=page.evaluate('V192.roadNodeCount')
                            before_dest=page.evaluate('V192.destinations()')
                            for tile in ('west','matrei','south'):
                                assert page.evaluate('(x)=>V192.focusTile(x)',tile)
                                page.evaluate('()=>V192.zoomTo(6)')
                                assert page.evaluate('V192.snapshotForReview()')
                                off=OUT/f'{key}-{tile}-off.png'
                                page.screenshot(path=str(off),animations='disabled')
                                page.evaluate('document.querySelector("#artGuide").click()')
                                assert page.evaluate('V192.v226ArtGuide') is True
                                assert page.evaluate('V192.snapshotForReview()')
                                on=OUT/f'{key}-{tile}-on.png'
                                page.screenshot(path=str(on),animations='disabled')
                                delta=changed(off,on)
                                if tile in ('west','south'):
                                    assert delta>200,('art guide invisible',key,tile,delta)
                                else:
                                    with Image.open(off) as a,Image.open(on) as b:
                                        W,H=a.size
                                        crop=(int(W*.30),int(H*.28),int(W*.70),int(H*.68))
                                        assert ImageChops.difference(a.crop(crop),b.crop(crop)).getbbox() is None,('Matrei changed',key)
                                page.evaluate('document.querySelector("#artGuide").click()')
                                assert page.evaluate('V192.v226ArtGuide') is False
                            assert page.evaluate('V192.roadNodeCount')==before_nodes
                            assert page.evaluate('V192.destinations()')==before_dest
                            assert page.evaluate("V192.orderTo('south')") is True
                            for f in (.2,.5,.8):
                                p=page.evaluate('(f)=>V192.progress(f)',f)
                                assert page.evaluate('(p)=>V192.roadDistance(p)',p)<.001
                            assert page.evaluate('V192.historicRouteVerified') is False
                            assert not errors,(key,errors)
                            report['configurations'][key]={
                                'twoUnapprovedExactRoadArtGuidesVisible':True,
                                'matreiCenterUnchanged':True,
                                'originalGraphUnchanged':True,
                                'armyStillFollowsExactV123Graph':True}
                        finally:
                            page.close()
                finally:
                    browser.close()
    finally:
        server.shutdown()
    sources=[OUT/f'webkit-portrait-{t}-on.png' for t in ('west','matrei','south')]
    if all(p.exists() for p in sources):
        contact=Image.new('RGB',(1170,680),'#19271f')
        draw=ImageDraw.Draw(contact)
        for i,(name,file) in enumerate(zip(('WEST','MATREI','SOUTH'),sources)):
            with Image.open(file) as im:
                contact.paste(im.convert('RGB').resize((390,650),Image.Resampling.LANCZOS),(i*390,30))
            draw.text((i*390+8,7),name+' / V226 ACTUAL WebKit / ART NOT APPROVED',fill='white')
        contact.save(OUT/'actual-webkit-portrait-artwork-guide.jpg',quality=84,optimize=True)
    report['technicalPassed']=len(report['configurations'])==4
    (OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
    assert report['technicalPassed']

if __name__=='__main__':
    main()

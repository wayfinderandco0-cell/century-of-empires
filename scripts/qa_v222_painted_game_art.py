#!/usr/bin/env python3
"""V222 four-config ACTUAL original-painting quilt game/route trial. Not art approval."""
import http.server
import json
import threading
from pathlib import Path
from PIL import Image, ImageChops, ImageDraw
import base64
from playwright.sync_api import sync_playwright
import qa_v203_canopy_structure as strict

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'qa/v222-original-painting-game-art'
ORIENTATIONS=(('portrait',390,844),('landscape',844,390))
ENGINES=('chromium','webkit')
class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,directory=str(ROOT),**kwargs)
    def log_message(self,*args):
        pass

def difference(a,b):
    with Image.open(a) as one, Image.open(b) as two:
        x=ImageChops.difference(one.convert('RGB'),two.convert('RGB'))
        return sum(1 for v in x.convert('L').getdata() if v>8)

def capture(page,url,region,path):
    page.goto(url,wait_until='domcontentloaded',timeout=30000)
    page.wait_for_function('window.V192?.ready===true',timeout=180000)
    assert page.evaluate('(name)=>V192.focusTile(name)',region)
    page.evaluate('()=>V192.zoomTo(6)')
    page.evaluate('()=>V192.snapshotForReview()')
    page.screenshot(path=str(path),animations='disabled')

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler)
    threading.Thread(target=server.serve_forever,daemon=True).start()
    base=f'http://127.0.0.1:{server.server_port}/'
    report={'configurations':{},'productionApproved':False,
            'historicalRoadsVerified':False,'sourceRegisteredToV123':False,
            'humanArtApproved':False,'physicalIPhoneApproved':False}
    try:
        with sync_playwright() as pw:
            for engine in ENGINES:
                browser=getattr(pw,engine).launch(headless=True)
                try:
                    for orientation,w,h in ORIENTATIONS:
                        key=f'{engine}-{orientation}'
                        page=browser.new_page(viewport={'width':w,'height':h},
                            is_mobile=True,has_touch=True,device_scale_factor=2)
                        errors=[]
                        page.on('pageerror',lambda error:errors.append(str(error)))
                        try:
                            url=base+'v222-painterly-west-south-review.html?reviewCapture=1'
                            page.goto(url,wait_until='domcontentloaded',timeout=30000)
                            page.wait_for_function('window.V192?.ready===true',timeout=180000)
                            assert page.evaluate('V192.v222Trial') is True
                            sources=page.evaluate('V192.v222Sources')
                            assert len(sources)==2 and {s['tile'] for s in sources}=={'west','south'}
                            assert {(s['x'],s['y']) for s in sources}=={(0,0),(1536,1024)}
                            assert page.evaluate('V192.roadNodeCount')>=90
                            assert page.evaluate('V192.connectedRoute') is True
                            assert page.evaluate('V192.artDimensions')==[1536,1024]
                            assert page.evaluate('V192.productionApproved') is False
                            limits=page.evaluate('V192.surveyLimits')
                            assert len(limits['markers'])==2
                            assert all(m['onwardRoadVerified'] is False for m in limits['markers'])
                            assert page.evaluate("V192.orderTo('south')") is True
                            for t in (.15,.45,.85):
                                p=page.evaluate('(f)=>V192.progress(f)',t)
                                assert page.evaluate('(p)=>V192.roadDistance(p)',p)<.001
                            page.evaluate('V192.halt()')
                            assert page.evaluate("V192.orderTo('west')") is True
                            for t in (.1,.4,.8):
                                p=page.evaluate('(f)=>V192.progress(f)',t)
                                assert page.evaluate('(p)=>V192.roadDistance(p)',p)<.001
                            for p in ([80,615],[3010,1700],[100,100]):
                                assert page.evaluate('(p)=>V192.tapRoadWorld(p)',p) is False
                            for region in ('west','matrei','south'):
                                assert page.evaluate('(r)=>V192.focusTile(r)',region)
                                page.evaluate('()=>V192.zoomTo(6)')
                                assert page.evaluate('()=>V192.snapshotForReview()')
                                page.screenshot(path=str(OUT/f'{key}-{region}-close.png'),animations='disabled')
                                if region in ('west','south'):
                                    assert page.evaluate('V192.togglePainted()') is False
                                    assert page.evaluate('V192.snapshotForReview()')
                                    original=OUT/f'{key}-{region}-toggle-original.png'
                                    page.screenshot(path=str(original),animations='disabled')
                                    assert difference(original,OUT/f'{key}-{region}-close.png')>200
                                    assert page.evaluate('V192.togglePainted()') is True
                                    assert page.evaluate('V192.snapshotForReview()')
                            # Matrei screenshot is pixel-identical in center, even
                            # though candidate West/South art and page chrome differ.
                            baseline=browser.new_page(viewport={'width':w,'height':h},
                                is_mobile=True,has_touch=True,device_scale_factor=2)
                            try:
                                baseline.goto(base+'v192-weathered-cartways-graphics-test.html?reviewCapture=1',
                                    wait_until='domcontentloaded',timeout=30000)
                                baseline.wait_for_function('window.V192?.ready===true',timeout=180000)
                                changed={}
                                for region in ('west','matrei','south'):
                                    assert baseline.evaluate('(r)=>V192.focusTile(r)',region)
                                    baseline.evaluate('()=>V192.zoomTo(6)')
                                    assert baseline.evaluate('()=>V192.snapshotForReview()')
                                    p=OUT/f'{key}-{region}-baseline.png'
                                    baseline.screenshot(path=str(p),animations='disabled')
                                    changed[region]=difference(p,OUT/f'{key}-{region}-close.png')
                                assert changed['west']>200 and changed['south']>200,changed
                                # A center scene must not be overwritten by
                                # unregistered source imagery; UI chrome differs.
                                with Image.open(OUT/f'{key}-matrei-close.png') as a, Image.open(OUT/f'{key}-matrei-baseline.png') as b:
                                    W,H=a.size
                                    box=(int(W*.25),int(H*.28),int(W*.75),int(H*.72))
                                    assert ImageChops.difference(a.crop(box),b.crop(box)).getbbox() is None,('Matrei altered',key)
                            finally:
                                baseline.close()
                            assert not errors,(key,errors)
                            report['configurations'][key]={'routeGraphPreserved':True,
                                'twoDistinctNativePaintingMaterialCells':True,
                                'unverifiedRoadEndsRemainBlocked':True,
                                'changedPixelsVsOriginal':changed,
                                'MatreiCenterUnchanged':True}
                        finally:
                            page.close()
                finally:
                    browser.close()
    finally:
        server.shutdown()
    # Human-visible exact WebKit portrait contact, committed only to isolated
    # review branch. This is evidence, not an acceptance certificate.
    files=[OUT/f'webkit-portrait-{tile}-close.png' for tile in ('west','matrei','south')]
    if all(p.exists() for p in files):
        contact=Image.new('RGB',(1170,680),'#19271f')
        draw=ImageDraw.Draw(contact)
        for i,(tile,p) in enumerate(zip(('WEST','MATREI','SOUTH'),files)):
            with Image.open(p) as im:
                scaled=im.convert('RGB').resize((390,650),Image.Resampling.LANCZOS)
                contact.paste(scaled,(i*390,30))
            draw.text((i*390+8,7),tile+' / actual WebKit portrait / NOT APPROVED',fill='white')
        contact.save(OUT/'webkit-portrait-review.jpg',quality=78,optimize=True)
        raw=(OUT/'webkit-portrait-review.jpg').read_bytes()
        (OUT/'webkit-portrait-review-data.js').write_text(
            'window.V222PhoneReview="data:image/jpeg;base64,'+
            base64.b64encode(raw).decode('ascii')+'";\\n')
    # Preserve original strict V203 thresholds, without treating a numeric
    # pass as photographic human approval. Its report is still fail-closed.
    visual=strict.audit(OUT,OUT/'strict-v203',make_contact=True)
    report['strictV203']=visual
    report['technicalPassed']=len(report['configurations'])==4
    (OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'technicalPassed':report['technicalPassed'],
        'strictArtPassed':visual['passed'],'configurations':list(report['configurations'])},indent=2))
    assert report['technicalPassed']

if __name__=='__main__':
    main()

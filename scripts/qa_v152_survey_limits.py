#!/usr/bin/env python3
"""V152: browser screenshot evidence for real, graph-derived survey-limit icons.
This does NOT approve source art, geographic routes, 1780 roads or physical iPhone.
"""
import http.server
import json
import threading
from pathlib import Path
from PIL import Image, ImageChops
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'qa/v152-survey-limits'
OUT.mkdir(parents=True, exist_ok=True)

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)
    def log_message(self, *args):
        pass

server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), Handler)
threading.Thread(target=server.serve_forever, daemon=True).start()
url = f'http://127.0.0.1:{server.server_port}/v137-coherent-alpine-preview.html'
results = {}
try:
    with sync_playwright() as p:
        for engine in ('chromium', 'webkit'):
            browser = getattr(p, engine).launch(headless=True)
            try:
                for orientation, w, h in (('portrait', 390, 844), ('landscape', 844, 390)):
                    page = browser.new_page(viewport={'width':w,'height':h},
                        is_mobile=True,has_touch=True,device_scale_factor=2)
                    errors = []
                    page.on('pageerror', lambda e: errors.append(str(e)))
                    page.goto(url, wait_until='domcontentloaded',timeout=30000)
                    page.wait_for_function('window.V137?.ready === true',timeout=45000)
                    report = page.evaluate('V137.surveyLimits')
                    assert report['version']==152 and len(report['markers'])==2
                    assert report['productionApproved'] is False
                    assert report['unverifiedContinuationsDrawn'] is False
                    assert report['onwardNavigationApproved'] is False
                    assert [m['world'] for m in report['markers']]==[[275,550],[2806,1629]]
                    assert page.evaluate('V137.connectedRoute') is True
                    assert page.evaluate('V137.productionApproved') is False
                    assert page.evaluate('V137.seamStatus').__len__()==2
                    for region, camera, endpoint in (
                        ('west',(790,510),(275,550)),
                        ('south',(2300,1580),(2806,1629))):
                        assert page.evaluate('(region)=>V137.focusTile(region)',region)
                        page.evaluate('()=>new Promise(done=>requestAnimationFrame(()=>requestAnimationFrame(done)))')
                        prefix=f'{engine}-{orientation}-{region}'
                        with_marker=OUT/f'{prefix}-with-marker.png'
                        without_marker=OUT/f'{prefix}-without-marker.png'
                        page.screenshot(path=str(with_marker),animations='disabled')
                        page.evaluate('() => { window.__v152OriginalPaint=V152Survey.paint;V152Survey.paint=()=>{}; }')
                        page.evaluate('()=>new Promise(done=>requestAnimationFrame(()=>requestAnimationFrame(done)))')
                        page.screenshot(path=str(without_marker),animations='disabled')
                        page.evaluate('() => { V152Survey.paint=window.__v152OriginalPaint; }')
                        scale=min(w/3200,h/2450)*2.4
                        sx=(w/2+(endpoint[0]-camera[0])*scale)*2
                        sy=(h/2+(endpoint[1]-camera[1])*scale)*2
                        with Image.open(with_marker) as a, Image.open(without_marker) as b:
                            assert a.size==b.size==(w*2,h*2)
                            delta=ImageChops.difference(a.convert('RGB'),b.convert('RGB'))
                            left=max(0,int(sx)-35);right=min(w*2,int(sx)+36)
                            top=max(0,int(sy)-35);bottom=min(h*2,int(sy)+36)
                            assert left<right and top<bottom
                            crop=delta.crop((left,top,right,bottom))
                            # Marker is a rendered screen-space object, not merely
                            # a DOM/JS flag or an unobservable status message.
                            changed=sum(1 for px in crop.getdata() if max(px)>20)
                            assert changed>45,(prefix,'missing painted survey-limit icon',changed)
                            results[prefix]={'marker_pixel_changes':changed,
                                'screen_px':[round(sx,2),round(sy,2)],
                                'route_geometry_changed':False,
                                'art_or_historical_approval':False}
                    assert not errors,(engine,orientation,errors)
                    page.close()
            finally:
                browser.close()
finally:
    server.shutdown()
assert len(results)==8
(OUT/'report.json').write_text(json.dumps({'results':results,
    'browser_configs_passed':4,'source_road_approvals':0,
    'physical_iPhone_approved':False,'productionApproved':False},indent=2)+'\n')
print('V152: 4/4 mobile browser configurations, 8/8 survey-limit marker screenshot deltas PASS; no game-art/geographic approval.')

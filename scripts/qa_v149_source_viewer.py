#!/usr/bin/env python3
"""Four phone-browser views of REAL modern source pixels, never game octagons.

Run after the V147 orthophoto mosaic downloader writes qa/v149-source.
"""
import http.server
import json
import threading
from pathlib import Path
from PIL import Image
from playwright.sync_api import sync_playwright

root = Path(__file__).resolve().parents[1]
source = root / 'qa/v149-source'
out = root / 'qa/v149-browser'
out.mkdir(parents=True, exist_ok=True)
manifest = json.loads((source / 'manifest.json').read_text())
assert manifest['version'] == 147 and len(manifest['samples']) == 9
assert manifest['gameRouteGeoregistered'] is False
assert manifest['productionApproved'] is False
for s in manifest['samples']:
    with Image.open(source / s['imageFile']) as im:
        assert im.size == (256, 256) and im.format == 'JPEG'

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(root), **kw)
    def log_message(self, *args):
        pass

server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), Handler)
threading.Thread(target=server.serve_forever, daemon=True).start()
url = f'http://127.0.0.1:{server.server_port}/v149-geographic-source-viewer.html?local=1'
results = {}
try:
    with sync_playwright() as p:
        for engine in ('chromium', 'webkit'):
            browser = getattr(p, engine).launch(headless=True)
            try:
                for orient, width, height in (('portrait', 390, 844), ('landscape', 844, 390)):
                    page = browser.new_page(viewport={'width': width, 'height': height},
                        is_mobile=True, has_touch=True, device_scale_factor=2)
                    errors = []
                    page.on('pageerror', lambda e: errors.append(str(e)))
                    page.goto(url, wait_until='domcontentloaded', timeout=30000)
                    page.wait_for_function('window.V149?.ready===true', timeout=30000)
                    state = page.evaluate('''() => ({loaded:V149.loaded,failed:V149.failed,
                      tiles:V149.tileXYZ,flags:[V149.sourceOnly,V149.gameRouteGeoregistered,
                      V149.historic1780Certified,V149.gameOctagonCentersCertified,
                      V149.navigableRouteCertified,V149.productionApproved],
                      bounds:V149.boundsLonLat})''')
                    assert state['loaded'] == 9 and state['failed'] == 0
                    assert state['flags'] == [True, False, False, False, False, False]
                    assert len(state['tiles']) == 9
                    assert state['tiles'][0]['x'] + 2 == state['tiles'][-1]['x']
                    assert state['tiles'][0]['y'] + 2 == state['tiles'][-1]['y']
                    for a, b in zip(state['bounds'], manifest['mosaicBoundsLonLat']):
                        assert abs(a-b) < 1e-10
                    # Anchored zoom and pan preserve the exact geographic point.
                    before = page.evaluate('V149.screenToGeo(210,210)')
                    page.evaluate('V149.zoomAt(2,210,210)')
                    after = page.evaluate('V149.screenToGeo(210,210)')
                    assert all(abs(a-b)<1e-11 for a,b in zip(before,after))
                    page.evaluate('V149.panBy(35,-20)')
                    shifted = page.evaluate('V149.screenToGeo(245,190)')
                    assert all(abs(a-b)<1e-11 for a,b in zip(before,shifted))
                    page.locator('#reset').click()
                    page.screenshot(path=str(out/f'{engine}-{orient}-whole-source.png'))
                    for col, label in ((0,'west-source'),(1,'center-source'),(2,'east-source')):
                        assert page.evaluate('(c) => V149.focusSourceColumn(c)', col)
                        page.screenshot(path=str(out/f'{engine}-{orient}-{label}.png'))
                    assert not errors, errors
                    results[f'{engine}-{orient}'] = {'pass': True, 'realSourceTiles': 9,
                        'sourceOnly': True, 'geographicPanZoomLocked': True}
                    page.close()
            finally:
                browser.close()
finally:
    server.shutdown()
report = {'passed':len(results)==4, 'results':results,
          'gameOctagonsCompleted':False, 'routeRegistration':False,
          'humanArtApproval':False, 'historicalCertification':False}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
assert report['passed']

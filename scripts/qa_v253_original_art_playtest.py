#!/usr/bin/env python3
"""V253: original source pixels through actual V249 game renderer, ART RED.

WEST_SOURCE/SOUTH_SOURCE optionally point to independent fictional originals.
CI uses existing REJECTED V224 CC BY 4.0 fixtures. No graph or game edits.
"""
import hashlib
import http.server
import json
import os
from pathlib import Path
import shutil
import threading
from urllib.parse import urlencode

from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'qa/v253-original-art-playtest'
INPUT = OUT / 'sources'
CONFIGS = (('chromium','portrait',390,844), ('chromium','landscape',844,390),
           ('webkit','portrait',390,844), ('webkit','landscape',844,390))
FIXTURES = {'west': ROOT/'terrain-v224/assets/west.webp',
            'south': ROOT/'terrain-v224/assets/south.webp'}

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,directory=str(ROOT),**kwargs)
    def log_message(self,*args): pass

def prepare_sources():
    INPUT.mkdir(parents=True,exist_ok=True)
    report = {}
    for tile in ('west','south'):
        chosen = os.environ.get(tile.upper()+'_SOURCE')
        source = Path(chosen).resolve() if chosen else FIXTURES[tile]
        raw = source.read_bytes()
        with Image.open(source) as image:
            if image.size != (1536,1024) or image.format not in ('PNG','JPEG','WEBP'):
                raise ValueError(f'{tile}: expected original 1536x1024 PNG/JPEG/WebP')
            suffix = {'PNG':'.png','JPEG':'.jpg','WEBP':'.webp'}[image.format]
        target = INPUT/(tile+suffix)
        shutil.copyfile(source,target)
        report[tile] = {'sha256':hashlib.sha256(raw).hexdigest(),
                        'source':str(source),'url':'qa/v253-original-art-playtest/sources/'+target.name,
                        'originalPixelsUnmodified':True,
                        'sourceRegisteredToV123':False,
                        'historical1780RoadVerified':False,
                        'bridgeBanksVerified':False,'humanApproved':False}
    if report['west']['sha256']==report['south']['sha256']:
        raise ValueError('WEST/SOUTH must be distinct images')
    return report

def run():
    OUT.mkdir(parents=True,exist_ok=True)
    sources = prepare_sources()
    server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler)
    threading.Thread(target=server.serve_forever,daemon=True).start()
    params={'reviewCapture':'1'}
    for tile in ('west','south'):
        params[tile+'Src']=sources[tile]['url']
        params[tile+'Sha256']=sources[tile]['sha256']
    url=f'http://127.0.0.1:{server.server_port}/v249-pinned-source-art-review.html?'+urlencode(params)
    report={'version':253,'purpose':'ACTUAL_GAME_RENDERER_ORIGINAL_SOURCE_PIXELS_UNAPPROVED',
            'sources':sources,'fourBrowserTechnicalPass':False,
            'strictV203VisualPass':False,'historicalRoadsVerified':False,
            'sourceGameTiepointsVerified':False,'bridgeBanksVerified':False,
            'humanVisualApproval':False,'productionApproved':False,
            'configs':{}}
    try:
        with sync_playwright() as pw:
            for engine,orientation,w,h in CONFIGS:
                key=engine+'-'+orientation
                opts={}
                if engine=='chromium' and os.environ.get('V253_SYSTEM_CHROMIUM'):
                    opts['executable_path']=os.environ['V253_SYSTEM_CHROMIUM']
                browser=getattr(pw,engine).launch(headless=True,**opts)
                page=browser.new_page(viewport={'width':w,'height':h},
                         device_scale_factor=2,is_mobile=True,has_touch=True)
                errors=[]
                page.on('pageerror',lambda err:errors.append(str(err)))
                try:
                    page.goto(url,wait_until='domcontentloaded',timeout=60000)
                    page.wait_for_function("window.V192?.pinnedSourceReview?.state === 'loaded'",timeout=180000)
                    assert page.evaluate('V192.rawArtReview') is True
                    assert page.evaluate('V192.productionApproved') is False
                    assert page.evaluate('V192.connectedRoute') is True
                    nodes=page.evaluate('V192.roadNodeCount')
                    assert page.evaluate("V192.orderTo('south')") is False
                    for tile in ('west','matrei','south'):
                        assert page.evaluate('(id)=>V192.focusTile(id)',tile)
                        page.evaluate('V192.zoomTo(6)')
                        assert page.evaluate('V192.snapshotForReview()')
                        page.screenshot(path=str(OUT/f'{key}-{tile}-close.png'),animations='disabled')
                    assert page.evaluate('V192.setRawArtReview(false)') is True
                    assert page.evaluate("V192.orderTo('south')") is True
                    max_error=0
                    for f in (.2,.5,.8):
                        p=page.evaluate('(f)=>V192.progress(f)',f)
                        error=page.evaluate('(p)=>V192.roadDistance(p)',p)
                        max_error=max(max_error,error)
                        assert error<.001,(key,error)
                    assert page.evaluate('V192.roadNodeCount')==nodes
                    assert not errors,(key,errors)
                    report['configs'][key]={'rawWestMatreiSouthScreenshots':True,
                       'originalSourcePairShaVerified':True,'V123MovementRestored':True,
                       'maxArmyGraphDeviation':max_error,'MatreiOriginalRendererUsed':True,
                       'productionApproved':False}
                finally:
                    page.close();browser.close()
    finally:
        server.shutdown()
    shots=[OUT/f'webkit-portrait-{t}-close.png' for t in ('west','matrei','south')]
    if all(p.exists() for p in shots):
        contact=Image.new('RGB',(1170,680),'#17251e');draw=ImageDraw.Draw(contact)
        for i,(tile,p) in enumerate(zip(('west','matrei','south'),shots)):
            with Image.open(p) as img:
                contact.paste(img.convert('RGB').resize((390,650)),(i*390,30))
            draw.text((i*390+8,8),tile.upper()+' - UNAPPROVED ACTUAL BROWSER',fill='white')
        contact.save(OUT/'actual-webkit-portrait-UNAPPROVED.jpg',quality=86)
    report['fourBrowserTechnicalPass']=len(report['configs'])==4
    (OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2),flush=True)
    assert report['fourBrowserTechnicalPass']

if __name__=='__main__':run()

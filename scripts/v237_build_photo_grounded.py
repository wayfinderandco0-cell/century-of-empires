#!/usr/bin/env python3
"""V237: two independently CC0-licensed native-photo Alpine art studies.

These are source-proven *photographs*, not V123-registered geographic tiles,
historical cartways, verified bridge banks, or accepted game imagery.
Never paints synthetic roadbed under canopy. No Matrei pixels copied.
"""
import base64
import hashlib
import io
import json
import re
import time
from pathlib import Path

import cv2
import numpy as np
import requests
from PIL import Image, ImageDraw
import v232_route_ground_preflight as v232
import v235_canopy_aware_native_art as v235

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'qa/v237-photo-grounded'
ASSETS=ROOT/'terrain-v237/generated'
SOURCES={
 'west':{
  'url':'https://upload.wikimedia.org/wikipedia/commons/5/52/Forested_mountain_valley_%28Unsplash%29.jpg',
  'sha1':'4a01fd2356056ceea1bfdf0374751040fdbd0145',
  'size':[4288,2848], 'author':'Stijn te Strake',
  'place':'Schoenenbach, Bezau, Austria',
  'page':'https://commons.wikimedia.org/wiki/File:Forested_mountain_valley_(Unsplash).jpg',
  'fixedCrop':[960,1776,2496,2800]
 },
 'south':{
  'url':'https://upload.wikimedia.org/wikipedia/commons/e/e9/Alpine_valley_%28Unsplash%29.jpg',
  'sha1':'29667d44329ad6a36ce8f881e16dbcc51f8995db',
  'size':[5472,3078], 'author':'Paul Gilmore - Pastourmatzis',
  'place':'Brandenberg Alps, Austria',
  'page':'https://commons.wikimedia.org/wiki/File:Alpine_valley_(Unsplash).jpg'
 }
}
FALSE={**v232.FALSE_FLAGS,'gameArtApproved':False,'sourceRegisteredToV123':False,
       'licenseVerified':False,'roadClearanceVerified':False}
def download(tile, info):
    raw=None
    for delay in (0,12,35):
        if delay:time.sleep(delay)
        resp=requests.get(info['url'],timeout=90,headers={
          'User-Agent':'CenturyOfEmpires/0.3 (CC0 art study; github issue 9)'})
        if resp.status_code==429:continue
        resp.raise_for_status();raw=resp.content;break
    if raw is None:raise RuntimeError('Pinned CC0 source unavailable: '+tile)
    if hashlib.sha1(raw).hexdigest()!=info['sha1']:
        raise ValueError('STOP: original source SHA1 drift '+tile)
    with Image.open(io.BytesIO(raw)) as im:
        if list(im.size)!=info['size']:
            raise ValueError('STOP: source dimensions drift '+tile)
        image=im.convert('RGB')
    return image,hashlib.sha256(raw).hexdigest()

def candidate_crop(image, points, fixed=None):
    """Find a *single* contiguous native 1536x1024 crop, never cloned patches.

    Only on the new SOUTH source; WEST reuses the known V235 native meadow
    candidate. Fast integral-image ranking cannot certify terrain semantics.
    """
    w,h=image.size
    mask,_=v235.canopy_aware_ground_mask(image)
    integral=cv2.integral(mask)
    samples=v232.sample_polyline(points,spacing=20)
    def score(x,y):
        good=[]
        for px,py in samples:
            sx,sy=int(round(x+px)),int(round(y+py))
            x0,x1=max(0,sx-12),min(w,sx+13)
            y0,y1=max(0,sy-12),min(h,sy+13)
            total=(integral[y1,x1]-integral[y0,x1]
                   -integral[y1,x0]+integral[y0,x0])
            good.append(float(total)/max(1,(x1-x0)*(y1-y0)))
        passed=np.asarray(good)>=.67
        longest=run=0
        for ok in passed:
            run=0 if ok else run+1
            longest=max(longest,run)
        return (float(np.mean(passed))-.007*longest, float(np.mean(passed)),longest*20)
    if fixed:
        x0,y0,x1,y1=fixed
        if x1-x0!=1536 or y1-y0!=1024:raise ValueError('Invalid native crop')
        best=(score(x0,y0),x0,y0)
    else:
        best=None
        # New SOUTH source, one deliberate source replacement, not re-cropping
        # the V231/V235 rejected lake source.
        xs=sorted(set(list(range(0,w-1536+1,192))+[w-1536]))
        ys=sorted(set(list(range(0,h-1024+1,192))+[h-1024]))
        for y in ys:
            for x in xs:
                s=score(x,y)
                if best is None or s>best[0]:best=(s,x,y)
    s,x,y=best
    return image.crop((x,y,x+1536,y+1024)),[x,y,x+1536,y+1024],s

def verify_source(image,points,tile):
    # Correct V234 foliage false positives; apply same mask to final 25px
    # road corridor, never allow a heuristic pass to imply physical approval.
    old=v232.ground_mask
    try:
        v232.ground_mask=v235.canopy_aware_ground_mask
        return v232.inspect(image,points,tile)
    finally:v232.ground_mask=old

def write_preview():
    html=(ROOT/'v236-authored-alpine-playtest.html').read_text()
    html=html.replace('terrain-grid/v236-authored-alpine.js',
      'terrain-v237/generated/west-data.js"></script><script src="terrain-v237/generated/south-data.js"></script><script src="terrain-grid/v237-photo-grounded.js')
    html=html.replace('V236AuthoredAlpine.paint(cx,atlas)',
                      'V237PhotoGrounded.paint(cx,atlas)')
    html=html.replace('get v236Study()', 'get v237Study()')
    html=html.replace('version:236,kind:"FICTIONAL_AUTHORED_ALPINE_STUDY"',
                      'version:237,kind:"CC0_PHOTO_GROUND_STUDY"')
    html=html.replace('V236 ART STUDY','V237 PHOTO ART STUDY')
    html=html.replace('Original fictional Alpine composition · cartways unchanged · NOT APPROVED',
                      'Distinct licensed CC0 photos · geography and roads UNVERIFIED · NOT APPROVED')
    html=html.replace('Original fictional Alpine composition', 'CC0 photographic study')
    (ROOT/'v237-photo-grounded-playtest.html').write_text(html)
    qa=(ROOT/'scripts/qa_v236_authored_alpine.py').read_text()
    qa=qa.replace('v236','v237').replace('V236','V237')
    qa=qa.replace('FICTIONAL_AUTHORED_ALPINE_STUDY','CC0_PHOTO_GROUND_STUDY')
    qa=qa.replace("m['version']==236", "m['version']==237")
    qa=qa.replace("'version':236", "'version':237")
    qa=qa.replace('twoDistinctFictionalCompositionsRendered','twoDistinctCC0NativePhotosRendered')
    qa=qa.replace('v237-authored-alpine-playtest.html',
                  'v237-photo-grounded-playtest.html')
    qa=qa.replace("page.wait_for_function('window.V192?.ready===true',timeout=180000)",
      "page.wait_for_function('window.V192?.ready===true && window.V237PhotoGrounded?.loaded===true',timeout=180000)",1)
    (ROOT/'scripts/qa_v237_photo_grounded.py').write_text(qa)

def build():
    OUT.mkdir(parents=True,exist_ok=True);ASSETS.mkdir(parents=True,exist_ok=True)
    roads=v232.source_roads()
    records={}
    for tile,info in SOURCES.items():
        source,source_sha=download(tile,info)
        scene,crop,ranking=candidate_crop(source,roads[tile],info.get('fixedCrop'))
        metrics,review=verify_source(scene,roads[tile],tile)
        review.save(OUT/(tile+'-actual-native-ground-review.jpg'),quality=89)
        filename=tile+'-cc0-native.webp'
        path=ASSETS/filename
        scene.save(path,'WEBP',quality=92,method=6)
        raw=path.read_bytes()
        (ASSETS/(tile+'-data.js')).write_text(
          'window.V237'+tile.capitalize()+'Data="data:image/webp;base64,'+
          base64.b64encode(raw).decode('ascii')+'";\n')
        records[tile]={**info,'sourceSha256':source_sha,
          'crop':crop,'ranking':list(ranking),'nativePixels':[1536,1024],
          'assetSha256':hashlib.sha256(raw).hexdigest(),
          'assetBytes':len(raw),'license':'CC0 1.0',
          'licenseUrl':'https://creativecommons.org/publicdomain/zero/1.0/',
          'necessaryNativeGround':metrics,**FALSE}
    report={'version':237,'kind':'TWO_DISTINCT_CC0_NATIVE_PHOTO_STUDIES',
      'bothNecessaryGroundGatesPass':all(
       r['necessaryNativeGround']['necessaryRoadGroundGate'] for r in records.values()),
      'sources':records,'roadSource':'terrain-grid/v123-atlas.js',
      'photographicCameraAndHistoricRouteRegistration':'UNVERIFIED',
      'compositeMethod':'one contiguous unmodified source crop per tile; existing V123 cartway overlay only',
      **FALSE}
    (OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    write_preview()
    print(json.dumps({'sourceGround':{
      k:{'crop':v['crop'],'open':v['necessaryNativeGround']['openRoadbedArea'],
         'blocked':v['necessaryNativeGround']['longestBlockedRunPx']}
      for k,v in records.items()},'bothNecessary':report['bothNecessaryGroundGatesPass']},indent=2))
    return report

if __name__=='__main__':build()

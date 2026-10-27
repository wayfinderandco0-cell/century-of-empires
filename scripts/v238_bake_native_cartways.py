#!/usr/bin/env python3
"""V238 isolated native photographic cartway bake; not historical registration.

WEST: pinned V237 Stijn te Strake CC0 source-native 1536x1024 crop.
SOUTH: independently pinned Jace Grandinetti 2016 CC0 Gries am Brenner
photo. Never treat modern photographed tracks as verified 1780 cartways.
Bakes only on open photographic ground; rejects canopy/rock/water.
"""
import argparse
import base64
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import time
from urllib.parse import quote
import cv2
import numpy as np
import requests
from PIL import Image, ImageDraw
import v232_route_ground_preflight as v232
import v235_canopy_aware_native_art as v235
import v237_build_photo_grounded as v237

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'qa/v238-native-cartway'
ASSETS=ROOT/'terrain-v238/generated'
WEST_SHA256='425d85e01adb9a34a141d1f2860a2e35575bbad42ba1eda1392301f46ae78b41'
SOUTH_INFO={
 'filename':'Peaceful Austrian valley (Unsplash).jpg',
 'sha1':'f9cc498c7ff512e40a4d00023e1524a40fd9b898',
 'size':[6000,4000],
 'author':'Jace Grandinetti',
 'date':'2016-07-19',
 'place':'Gries am Brenner, Austria (NOT Matrei registration)',
 'page':'https://commons.wikimedia.org/wiki/File:Peaceful_Austrian_valley_(Unsplash).jpg',
 'license':'CC0 1.0',
 'licenseUrl':'https://creativecommons.org/publicdomain/zero/1.0/'
}
FALSE={**v232.FALSE_FLAGS,'gameArtApproved':False,'sourceRegisteredToV123':False,
 'historicalRoadsVerified':False,'bridgeBanksVerified':False,'humanVisualApproval':False,
 'physicalIPhoneApproved':False,'productionApproved':False}
PIN='09f04b4062e24fbacbb645307462cdddce2b2aa3'
def verify_graph():
    raw=(ROOT/'terrain-grid/v123-atlas.js').read_bytes()
    blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
    if blob!=PIN:raise ValueError('STOP: V123 immutable graph changed')
    return v232.source_roads()

def source_south():
    name=SOUTH_INFO['filename']
    md5=hashlib.md5(name.encode()).hexdigest()
    url='https://upload.wikimedia.org/wikipedia/commons/'+md5[0]+'/'+md5[:2]+'/'+quote(name)
    response=None
    for delay in (0,10):
        if delay:time.sleep(delay)
        response=requests.get(url,timeout=100,headers={'User-Agent':
          'CenturyOfEmpires/0.3 (attributed CC0 art experiment; issue 9)'})
        if response.status_code not in (429,503):break
    response.raise_for_status()
    raw=response.content
    if hashlib.sha1(raw).hexdigest()!=SOUTH_INFO['sha1']:
        raise ValueError('STOP: SOUTH pinned source SHA1 drift')
    with Image.open(io.BytesIO(raw)) as im:
        if list(im.size)!=SOUTH_INFO['size']:
            raise ValueError('STOP: SOUTH source dimensions drift')
        image=im.convert('RGB')
    return image,hashlib.sha256(raw).hexdigest(),url

def native_ground(image,road,tile):
    old=v232.ground_mask
    try:
        v232.ground_mask=v235.canopy_aware_ground_mask
        return v232.inspect(image,road,tile)
    finally:v232.ground_mask=old

def bake_cartway(image,road):
    """Bake physically narrower cartway on photographic ground, not on trees.

    Uses only the photograph's own fine texture as material: no noise, cloned
    patches, broad artificial grade, changed route points, or new bridge.
    This is an artistic interpretation and still requires screenshot review.
    """
    rgb=np.asarray(image.convert('RGB'))
    if rgb.shape!=(1024,1536,3):raise ValueError('Native 1536x1024 required')
    line=np.zeros((1024,1536),np.uint8)
    cv2.polylines(line,[np.asarray(road,np.int32)],False,255,1,cv2.LINE_8)
    dist=cv2.distanceTransform(255-line,cv2.DIST_L2,5).astype(np.float32)
    hsv=cv2.cvtColor(rgb,cv2.COLOR_RGB2HSV)
    h,s,v=cv2.split(hsv)
    clear=(h>=18)&(h<=48)&(s>=70)&(v>=65)&(v<=245)
    corridor=float(np.mean(clear[dist<=24]))
    f=rgb.astype(np.float32)
    high=np.clip(f-cv2.GaussianBlur(f,(0,0),sigmaX=5),-35,35)
    gray=cv2.cvtColor(rgb,cv2.COLOR_RGB2GRAY).astype(np.float32)
    tone=cv2.GaussianBlur(gray,(0,0),sigmaX=26)/255.
    dirt=np.empty_like(f)
    dirt[:,:,0]=105+34*tone+high[:,:,0]*.90
    dirt[:,:,1]=87+28*tone+high[:,:,1]*.80
    dirt[:,:,2]=60+22*tone+high[:,:,2]*.75
    dirt-=np.exp(-((dist-5.3)/1.6)**2)[:,:,None]*8
    road_alpha=np.clip((12.5-dist)/3.3,0,1)
    shoulder=np.clip((22.5-dist)/7.,0,1)*(1-road_alpha)
    edge=np.clip((27-dist)/5.,0,1)*(1-road_alpha)*(1-shoulder)
    out=f*(1-road_alpha[:,:,None])+dirt*road_alpha[:,:,None]
    verge=dirt*.60+f*.40
    out=out*(1-shoulder[:,:,None])+verge*shoulder[:,:,None]
    out=out*(1-edge[:,:,None])+(f*.83+dirt*.17)*edge[:,:,None]
    return Image.fromarray(np.uint8(np.clip(out,0,255))),corridor

def bake_scene(image,road,tile):
    metrics,ground_review=native_ground(image,road,tile)
    baked,open_fraction=bake_cartway(image,road)
    # Conservative necessary gate; never substitutes human source/route review.
    approved_for_technical_preview=(
        metrics['necessaryRoadGroundGate'] and open_fraction>=.80)
    return baked,ground_review,metrics,open_fraction,approved_for_technical_preview

def save_art(tile,art):
    ASSETS.mkdir(parents=True,exist_ok=True)
    path=ASSETS/(tile+'-native-cartway.webp')
    art.save(path,'WEBP',quality=91,method=6)
    data=base64.b64encode(path.read_bytes()).decode('ascii')
    (ASSETS/(tile+'-data.js')).write_text(
      'window.V238'+tile.capitalize()+'Data="data:image/webp;base64,'+data+'";\n')
    return {'assetSha256':hashlib.sha256(path.read_bytes()).hexdigest(),
            'assetBytes':path.stat().st_size}

def build(west_source):
    OUT.mkdir(parents=True,exist_ok=True)
    roads=verify_graph()
    raw=Path(west_source).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=WEST_SHA256:
        raise ValueError('STOP: WEST V237 source-native artifact SHA256 drift')
    west=Image.open(io.BytesIO(raw)).convert('RGB')
    if west.size!=(1536,1024):raise ValueError('WEST native source size drift')
    west_baked,west_review,wm,wopen,wok=bake_scene(west,roads['west'],'west')
    west_review.save(OUT/'west-unaltered-source-ground-review.jpg',quality=89)
    west_baked.save(OUT/'west-baked-cartway-review.jpg',quality=89)
    records={'west':{
        'author':'Stijn te Strake','license':'CC0 1.0',
        'page':'https://commons.wikimedia.org/wiki/File:Forested_mountain_valley_(Unsplash).jpg',
        'sourceAssetSha256':WEST_SHA256,'sourcePixels':[1536,1024],
        'necessaryGround':wm,'openCorridorFraction':wopen,
        'necessaryArtPreflight':wok,**FALSE}}
    # One new, independent source; no substitution with a rejected old source.
    try:
        south,source_sha,url=source_south()
        crop,box,rank=v237.candidate_crop(south,roads['south'])
        south_baked,south_review,sm,sopen,sok=bake_scene(crop,roads['south'],'south')
        south_review.save(OUT/'south-unaltered-source-ground-review.jpg',quality=89)
        south_baked.save(OUT/'south-baked-cartway-review.jpg',quality=89)
        records['south']={**SOUTH_INFO,'downloadUrl':url,
          'sourceSha256':source_sha,'nativeCrop':box,'nativeRanking':list(rank),
          'necessaryGround':sm,'openCorridorFraction':sopen,
          'necessaryArtPreflight':sok,**FALSE}
    except Exception as exc:
        # Fail closed and keep WEST evidence; no false substitute or preview.
        records['south']={'status':'BLOCKED','reason':str(exc),
          'necessaryArtPreflight':False,**FALSE}
        south_baked=None
    both=bool(wok and records['south']['necessaryArtPreflight'])
    report={'version':238,'kind':'NATIVE_PHOTO_CARTWAY_BAKE_UNAPPROVED',
      'bothNecessaryGroundGatesPass':both,'sourceRegistration':'UNVERIFIED',
      'roadGraph':'IMMUTABLE V123','westSouthSourceDistinct':True,
      'sources':records,**FALSE}
    if both:
        report['assets']={'west':save_art('west',west_baked),
                          'south':save_art('south',south_baked)}
        # An opt-in game preview is generated only after BOTH necessary gates.
        html=(ROOT/'v236-authored-alpine-playtest.html').read_text()
        html=html.replace('terrain-grid/v236-authored-alpine.js',
          'terrain-v238/generated/west-data.js"></script><script src="terrain-v238/generated/south-data.js"></script><script src="terrain-grid/v238-native-cartway.js')
        html=html.replace('V236AuthoredAlpine.paint(cx,atlas)',
                          'V238NativeCartway.paint(cx,atlas)')
        html=html.replace('get v236Study()', 'get v238Study()')
        html=html.replace('version:236,kind:"FICTIONAL_AUTHORED_ALPINE_STUDY"',
                          'version:238,kind:"NATIVE_PHOTO_CARTWAY_BAKE_UNAPPROVED"')
        html=html.replace('V236 ART STUDY','V238 CARTWAY STUDY')
        html=html.replace('Original fictional Alpine composition',
                          'Source-grounded fictional cartway study')
        (ROOT/'v238-native-cartway-playtest.html').write_text(html)
    (OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'bothNecessary':both,
       'westOpen':wopen,'south':records['south'].get('openCorridorFraction',
       records['south'].get('reason'))},indent=2))
    return report

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--west',type=Path,required=True)
    args=parser.parse_args()
    result=build(args.west)
    if not result['bothNecessaryGroundGatesPass']:
        raise SystemExit('V238 art source preflight RED; no playable preview promoted')

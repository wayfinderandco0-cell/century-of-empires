#!/usr/bin/env python3
"""Reconstruct SOUTH's Matrei-border photographic material, isolated V267 only.

The native SOUTH trees, road, river and bridge stay in their original positions.
No V121/V123/V94, sprites, saves or production changes. The result is a
fictional game-art candidate, staged only at ?southArt=apron.
"""
from __future__ import annotations
import base64, hashlib, io, json, re
from pathlib import Path
import cv2
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
HTML=ROOT/'v267-three-octagon-original-art-prototype.html'
SOUTH=ROOT/'art-reviews/v267-original-source/south-bridge-contact-unapproved.webp'
OUTPUT=ROOT/'art-reviews/v267-original-source/south-matrei-material-apron-unapproved.webp'
MANIFEST=OUTPUT.with_suffix('.json')
W,H=1536,1024
MARKER='SOUTH_MATREI_MATERIAL_APRON_20261029'

def smooth(t):
    t=np.clip(t,0,1)
    return t*t*(3-2*t)

def matrei_display_edge(html):
    m=re.search(r'ART_MATREI_CANONICAL="data:image/[^;]+;base64,([^"]+)"',html)
    if not m:
        raise RuntimeError('Canonical V121 image missing')
    source=np.asarray(Image.open(io.BytesIO(base64.b64decode(m.group(1)))).convert('RGB'))
    if source.shape[:2]!=(H,W):
        raise RuntimeError('Unexpected Matrei dimensions')
    x=np.arange(W,dtype=np.float32)[None,:]
    y=np.arange(982,1024,dtype=np.float32)[:,None]
    t=smooth((y-845)/179)
    sy=10+y*(953/H)-26*t
    sl=np.where(sy<286,385-(sy-10)*(295/276),np.where(sy>674,90+(sy-674)*(295/289),90))
    tl=np.where(y<256,256-y,np.where(y>768,y-768,0))
    tr=W-tl
    b=smooth((y-700)/324)
    sx=np.clip(sl+(x-tl)*(W-2*sl)/(tr-tl)-55*b*np.exp(-.5*((x-466)/105)**2),0,W-1.001)
    west=26*np.exp(-.5*((x-240)/400)**2)*np.exp(-.5*((y-505)/110)**2)
    return cv2.remap(source,sx.astype('float32'),
                     np.clip(sy+west,0,H-1.001).astype('float32'),cv2.INTER_LINEAR)

def harmonize(native,edge):
    """No geometry resampling; keep SOUTH below row 300 bit-for-bit native."""
    rgb=native.astype(np.uint8)
    lab=cv2.cvtColor(rgb,cv2.COLOR_RGB2LAB).astype(np.float32)
    ml=cv2.cvtColor(edge,cv2.COLOR_RGB2LAB).astype(np.float32)
    mat=np.median(ml[-14:-3],axis=0)
    own=np.median(lab[4:17],axis=0)
    delta=mat-own
    delta[:,0]=np.clip(delta[:,0],-19,19)
    delta[:,1:]=np.clip(delta[:,1:],-8,8)
    delta=cv2.GaussianBlur(delta[None,:,:],(0,0),31)[0]
    x=np.arange(W,dtype=np.float32)
    y=np.arange(H,dtype=np.float32)
    span=smooth((x-252)/85)*smooth((1284-x)/85)
    protect_road=1-0.32*np.exp(-0.5*((x-466)/48)**2)
    weight=(span*protect_road)[None,:]*smooth((300-y)/300)[:,None]*0.88
    corrected=np.clip(lab+weight[:,:,None]*delta[None,:,:],0,255).astype(np.uint8)
    result=cv2.cvtColor(corrected,cv2.COLOR_LAB2RGB)
    result[300:]=rgb[300:]
    # Genuine Matrei pixels only at the physical cartway and river joins:
    # 14px, never an invented digital road or repeated forest strip.
    xx=np.arange(W,dtype=np.float32)[None,:]
    yy=np.arange(14,dtype=np.float32)[:,None]
    road=np.exp(-.5*((xx-466)/48)**4)
    river=np.exp(-.5*((xx-930)/95)**4)
    alpha=.80*(1-smooth(yy/14))*np.clip(road+river,0,1)
    result[:14]=np.uint8(np.clip(
        result[:14]*(1-alpha[:,:,None])+edge[-14:]*alpha[:,:,None],0,255))
    return result

def stage_html(html):
    if MARKER in html:
        return html
    old='const SOUTH_BRIDGE_CONTACT_PREVIEW=SOUTH_ART_MODE==="bridge";'
    new='const SOUTH_APRON_PREVIEW=SOUTH_ART_MODE==="apron"; /* '+MARKER+' */\n'+old
    if html.count(old)!=1: raise RuntimeError('SOUTH mode changed')
    html=html.replace(old,new,1)
    old='const SOUTH_ORIGINAL_PREVIEW=SOUTH_ART_MODE==="original"||SOUTH_BRIDGE_CONTACT_PREVIEW;'
    new='const SOUTH_ORIGINAL_PREVIEW=SOUTH_ART_MODE==="original"||SOUTH_BRIDGE_CONTACT_PREVIEW||SOUTH_APRON_PREVIEW;'
    if html.count(old)!=1: raise RuntimeError('SOUTH alternate mode changed')
    html=html.replace(old,new,1)
    old='const southArtSource=SOUTH_BRIDGE_CONTACT_PREVIEW'
    new=('const southArtSource=SOUTH_APRON_PREVIEW\n'
         '  ? "art-reviews/v267-original-source/south-matrei-material-apron-unapproved.webp"\n'
         '  : SOUTH_BRIDGE_CONTACT_PREVIEW')
    if html.count(old)!=1: raise RuntimeError('SOUTH source selection changed')
    html=html.replace(old,new,1)
    assert html.count('const southRoad=')==1 and html.count('const westRoad=')==1
    return html

def main():
    html=HTML.read_text(encoding='utf-8')
    if MARKER in html and OUTPUT.is_file():
        print('Candidate already staged; no repeat resampling')
        return
    with Image.open(SOUTH) as f:
        if f.size!=(W,H): raise RuntimeError('Wrong SOUTH source dimensions')
        native=np.asarray(f.convert('RGB'))
    edge=matrei_display_edge(html)
    art=harmonize(native,edge)
    assert np.array_equal(art[300:],native[300:])
    assert np.mean(np.abs(art[:280].astype(np.int16)-native[:280].astype(np.int16)))>0.3
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    Image.fromarray(art).save(OUTPUT,'WEBP',quality=93,method=6)
    HTML.write_text(stage_html(html),encoding='utf-8')
    MANIFEST.write_text(json.dumps({
      'status':'UNAPPROVED; production RED',
      'provenance':'fictional Alpine game artwork; not verified historic geography',
      'source':str(SOUTH.relative_to(ROOT)),
      'source_sha256':hashlib.sha256(SOUTH.read_bytes()).hexdigest(),
      'candidate':str(OUTPUT.relative_to(ROOT)),
      'candidate_sha256':hashlib.sha256(OUTPUT.read_bytes()).hexdigest(),
      'dimensions':[W,H],
      'preview':'?southArt=apron',
      'registration':'zero geometry shift; 300px photographic material apron; 14px road/river contact',
      'road_seams_unchanged':{'west':[1536,478],'south':[466,0]},
      'requires':'real phone-size visual comparison, physical iPhone Safari approval',
      'protected':'V121/V123/V94, sprites, saves, main unchanged'
    },indent=2)+'\n')
    print('Rebuilt original SOUTH material apron:',OUTPUT,OUTPUT.stat().st_size,'bytes')

if __name__=='__main__':
    main()

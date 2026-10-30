#!/usr/bin/env python3
"""Author a NEW northern SOUTH river basin (fictional Alpine atlas art).

Unlike earlier rigid donor shifts, this paints a continuous river footprint
from the V121 south-edge geometry into the native SOUTH gorge. It synthesizes
photographic *material* in small irregular patches without cloning any tree,
house, bridge or complete Matrei landscape. All source art and gameplay remain.
Only ?southArt=basin opts in. Unapproved until actual iPhone visual review.
"""
from __future__ import annotations
import base64, hashlib, io, json, re
from pathlib import Path
import cv2
import numpy as np
from PIL import Image
from v267_south_matrei_material_rebuild import matrei_display_edge

ROOT=Path(__file__).resolve().parents[1]
HTML=ROOT/'v267-three-octagon-original-art-prototype.html'
MATREI=ROOT/'v121-octagon-1-painted-road.html'
SOUTH=ROOT/'art-reviews/v267-original-source/south-bridge-contact-unapproved.webp'
OUT=ROOT/'art-reviews/v267-original-source/south-new-northern-basin-unapproved.webp'
REPORT=ROOT/'art-reviews/v267-northern-basin-review.md'
W,H=1536,1024
SEED=20261030
MARK='V267_NEW_NORTHERN_BASIN_SOURCE_20261030'

def smooth(t):
    t=np.clip(t,0,1)
    return t*t*(3-2*t)

def get_matrei():
    text=MATREI.read_text()
    m=re.search(r'data:image/webp;base64,([A-Za-z0-9+/=]+)',text)
    if not m: raise RuntimeError('V121 source missing')
    return np.asarray(Image.open(io.BytesIO(base64.b64decode(m.group(1)))).convert('RGB'))

def photo_quilt(donor, good, size, rng, tile=56):
    """Assemble real small-scale water/rock material without whole-scene copies."""
    h,w=size
    stride=tile//2
    candidates=[]
    dh,dw=donor.shape[:2]
    for y in range(0,dh-tile,8):
        for x in range(0,dw-tile,8):
            if good[y:y+tile,x:x+tile].mean()>.75:
                candidates.append((x,y))
    if len(candidates)<6:
        # Conservative fallback: do not silently fabricate an entire water scene.
        raise RuntimeError(f'Insufficient photographed texture patches: {len(candidates)}')
    acc=np.zeros((h,w,3),np.float32)
    weight=np.zeros((h,w),np.float32)
    hann=np.outer(np.hanning(tile),np.hanning(tile)).astype(np.float32)
    hann=.04+.96*hann
    for yy in range(-stride,h,stride):
        for xx in range(-stride,w,stride):
            sx,sy=candidates[int(rng.integers(len(candidates)))]
            patch=donor[sy:sy+tile,sx:sx+tile].astype(np.float32)
            y0=max(0,yy);x0=max(0,xx)
            y1=min(h,yy+tile);x1=min(w,xx+tile)
            if y1<=y0 or x1<=x0:continue
            py0=y0-yy;px0=x0-xx
            alpha=hann[py0:py0+y1-y0,px0:px0+x1-x0]
            acc[y0:y1,x0:x1]+=patch[py0:py0+y1-y0,px0:px0+x1-x0]*alpha[:,:,None]
            weight[y0:y1,x0:x1]+=alpha
    return np.uint8(np.clip(acc/np.maximum(weight[:,:,None],.001),0,255))

def build(native,matrei,edge):
    rng=np.random.default_rng(SEED)
    result=native.copy()
    # Draw an ORIGINAL, continuously narrowing gorge footprint. Its northern
    # mouth is broad like Matrei's river, while its lower reach reconnects to
    # the original SOUTH river above the stone bridge. No whole-image warp.
    knots=np.array([
      [0,925,154],[75,948,145],[155,987,135],[230,1030,126],
      [310,1065,112],[385,1103,101],[448,1130,89]
    ],dtype=np.float32)
    y=np.arange(H,dtype=np.float32)
    center=np.interp(y,knots[:,0],knots[:,1])
    radius=np.interp(y,knots[:,0],knots[:,2])
    x=np.arange(W,dtype=np.float32)
    xx,yy=np.meshgrid(x,y)
    # Irregular rocky shoreline, not a straight geometric stripe.
    shore=7*np.sin(yy*.039+np.sin(yy*.012)*2)+5*np.sin(yy*.11+1.7)
    shore+=4*np.sin(yy*.17+2.3)
    distance=np.abs(xx-center[:,None])-radius[:,None]-shore
    water=smooth((8-distance)/16)
    water*=smooth((450-yy)/85)
    water[:,:710]=0
    water[:,1420:]=0
    water[450:]=0

    # Real photographed water material, assembled as many independent small
    # swatches. No duplicated waterfall, trees, bridge or entire Matrei scene.
    hsv=cv2.cvtColor(matrei,cv2.COLOR_RGB2HSV)
    good=((hsv[:,:,0]>=76)&(hsv[:,:,0]<=118)&
          (hsv[:,:,1]>=35)&(hsv[:,:,2]>=55)).astype(np.float32)
    donor=matrei[440:950,600:1160]
    donor_good=good[440:950,600:1160]
    water_tex=photo_quilt(donor,donor_good,(450,710),rng,tile=44)
    # Blend in native SOUTH water for a gradual transition in material,
    # rather than a sharp switch between two photographic sources.
    source_hsv=cv2.cvtColor(native,cv2.COLOR_RGB2HSV)
    native_good=((source_hsv[:,:,0]>=75)&(source_hsv[:,:,0]<=125)&
                 (source_hsv[:,:,1]>=30)&(source_hsv[:,:,2]>=45)).astype(np.float32)
    try:
        local_tex=photo_quilt(native[80:960,800:1500],
                              native_good[80:960,800:1500],
                              (450,710),rng,tile=36)
        factor=smooth((yy[:450,710:1420]-120)/250)[:,:,None]
        water_tex=np.uint8(water_tex*(1-factor)+local_tex*factor)
    except RuntimeError:
        pass
    region=result[:450,710:1420].astype(np.float32)
    alpha=water[:450,710:1420,None]
    result[:450,710:1420]=np.uint8(np.clip(region*(1-alpha)+water_tex*alpha,0,255))

    # Rock/gravel banks from native SOUTH material. Each bank is a real
    # textured strip 10-32px thick, following the irregular river edge.
    # No synthetic olive green gap or entire forest displacement.
    native_hsv=cv2.cvtColor(native,cv2.COLOR_RGB2HSV)
    rock=((native_hsv[:,:,1]<95)&(native_hsv[:,:,2]>65)&
          (native_hsv[:,:,2]<205)).astype(np.float32)
    # Prefer limestone donors from the existing SOUTH cliffs, never roads.
    rock_donor=native[160:750,740:1450]
    rock_good=rock[160:750,740:1450]
    try:
        gravel=photo_quilt(rock_donor,rock_good,(450,710),rng,tile=34)
        apron=smooth((distance-1)/10)*smooth((42-distance)/25)
        apron*=smooth((440-yy)/75)
        apron[:,:710]=0;apron[:,1420:]=0;apron[450:]=0
        a=(apron[:450,710:1420]*.78)[:,:,None]
        base=result[:450,710:1420].astype(np.float32)
        result[:450,710:1420]=np.uint8(np.clip(base*(1-a)+gravel*a,0,255))
    except RuntimeError:
        pass

    # The displayed Matrei border is sampled from the REAL V121 renderer
    # transform (not the source image's gold frame). A 20px contact layer
    # joins road, banks and water without transplanting a repeated forest.
    contact=edge[-1].astype(np.float32)
    for row in range(24):
        f=.93*(1-smooth(row/24))
        road_contact=np.exp(-.5*((x-466)/44)**4)
        road_contact[np.abs(x-466)>75]=0
        mask=(smooth((x-685)/65)*smooth((1350-x)/65)+
              road_contact).clip(0,1)
        a=(f*mask)[:,None]
        result[row]=np.uint8(np.clip(result[row]*(1-a)+contact*a,0,255))
    assert np.array_equal(result[460:],native[460:])
    assert np.array_equal(result[:450,:370],native[:450,:370])
    assert np.array_equal(result[:450,1450:],native[:450,1450:])
    changed=int(np.count_nonzero(np.max(abs(result.astype(np.int16)-native.astype(np.int16)),axis=2)>8))
    assert changed>85000,changed
    return result,changed

def stage(html):
    if MARK in html:return html
    key='const SOUTH_GORGE_RIVER_PREVIEW=SOUTH_ART_MODE==="gorge";'
    assert html.count(key)==1
    html=html.replace(key,'const SOUTH_BASIN_PREVIEW=SOUTH_ART_MODE==="basin"; /* '+MARK+' */\n'+key,1)
    key='const southArtSource=SOUTH_GORGE_RIVER_PREVIEW'
    assert html.count(key)==1
    html=html.replace(key,'const southArtSource=SOUTH_BASIN_PREVIEW\n  ? "art-reviews/v267-original-source/south-new-northern-basin-unapproved.webp"\n  : SOUTH_GORGE_RIVER_PREVIEW',1)
    assert html.count('const southRoad=')==1 and html.count('const westRoad=')==1
    assert '[1536,478]' in html and '[466,0]' in html
    return html

def main():
    html=HTML.read_text()
    with Image.open(SOUTH) as im:native=np.asarray(im.convert('RGB'))
    matrei=get_matrei()
    assert native.shape==(H,W,3) and matrei.shape==(H,W,3)
    edge=matrei_display_edge(html)
    art,changed=build(native,matrei,edge)
    OUT.parent.mkdir(parents=True,exist_ok=True)
    Image.fromarray(art).save(OUT,'WEBP',quality=94,method=6)
    updated=stage(html)
    if updated!=html:HTML.write_text(updated)
    REPORT.write_text(
      '# SOUTH northern basin — ORIGINAL material reconstruction, UNAPPROVED\n\n'
      'A new authored river footprint narrows from the Matrei southern edge into '
      'the original SOUTH gorge, using photographic water and limestone material '
      'from multiple small nonrepeating swatches, without copying Matrei trees, '
      'settlements, bridge or complete scene. Road x466, original SOUTH bridge, '
      'all terrain below y460, V121/V123/V94/sprites/saves and main protected.\n\n'
      'This is fictional 1780–1880 atmosphere game art, NOT verified topography.\n'
      f'Changed source pixels: {changed}; artwork: {OUT.relative_to(ROOT)}.\n'
      'Actual same-camera Chromium/WebKit screenshots and physical iPhone '
      'inspection are REQUIRED. This is not visually approved. Production RED.\n')
    print(json.dumps({'output':str(OUT.relative_to(ROOT)),
      'bytes':OUT.stat().st_size,'changed_pixels':changed,
      'status':'UNAPPROVED','html_staged':updated!=html}))
if __name__=='__main__':main()

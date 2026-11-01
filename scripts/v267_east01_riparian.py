#!/usr/bin/env python3
"""EAST-01 V267 original-ridge riparian continuity candidate; never alters approved art.

Reworks ONLY the previously authored original east ridge. No heightmesh, screenshot
crop, tree cloning, invented bridge, historical road, or V123 graph change.
A photographic/AI original ridge remains the relief and vegetation source.
The narrow river material is inferred from V121's actual river colors, and its
route is provisional until the physical edge is independently reviewed.
"""
from __future__ import annotations
import hashlib, json, math
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter, ImageDraw

ROOT=Path(__file__).resolve().parents[1]
DIR=ROOT/"terrain-grid"/"v267-original-art-batch-01"
MATREI=ROOT/"terrain-grid"/"art"/"matrei-v121-original.webp"
RIDGE=DIR/"matrei-east-ridge.webp"
W,H=1536,1024

def smooth(x):
    t=np.clip(x,0,1)
    return t*t*(3-2*t)

def registered_matrei(original):
    """Same world registration formulas as atlas-integrated.js, review only."""
    source=np.asarray(original.convert("RGB"),dtype=np.float32)
    y=np.arange(H,dtype=np.float32)[:,None]
    x=np.arange(W,dtype=np.float32)[None,:]
    t=smooth((y-845)/179)
    sy0=10+y*(953/H)-26*t
    sl=np.where(sy0<286,385-(sy0-10)*(295/276),
                np.where(sy0>674,90+(sy0-674)*(295/289),90))
    tl=np.where(y<256,256-y,np.where(y>768,y-768,0))
    tr=W-tl
    south=np.exp(-.5*((x-466)/105)**2)
    west=np.exp(-.5*((x-240)/400)**2)
    b=smooth((y-700)/324)
    wy=26*np.exp(-.5*((y-505)/110)**2)
    sx=np.clip(sl+(x-tl)*(W-2*sl)/(tr-tl)-55*b*south,0,W-1.001)
    sy=np.clip(sy0+wy*west,0,H-1.001)
    x0=np.floor(sx).astype(np.int32);y0=np.floor(sy).astype(np.int32)
    fx=(sx-x0)[...,None];fy=(sy-y0)[...,None]
    a=source[y0,x0];c=source[y0,x0+1]
    d=source[y0+1,x0];e=source[y0+1,x0+1]
    result=(1-fy)*((1-fx)*a+fx*c)+fy*((1-fx)*d+fx*e)
    return np.uint8(np.clip(result,0,255))

def river_material(m):
    """Estimate a water palette and east-bank exit from native Matrei pixels."""
    area=m[350:890,650:1390].astype(np.float32)
    water=(area[:,:,2]>area[:,:,0]*1.15)&(area[:,:,1]>area[:,:,0]*1.05)&(area[:,:,2]>48)
    pixels=area[water]
    palette=np.median(pixels,axis=0) if len(pixels)>500 else np.array([48,98,105])
    edge=m[340:730,1460:1490].astype(np.float32)
    mask=(edge[:,:,2]>edge[:,:,0]*1.15)&(edge[:,:,1]>edge[:,:,0]*1.05)&(edge[:,:,2]>48)
    row_count=mask.sum(axis=1)
    # Only an observed connected water band may set the exit. Otherwise keep
    # a provisional position, explicitly flagged as NOT a verified river seam.
    observed=bool(row_count.max()>=12)
    y_exit=int(np.argmax(np.convolve(row_count,np.ones(31),mode="same"))+340) if observed else 525
    return np.clip(palette,[28,55,59],[100,150,160]),y_exit,observed

def generate():
    for p in (MATREI,RIDGE):
        if not p.is_file():raise SystemExit(f"Required original art missing: {p}")
    matrei=Image.open(MATREI).convert("RGB")
    ridge=Image.open(RIDGE).convert("RGB")
    if matrei.size!=(W,H) or ridge.size!=(W,H):raise SystemExit("Native V267 art must be 1536x1024")
    m=registered_matrei(matrei)
    palette,y_exit,observed=river_material(m)
    rng=np.random.default_rng(2671101)
    yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
    # A natural, unbranched provisional channel: no bridge or road is painted.
    center=y_exit+32*np.sin(xx/260)+.105*xx
    half_width=46+11*np.sin(xx/380+1.1)
    dist=np.abs(yy-center)
    bank=np.clip((half_width+28-dist)/29,0,1)
    river=np.clip((half_width-dist)/12+.5,0,1)
    river=smooth(river)
    # Multiscale, locally shaded water material from V121's observed palette.
    grain=Image.fromarray(np.uint8(rng.random((H,W))*255),"L")
    fine=np.asarray(grain.filter(ImageFilter.GaussianBlur(2.2)),dtype=np.float32)-127
    broad=np.asarray(grain.filter(ImageFilter.GaussianBlur(14)),dtype=np.float32)-127
    variation=1.5*fine+2.4*broad
    water=np.empty((H,W,3),dtype=np.float32)
    water[:]=palette
    water+=variation[:,:,None]*np.array([.55,.78,1.1])[None,None,:]
    glints=(np.sin(xx*.11+np.sin(yy*.045)*3)>0.97)&(dist<half_width*.7)
    water[glints]+=np.array([17,24,24])
    water=np.clip(water,0,255)
    base=np.asarray(ridge,dtype=np.float32).copy()
    # Dark, grassy banks tint the original ridge rather than replacing its
    # natural trees or relief with a synthetic/duplicated landscape.
    green=np.array([58,78,44],dtype=np.float32)
    a_bank=(bank-river)*.18
    base=base*(1-a_bank[:,:,None])+green*a_bank[:,:,None]
    a_water=river*.94
    base=base*(1-a_water[:,:,None])+water*a_water[:,:,None]
    # Native-scale boundary registration: a short source-material transition
    # from Matrei's registered interior, never its black/gold frame.
    # Limited to 56 px; not a clone of a landscape or a false road.
    strip=m[:,1420:1476].astype(np.float32)
    for x in range(56):
        alpha=.86*(1-smooth(x/56))
        base[:,x,:]=base[:,x,:]*(1-alpha)+strip[:,55-x,:]*alpha
    out=Image.fromarray(np.uint8(np.clip(base,0,255)),"RGB")
    target=DIR/"matrei-east-riparian-v3.webp"
    out.save(target,"WEBP",quality=91,method=6)
    # Actual native-scale visual evidence; no fabricated screenshot or WebKit claim.
    contact=Image.new("RGB",(3072,1024),(19,30,24))
    contact.paste(Image.fromarray(m),(0,0));contact.paste(out,(1536,0))
    draw=ImageDraw.Draw(contact)
    draw.line([(1536,256),(1536,768)],fill=(225,182,104),width=3)
    comparison=DIR/"matrei-east-riparian-v3-comparison.webp"
    contact.save(comparison,"WEBP",quality=84,method=6)
    thumb=DIR/"matrei-east-riparian-v3-thumb.webp"
    contact.resize((1024,341),Image.Resampling.LANCZOS).save(thumb,"WEBP",quality=70,method=6)
    data={"schema":"coe-v267-east-riparian-candidate/v1","sourceOriginal":"matrei-east-ridge.webp",
          "referenceMatrei":"terrain-grid/art/matrei-v121-original.webp",
          "output":target.name,"comparison":comparison.name,"thumbnail":thumb.name,
          "sha256":hashlib.sha256(target.read_bytes()).hexdigest(),
          "riverExitY":y_exit,"riverExitDetectedFromSource":observed,
          "roadPorts":[],"roadsVerified":False,"riverSeamVerified":False,
          "mobileWebkitRendered":False,"visuallyReviewed":False,
          "nativePlayable":False,"historicallyVerified":False,
          "userApproved":False,"finished":False,
          "notes":"Unapproved physical terrain continuation study. Registered V121 pixels and original ridge used; provisional river path needs real visual QA. No invented cartway."}
    (DIR/"matrei-east-riparian-v3-evidence.json").write_text(json.dumps(data,indent=2)+"\n")
    print(json.dumps({"art":str(target),"bytes":target.stat().st_size,"riverExitY":y_exit,"sourceWaterDetected":observed}))

if __name__=="__main__":generate()

#!/usr/bin/env python3
"""SOUTH→SE road candidate V2: locally preserved terrain with narrow earth ruts.

Not a certified road or playable connection. The three approved V267 images,
V123 graph, campaign, units and saves are never written. V1's broad remote-
texture meadow replacement caused an obvious smear; this version edits only
a narrow track and keeps the existing source photograph's fine structure.
"""
from pathlib import Path
import hashlib
import json
import math
import numpy as np
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[1]
SOUTH=ROOT/"art-reviews/v267-original-source/south-unified-native-border-unapproved.webp"
BASE=ROOT/"terrain-grid/v267-countryside-original/forest-clearing-04-master.webp"
OUT=ROOT/"terrain-grid/v267-southeast-road-02"
W,H=1536,1024
# Engineering proposal ONLY; the source road is not historically researched.
PATH=[(0,578),(90,580),(210,589),(345,602),(470,613),
      (600,619),(735,609),(865,586),(1010,567),(1140,553)]

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def smooth(t):
    t=np.clip(t,0,1)
    return t*t*(3-2*t)

def make_road(base,south):
    rgb=np.asarray(base.convert("RGB")).copy()
    src=np.asarray(south.convert("RGB"))
    # A narrow corridor, not the previous 94-pixel smeared tree clearance.
    x0,x1,y0,y1=0,1190,512,674
    yy,xx=np.mgrid[y0:y1,x0:x1].astype(np.float32)
    distance=np.full(xx.shape,1e6,dtype=np.float32)
    signed=np.zeros_like(distance)
    along=np.zeros_like(distance)
    travelled=0.
    for (ax,ay),(bx,by) in zip(PATH[:-1],PATH[1:]):
        dx,dy=bx-ax,by-ay
        length=math.hypot(dx,dy)
        t=np.clip(((xx-ax)*dx+(yy-ay)*dy)/(length*length),0,1)
        lateral_x=xx-(ax+t*dx)
        lateral_y=yy-(ay+t*dy)
        d=np.hypot(lateral_x,lateral_y)
        closer=d<distance
        distance=np.where(closer,d,distance)
        signed=np.where(closer,(-dy*lateral_x+dx*lateral_y)/length,signed)
        along=np.where(closer,travelled+t*length,along)
        travelled+=length

    original=rgb[y0:y1,x0:x1].astype(np.float32)
    # Preserve every tree, rock and meadow texture pixel. Road is a color
    # treatment of the *same* pixel, not transplanted/warped remote ground.
    luminance=(original[...,0]*.30+original[...,1]*.59+original[...,2]*.11)
    # Earth tone retains native per-pixel luminance and microcontrast.
    earth=np.stack([np.clip(luminance*1.07+11,0,255),
                    np.clip(luminance*.89+6,0,255),
                    np.clip(luminance*.68+5,0,255)],axis=-1)
    # Two shallow wagon ruts and uneven grassy center, not a broad highway.
    irregular=1.8*np.sin(along*.021)+1.2*np.sin(along*.073)
    lane=np.abs(signed-irregular)
    ruts=np.exp(-.5*((lane-8.8)/3.4)**2)
    foot=np.exp(-.5*(lane/13.0)**2)
    track=smooth((20-distance)/6)*(0.22*foot+0.57*ruts)
    shoulder=smooth((29-distance)/7)*0.10
    alpha=np.clip(track+shoulder,0,.79)
    changed=original*(1-alpha[...,None])+earth*alpha[...,None]

    # Only a 9px feather at the shared border. The previous 55px import
    # distorted trees and produced the rejected dark smear. This is NOT
    # evidence of a valid ground-level road or a certified road join.
    seam_y=smooth((40-np.abs(yy-578))/14)
    seam_x=smooth((10-xx)/10)
    seam=seam_y*seam_x
    sx=np.clip(1535-xx,0,1535).astype(int)
    sampled=src[yy.astype(int),sx].astype(np.float32)
    changed=changed*(1-seam[...,None])+sampled*seam[...,None]
    rgb[y0:y1,x0:x1]=np.uint8(np.clip(changed,0,255))
    result=Image.fromarray(rgb,"RGB")
    original_uint=np.asarray(base.convert("RGB"))
    result_uint=np.asarray(result)
    modified=np.any(result_uint!=original_uint,axis=2)
    # A nonzero but bounded edit is required. No full-frame replacement.
    changed_fraction=float(modified.mean())
    assert 0.002<changed_fraction<0.065,changed_fraction
    # Edge RGB metric is descriptive ONLY; it cannot approve a seam.
    edge_mismatch=float(np.abs(src[563:594,1535].astype(float)-
                               result_uint[563:594,0].astype(float)).mean())
    # Expose whether SOUTH's apparent exit is near-black, which may indicate
    # an art-frame edge rather than ground; never silently call it a road.
    south_edge_luma=float(src[568:589,1535].mean())
    return result,dict(modifiedPixelFraction=round(changed_fraction,5),
                       edgeRGBMismatch=round(edge_mismatch,3),
                       southEdgeMeanRGB=round(south_edge_luma,2),
                       roadPhysicalContinuityVerified=False)

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    protected={str(p.relative_to(ROOT)):sha(p) for p in (SOUTH,BASE)}
    with Image.open(SOUTH) as south,Image.open(BASE) as base:
        assert south.size==base.size==(W,H)
        result,metrics=make_road(base,south)
        result.save(OUT/"southeast-02-local-ruts.webp","WEBP",quality=90,method=6)
        result.resize((768,512),Image.Resampling.LANCZOS).save(
            OUT/"southeast-02-local-ruts-mobile.webp","WEBP",quality=82,method=6)
        sheet=Image.new("RGB",(1200,650),(18,27,24))
        d=ImageDraw.Draw(sheet)
        sheet.paste(south.convert("RGB").crop((936,335,1536,935)),(0,40))
        sheet.paste(result.crop((0,335,600,935)),(600,40))
        d.text((14,14),"SOUTH original edge (unaltered)",fill="#f7dfb6")
        d.text((614,14),"NEW candidate V2 (no broad texture transplant)",fill="#f7dfb6")
        sheet.save(OUT/"southeast-02-seam-review.webp","WEBP",quality=88)
    assert all(sha(ROOT/p)==digest for p,digest in protected.items()),"Protected artwork changed"
    meta=dict(schema="coe-v267-southeast-road-v2/v1",
        image="terrain-grid/v267-southeast-road-02/southeast-02-local-ruts.webp",
        mobileImage="terrain-grid/v267-southeast-road-02/southeast-02-local-ruts-mobile.webp",
        sourceArt=list(protected),sourceSHA256=protected,
        worldOrigin=[3072,1024],worldSize=[W,H],
        southExit=[1536,578],newWestEntry=[0,578],
        proposedRoadLocal=PATH,metrics=metrics,
        visualApproval=False,physicalSeamVerified=False,
        gameplayEnabled=False,historicallyVerified=False,userApproved=False,
        nativePlayable=False,finished=False,
        note="New roaded derivative of countryside-04, not a fifth original landscape. No approved road or army route. V1 rejected; V2 uses local pixels only.")
    (OUT/"southeast-02-source.json").write_text(json.dumps(meta,indent=2)+"\n")
    print(json.dumps({"image":meta["image"],"metrics":metrics,"playable":False}))
if __name__=="__main__":
    main()

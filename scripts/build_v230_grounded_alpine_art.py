#!/usr/bin/env python3
"""V230: coherent native-source Alpine terrain with graph-locked narrow ground contact.
A source-attributed ART EXPERIMENT, not registered 1780 geography or verified roads.
No procedural texture, duplicated Matrei pixels, new roads, or new crossings.
"""
import argparse, hashlib, io, json
from pathlib import Path
import cv2
import numpy as np
import requests
from PIL import Image
from build_v229_austrian_source_art import SOURCES, ROADS, SIZE, FALSE_FLAGS, assert_immutable_roads

KIND = "UNAPPROVED_ROUTE_GROUNDED_AUSTRIAN_COMPOSITION"
NATIVE_W, NATIVE_H = SIZE

def download(info):
    response = requests.get(info["url"], timeout=90,
                            headers={"User-Agent":"CenturyOfEmpiresArtSourceAudit/0.2"})
    response.raise_for_status()
    raw = response.content
    actual = hashlib.sha256(raw).hexdigest()
    if actual != info["sourceSha256"]:
        raise ValueError("STOP: unpinned source: " + actual)
    image = Image.open(io.BytesIO(raw)).convert("RGB")
    if image.size != (6000, 4000):
        raise ValueError("STOP: unexpected source dimensions")
    return np.asarray(image)

def natural_metrics(rgb):
    small = cv2.resize(rgb, (384, 256), interpolation=cv2.INTER_AREA)
    lab = cv2.cvtColor(small, cv2.COLOR_RGB2LAB)
    luma = lab[:,:,0].astype(np.float32)
    fine = np.abs(luma - cv2.GaussianBlur(luma, (0,0), 1.5))
    hsv = cv2.cvtColor(small, cv2.COLOR_RGB2HSV)
    h,s,v = [hsv[:,:,i] for i in range(3)]
    green = ((h>=25)&(h<=93)&(s>=30)&(v>=28)&(v<=230))
    sky = ((h>=92)&(h<=140)&(s>=35)&(v>=115))
    roofs = (((h<16)|(h>173))&(s>=100)&(v>=90))
    bright = ((s<26)&(v>235))
    return dict(fine=float(np.mean(fine)), area=float(np.mean(fine>9)),
                green=float(np.mean(green)), sky=float(np.mean(sky)),
                roof=float(np.mean(roofs)), bright=float(np.mean(bright)))

def choose_native_crop(original, cell):
    # Evaluate complete, contiguous, NON-REPEATED native-pixel source windows.
    # Sky/roof penalties are conservative heuristics, not semantic verification.
    small = cv2.resize(original, (1500,1000), interpolation=cv2.INTER_AREA)
    candidates = []
    for y in range(0,4000-NATIVE_H+1,248):
        for x in range(0,6000-NATIVE_W+1,372):
            p = small[y//4:(y+NATIVE_H)//4, x//4:(x+NATIVE_W)//4]
            if p.shape[:2] != (256,384): continue
            m = natural_metrics(p)
            # Both cells need rocks, varied conifers, and non-flat fine detail.
            # Different weights favor rugged WEST vs meadow/forest SOUTH.
            green_target = .42 if cell=="west" else .53
            score = (m["fine"]*1.8 + m["area"]*19
                     - abs(m["green"]-green_target)*12
                     - m["sky"]*40 - m["roof"]*28 - m["bright"]*15)
            candidates.append((score,x,y,m))
    if not candidates: raise ValueError("No contiguous native crop candidates")
    score,x,y,m = max(candidates,key=lambda z:z[0])
    return original[y:y+NATIVE_H,x:x+NATIVE_W].copy(),[x,y,x+NATIVE_W,y+NATIVE_H],round(score,3),m

def choose_meadow_strip(original, crop):
    # A SINGLE contiguous source-ground strip: monotonic sampling along the
    # unchanged V123 road, no looping/repeated tree/river/building motifs.
    best = None
    for y in range(100,4000-112,220):
        for x in range(0,6000-1536,384):
            strip = original[y:y+112,x:x+1536]
            s = cv2.resize(strip,(384,56),interpolation=cv2.INTER_AREA)
            hsv=cv2.cvtColor(s,cv2.COLOR_RGB2HSV)
            h, sat, v = [hsv[:,:,i] for i in range(3)]
            meadow=((h>=25)&(h<=88)&(sat>=28)&(v>=45)&(v<=225))
            sky=((h>=93)&(h<=140)&(sat>35)&(v>120))
            fine=cv2.cvtColor(s,cv2.COLOR_RGB2GRAY).astype(np.float32)
            fine=np.abs(fine-cv2.GaussianBlur(fine,(0,0),1.3))
            score=float(np.mean(meadow))*20 + float(np.mean(fine))*0.8 - float(np.mean(sky))*45
            if best is None or score>best[0]:best=(score,x,y)
    _,x,y=best
    return original[y:y+112,x:x+1536].copy(),[x,y,x+1536,y+112]

def ground_contact(scene, meadow, points):
    """Ground the existing 22px V194 cartway in real source grass/soil, not a highway.
    A 14px core fades to original terrain by 37px. The V123 line never moves.
    No bridge banks, new roads or routes are generated.
    """
    h,w=scene.shape[:2]
    yy,xx=np.mgrid[0:h,0:w].astype(np.float32)
    nearest=np.full((h,w),1e8,np.float32)
    arc=np.zeros((h,w),np.float32)
    signed=np.zeros((h,w),np.float32)
    pts=np.asarray(points,np.float32)
    lengths=np.linalg.norm(pts[1:]-pts[:-1],axis=1)
    cumulative=np.concatenate(([0.],np.cumsum(lengths)))
    for i,(a,b) in enumerate(zip(pts[:-1],pts[1:])):
        vec=b-a
        len2=float(vec@vec)
        if len2<1:continue
        left=max(0,int(min(a[0],b[0])-42));right=min(w,int(max(a[0],b[0])+43))
        top=max(0,int(min(a[1],b[1])-42));bottom=min(h,int(max(a[1],b[1])+43))
        if left>=right or top>=bottom:continue
        px=xx[top:bottom,left:right]-a[0]
        py=yy[top:bottom,left:right]-a[1]
        t=np.clip((px*vec[0]+py*vec[1])/len2,0,1)
        dx=px-t*vec[0];dy=py-t*vec[1]
        d=np.sqrt(dx*dx+dy*dy)
        region=nearest[top:bottom,left:right]
        keep=d<region
        region[keep]=d[keep]
        arc[top:bottom,left:right][keep]=(cumulative[i]+t*lengths[i])[keep]
        signed[top:bottom,left:right][keep]=((px*vec[1]-py*vec[0])/np.sqrt(len2))[keep]
    # Source-ground is sampled ONCE, in order, from a full native-resolution
    # 1536px meadow strip; no repeated motif or procedural pixel noise.
    src_x=(arc/max(1.,float(cumulative[-1])))*(meadow.shape[1]-1)
    src_y=np.clip(56+signed*.76,0,meadow.shape[0]-1)
    sampled=cv2.remap(meadow,src_x,src_y,cv2.INTER_LINEAR,
                      borderMode=cv2.BORDER_REFLECT)
    edge=np.clip((37-nearest)/23,0,1)
    alpha=edge*edge*(3-2*edge)
    result=(scene.astype(np.float32)*(1-alpha[:,:,None])+
            sampled.astype(np.float32)*alpha[:,:,None])
    return np.uint8(np.clip(result,0,255))

def build(output):
    assert_immutable_roads()
    output.mkdir(parents=True,exist_ok=True)
    sources={}
    for cell,info in SOURCES.items():
        original=download(info)
        scene,crop,score,metrics=choose_native_crop(original,cell)
        meadow,strip=choose_meadow_strip(original,crop)
        prepared=ground_contact(scene,meadow,ROADS[cell])
        name=cell+"-austrian-natural-cover-v230.webp"
        target=output/name
        Image.fromarray(prepared).save(target,"WEBP",quality=91,method=6)
        data=target.read_bytes()
        sources[cell]=dict(info,file=name,nativePixels=list(SIZE),
            sourceImagePixels=[6000,4000],outputSha256=hashlib.sha256(data).hexdigest(),
            outputBytes=len(data),license="CC BY-SA 4.0",
            licenseUrl="https://creativecommons.org/licenses/by-sa/4.0/",
            sourcePage="https://commons.wikimedia.org/wiki/File:"+info["title"].replace(" ","_"),
            crop=crop,sourceCropScore=score,sourceCropMetrics=metrics,
            nonrepeatingGroundStrip=strip,
            modifications="Distinct native-pixel source crop, contiguous source-meadow road clearance 14px core/37px feather on unchanged V123 route; not surveyed",
            **FALSE_FLAGS)
    if sources["west"]["sourceSha256"]==sources["south"]["sourceSha256"]:
        raise ValueError("duplicate source")
    manifest=dict(version=230,kind=KIND,sourceRegion="Matrei in Osttirol, Austria",
        license="CC BY-SA 4.0",notHistorical1780Geography=True,
        cartwaysAndBridgeBanksNotSurveyed=True,
        sourceRegisteredToV123=False,sourceLandmarkTiepointsVerified=False,
        selectionIsSemanticVerification=False,
        sources=sources,**{k:v for k,v in FALSE_FLAGS.items() if k!="sourceRegisteredToV123"})
    (output/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print(json.dumps({c:{"crop":s["crop"],"fine":s["sourceCropMetrics"]["fine"],
        "groundStrip":s["nonrepeatingGroundStrip"],"sha256":s["outputSha256"]}
        for c,s in sources.items()},indent=2))
    return manifest

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",type=Path,default=Path("terrain-v230/assets"))
    build(parser.parse_args().output)

#!/usr/bin/env python3
"""V240: fail-closed visible cartway-to-immutable V123 registration.

The visible road must be independently traced on original image pixels.
Geometry and earth-color checks are necessary only: not 1780 history,
geographic registration, bank verification or human art approval.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import cv2
import numpy as np
from PIL import Image, ImageDraw

SIZE=(1536,1024)
V123_BLOB="09f04b4062e24fbacbb645307462cdddce2b2aa3"
MAX_P95=9.0
MAX_ENDPOINT=14.0
MIN_EARTH_FRACTION=.68
MAX_GAP_PX=50.0

def sample(points,step=4):
    out=[]
    for a,b in zip(points[:-1],points[1:]):
        a=np.asarray(a,float);b=np.asarray(b,float)
        n=max(1,int(np.ceil(np.linalg.norm(b-a)/step)))
        out.extend([a+(b-a)*i/n for i in range(n)])
    out.append(np.asarray(points[-1],float))
    return np.asarray(out,float)

def nearest_dist(a,b):
    return np.sqrt(np.min(((a[:,None,:]-b[None,:,:])**2).sum(axis=2),axis=1))

def geometry(immutable,trace):
    a,b=sample(immutable),sample(trace)
    if len(a)<3 or len(b)<3:raise ValueError("Insufficient visible road trace")
    da,db=nearest_dist(a,b),nearest_dist(b,a)
    endpoints=min(max(np.linalg.norm(a[0]-b[0]),np.linalg.norm(a[-1]-b[-1])),
                  max(np.linalg.norm(a[0]-b[-1]),np.linalg.norm(a[-1]-b[0])))
    p95=float(np.percentile(np.r_[da,db],95))
    return {"p95MisalignmentPx":round(p95,2),
            "maxMisalignmentPx":round(float(max(da.max(),db.max())),2),
            "endpointErrorPx":round(float(endpoints),2),
            "geometryPass":bool(p95<=MAX_P95 and endpoints<=MAX_ENDPOINT)}

def earth_evidence(image,trace):
    rgb=np.asarray(image.convert("RGB"))
    hsv=cv2.cvtColor(rgb,cv2.COLOR_RGB2HSV)
    h,s,v=cv2.split(hsv)
    earth=(h>=5)&(h<=30)&(s>=40)&(v>=40)&(v<=235)
    pts=sample(trace,step=4)
    values=[];run=longest=0
    for x,y in pts:
        xi,yi=int(round(x)),int(round(y))
        x0,x1=max(0,xi-4),min(SIZE[0],xi+5)
        y0,y1=max(0,yi-4),min(SIZE[1],yi+5)
        ok=x0<x1 and y0<y1 and float(earth[y0:y1,x0:x1].mean())>=.45
        values.append(ok)
        run=0 if ok else run+4
        longest=max(longest,run)
    return {"earthRouteFraction":round(float(np.mean(values)),5),
            "longestNoEarthRunPx":longest,
            "visibleEarthPass":bool(np.mean(values)>=MIN_EARTH_FRACTION and longest<=MAX_GAP_PX)}

def verify(image,source_bytes,manifest,immutable):
    if image.size!=SIZE:raise ValueError("Native image size mismatch")
    if hashlib.sha256(source_bytes).hexdigest()!=manifest.get("sourceSha256"):
        raise ValueError("Source-image SHA256 mismatch")
    if manifest.get("annotationMethod")!="human-visible-road-trace":
        raise ValueError("Visible-road annotation required, not graph-derived coordinates")
    trace=manifest.get("visibleRoadPoints")
    if not isinstance(trace,list) or len(trace)<3 or any(len(p)!=2 for p in trace):
        raise ValueError("Invalid independent visible-road trace")
    if any(not(0<=p[0]<=SIZE[0] and 0<=p[1]<=SIZE[1]) for p in trace):
        raise ValueError("Trace leaves native image")
    g=geometry(immutable,trace);e=earth_evidence(image,trace)
    return {**g,**e,"necessaryVisibleCartwayGate":bool(g["geometryPass"] and e["visibleEarthPass"]),
            "annotationIndependentVerified":False,
            "sourceRegisteredToV123":False,"historicalRoadsVerified":False,
            "bridgeBanksVerified":False,"humanVisualApproval":False,
            "physicalIPhoneApproved":False,"productionApproved":False}

def render_review(image,immutable,trace):
    review=image.convert("RGBA")
    over=Image.new("RGBA",SIZE,(0,0,0,0));d=ImageDraw.Draw(over)
    d.line([tuple(p) for p in immutable],fill=(255,65,65,195),width=4)
    d.line([tuple(p) for p in trace],fill=(50,225,235,185),width=3)
    for p in (immutable[0],immutable[-1]):
        d.ellipse((p[0]-6,p[1]-6,p[0]+6,p[1]+6),outline=(255,65,65,255),width=2)
    return Image.alpha_composite(review,over).convert("RGB")

def load_immutable(atlas,tile):
    raw=Path(atlas).read_bytes()
    blob=hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
    if blob!=V123_BLOB:raise ValueError("Immutable V123 Git blob changed")
    match=re.search(r"const\s+"+tile+r"Road\s*=\s*(\[.*?\]);",raw.decode(),re.S)
    if not match:raise ValueError("Immutable V123 road missing")
    return json.loads(match.group(1))

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--image",type=Path,required=True)
    p.add_argument("--trace",type=Path,required=True)
    p.add_argument("--atlas",type=Path,required=True)
    p.add_argument("--tile",choices=["west","south"],required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    immutable=load_immutable(a.atlas,a.tile)
    raw=a.image.read_bytes();image=Image.open(a.image).convert("RGB")
    manifest=json.loads(a.trace.read_text())
    result=verify(image,raw,manifest,immutable)
    a.output.mkdir(parents=True,exist_ok=True)
    render_review(image,immutable,manifest["visibleRoadPoints"]).save(
        a.output/(a.tile+"-trace-review.jpg"),quality=91)
    (a.output/"report.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
    if not result["necessaryVisibleCartwayGate"]:
        raise SystemExit("ART RED: visible cartway does not register to V123")

if __name__=="__main__":main()

#!/usr/bin/env python3
"""V255: paired ORIGINAL-image road anchors, never verified 1780 geography or approved art.

Unlike V254's normalized-arclength Gaussian warp, this keeps independently
observed (but NOT geographically verified) source-image road vertices paired
with immutable V123 vertices and moves the EXISTING pixels with the ground.
"""
import argparse
import hashlib
import json
from pathlib import Path

import cv2
import numpy as np
from scipy.spatial import cKDTree

NATIVE=(1024,1536)
V123_SHA="09f04b4062e24fbacbb645307462cdddce2b2aa3"
PINS={
 "west":"7326e88c778ed4a0018c241156e701690e95deb1feeb8fa13a298c0f0c74505e",
 "south":"034246c5d9471cd6d87673daa48fb1a014dab38d414626677f6148ce8c7d08f3",
}
# Manual observations of road pixels in two ORIGINAL FICTIONAL images. These are
# NOT historical, natural geographic, or independently verified V209 tiepoints.
SOURCE={
 "west":[[275,427],[370,420],[470,422],[570,419],[680,413],[784,402],
         [890,392],[980,385],[1085,375],[1210,370],[1320,360],[1450,350],[1536,341]],
 "south":[[449,0],[451,74],[475,160],[500,235],[545,310],[610,350],
          [682,427],[755,507],[865,561],[1010,597],[1120,615],[1244,625]],
}
# Copied exactly from immutable V123, WEST reversed to pair with source orientation.
TARGET={
 "west":[[275,550],[370,522],[470,520],[570,540],[680,560],[784,551],
         [890,535],[980,515],[1085,507],[1210,490],[1320,480],[1450,478],[1536,478]],
 "south":[[466,0],[466,74],[470,160],[488,235],[540,310],[620,350],
          [700,400],[805,442],[930,510],[1050,550],[1140,585],[1270,605]],
}

def paired_samples(src,dst,spacing=1.5):
 a=np.asarray(src,dtype=np.float32);b=np.asarray(dst,dtype=np.float32)
 if a.shape!=b.shape or a.ndim!=2 or a.shape[1]!=2 or len(a)<2:
  raise ValueError("anchors must correspond one-to-one")
 if not np.isfinite(a).all() or not np.isfinite(b).all():
  raise ValueError("invalid anchor")
 if np.any(np.linalg.norm(np.diff(a,axis=0),axis=1)<1) or np.any(np.linalg.norm(np.diff(b,axis=0),axis=1)<1):
  raise ValueError("degenerate segment")
 aa=[];bb=[]
 for i in range(len(a)-1):
  n=max(2,int(np.ceil(max(np.linalg.norm(a[i+1]-a[i]),np.linalg.norm(b[i+1]-b[i]))/spacing)))
  t=np.linspace(0,1,n,endpoint=False,dtype=np.float32)[:,None]
  aa.append(a[i]*(1-t)+a[i+1]*t)
  bb.append(b[i]*(1-t)+b[i+1]*t)
 return np.vstack([*aa,a[-1:]]),np.vstack([*bb,b[-1:]])

def mapping(src,dst,sigma=170,spacing=1.5):
 a,b=paired_samples(src,dst,spacing)
 h,w=NATIVE
 yy,xx=np.indices((h,w),dtype=np.float32)
 pixels=np.column_stack((xx.ravel(),yy.ravel()))
 dist,idx=cKDTree(b).query(pixels,k=1,workers=-1)
 weight=np.exp(-0.5*(dist/sigma)**2).astype(np.float32)
 shift=(a[idx]-b[idx])*weight[:,None]
 return (xx.ravel()+shift[:,0]).reshape(h,w),(yy.ravel()+shift[:,1]).reshape(h,w)

def evaluate(mapx,mapy,src,dst):
 h,w=mapx.shape
 observed=(mapx>=0)&(mapx<=w-1)&(mapy>=0)&(mapy<=h-1)
 step=8
 gx=np.gradient(mapx[::step,::step]);gy=np.gradient(mapy[::step,::step])
 jac=(gx[1]*gy[0]-gx[0]*gy[1])/(step*step)
 s=np.asarray(src,dtype=float);d=np.asarray(dst,dtype=float)
 errors=[]
 for p,q in zip(d,s):
  x=int(np.clip(round(p[0]),0,w-1));y=int(np.clip(round(p[1]),0,h-1))
  errors.append(float(np.linalg.norm([mapx[y,x]-q[0],mapy[y,x]-q[1]])))
 displacement=float(np.linalg.norm(s-d,axis=1).max())
 return {
  "maxAnchorRemapErrorPx":round(max(errors),3),
  "meanAnchorRemapErrorPx":round(float(np.mean(errors)),3),
  "minSampledJacobian":round(float(jac.min()),4),
  "foldedFraction":round(float(np.mean(jac<=0)),6),
  "sourcePixelCoverage":round(float(np.mean(observed)),6),
  "maxPairedAnchorDisplacementPx":round(displacement,2),
  "necessaryGeometryPass":bool(max(errors)<=2 and jac.min()>=.24 and observed.mean()>=.997 and displacement<=155),
 }

def process(tile,path,out,atlas):
 raw=Path(atlas).read_bytes()
 blob=hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
 if blob!=V123_SHA:raise ValueError("immutable V123 atlas SHA changed")
 if hashlib.sha256(Path(path).read_bytes()).hexdigest()!=PINS[tile]:
  raise ValueError("wrong original source SHA256")
 img=cv2.imread(str(path),cv2.IMREAD_COLOR)
 if img is None or img.shape[:2]!=NATIVE:raise ValueError("wrong original dimensions")
 mx,my=mapping(SOURCE[tile],TARGET[tile])
 qa=evaluate(mx,my,SOURCE[tile],TARGET[tile])
 result=cv2.remap(img,mx,my,cv2.INTER_CUBIC,borderMode=cv2.BORDER_REFLECT_101)
 out=Path(out);out.mkdir(parents=True,exist_ok=True)
 cv2.imwrite(str(out/(tile+"-anchored-UNAPPROVED.webp")),result,[cv2.IMWRITE_WEBP_QUALITY,90])
 over=result.copy()
 cv2.polylines(over,[np.asarray(TARGET[tile],np.int32)],False,(20,20,255),3,cv2.LINE_AA)
 cv2.imwrite(str(out/(tile+"-physical-road-contact-UNAPPROVED.jpg")),over,[cv2.IMWRITE_JPEG_QUALITY,93])
 qa.update({
  "tile":tile,"originalSha256":PINS[tile],
  "sourceTraceIsIndependentGeographicEvidence":False,"historicRoadVerified":False,
  "naturalTiepointsVerified":False,"bridgeBanksVerified":False,
  "strictV203Passed":False,"fourBrowserArtPassed":False,
  "humanArtApproved":False,"productionApproved":False,
 })
 return qa

if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--west",required=True);p.add_argument("--south",required=True)
 p.add_argument("--atlas",default="terrain-grid/v123-atlas.js");p.add_argument("--out",required=True)
 args=p.parse_args();r={"version":255,"tiles":{}}
 for tile in ("west","south"):
  r["tiles"][tile]=process(tile,getattr(args,tile),args.out,args.atlas)
 Path(args.out,"report.json").write_text(json.dumps(r,indent=2)+"\n")
 print(json.dumps(r,indent=2))

#!/usr/bin/env python3
"""V259: correct SOUTH fictional cartway source pixels, NOT historical geography."""
import argparse, hashlib, json
from pathlib import Path
import cv2
import numpy as np
from scipy.interpolate import RBFInterpolator
from scipy.spatial import cKDTree
ROOT=Path(__file__).resolve().parents[1]
ATLAS_SHA="09f04b4062e24fbacbb645307462cdddce2b2aa3"
INPUT_SHA="f817dc0370652e674e175e0e08db7b285a491b2f0f680a37c5f4f106da7251b6"
TARGET=np.asarray([[466,0],[466,74],[470,160],[488,235],[540,310],[620,350],[700,400],[805,442],[930,510],[1050,550],[1140,585],[1200,596],[1270,605]],dtype=float)
# Sighted on actual lossless V258 SOUTH pixels; NOT independent V209 tiepoints.
SOURCE=np.asarray([[461,0],[465,74],[477,160],[502,235],[548,316],[620,366],[700,423],[805,469],[930,532],[1050,566],[1140,593],[1200,609],[1245,622]],dtype=float)
def verify_atlas(path):
    data=Path(path).read_bytes()
    sha=hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()
    if sha!=ATLAS_SHA:raise ValueError("Immutable V123 road/bridge atlas changed")
def remap(image):
    h,w=image.shape[:2]
    if (w,h)!=(1536,1024):raise ValueError("Expected native 1536x1024 pixels")
    boundary=[]
    for x in (0,256,512,768,1024,1280,1535):boundary.extend(([x,0],[x,1023]))
    for y in (256,512,768):boundary.extend(([0,y],[1535,y]))
    boundary=np.asarray(boundary,dtype=float)
    far=boundary[np.min(np.linalg.norm(boundary[:,None,:]-TARGET[None,:,:],axis=2),axis=1)>80]
    rbf=RBFInterpolator(np.vstack((TARGET,far)),np.vstack((SOURCE-TARGET,np.zeros_like(far))),kernel="thin_plate_spline",smoothing=6.0)
    dense=[]
    for a,b in zip(TARGET[:-1],TARGET[1:]):
        dense.extend(np.linspace(a,b,max(2,int(np.linalg.norm(b-a)/3)+1)))
    road_tree=cKDTree(np.asarray(dense))
    mapx=np.empty((h,w),np.float32);mapy=np.empty((h,w),np.float32)
    xs=np.arange(w,dtype=float)
    for y0 in range(0,h,64):
        ys=np.arange(y0,min(y0+64,h),dtype=float);xx,yy=np.meshgrid(xs,ys)
        pts=np.stack((xx.ravel(),yy.ravel()),axis=1)
        delta=rbf(pts)
        dist=road_tree.query(pts,workers=-1)[0]
        delta*=np.exp(-.5*(dist/110)**2)[:,None]
        mapx[y0:y0+len(ys)]=(pts[:,0]+delta[:,0]).reshape(len(ys),w)
        mapy[y0:y0+len(ys)]=(pts[:,1]+delta[:,1]).reshape(len(ys),w)
    result=cv2.remap(image,mapx,mapy,cv2.INTER_CUBIC,borderMode=cv2.BORDER_REFLECT_101)
    step=8;gx=np.gradient(mapx[::step,::step]);gy=np.gradient(mapy[::step,::step])
    jac=(gx[1]*gy[0]-gx[0]*gy[1])/(step*step)
    coverage=np.mean((mapx>=0)&(mapx<w)&(mapy>=0)&(mapy<h))
    displacement=np.hypot(mapx-np.arange(w)[None,:],mapy-np.arange(h)[:,None])
    qa={"minSampledJacobian":round(float(jac.min()),4),"foldedFraction":round(float(np.mean(jac<=0)),6),"sourcePixelCoverage":round(float(coverage),6),"maxAdditionalDisplacementPx":round(float(displacement.max()),3),"manualFictionalRoadTrace":True,"historicalRoadVerified":False,"independentGeographicTiepointsVerified":False,"bridgeBanksVerified":False,"strictV203Passed":False,"fourBrowserArtPassed":False,"userVisualApproval":False,"productionApproved":False}
    qa["necessaryGeometryPass"]=bool(jac.min()>=.5 and not np.any(jac<=0) and coverage>=.998 and displacement.max()<=40)
    return result,qa
def main():
    p=argparse.ArgumentParser();p.add_argument("--south",required=True);p.add_argument("--out",required=True);p.add_argument("--atlas",default=str(ROOT/"terrain-grid/v123-atlas.js"))
    a=p.parse_args();verify_atlas(a.atlas);raw=Path(a.south).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=INPUT_SHA:raise ValueError("Lossless V258 SOUTH SHA256 mismatch")
    source=cv2.imdecode(np.frombuffer(raw,np.uint8),cv2.IMREAD_COLOR)
    corrected,qa=remap(source);out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    path=out/"south-v259-UNAPPROVED.png"
    if not cv2.imwrite(str(path),corrected,[cv2.IMWRITE_PNG_COMPRESSION,3]):raise RuntimeError("Image write failed")
    qa["inputV258Sha256"]=INPUT_SHA;qa["outputV259Sha256"]=hashlib.sha256(path.read_bytes()).hexdigest()
    (out/"report.json").write_text(json.dumps(qa,indent=2)+"\n")
    print(json.dumps(qa,indent=2))
    if not qa["necessaryGeometryPass"]:raise SystemExit("V259 geometry REJECTED")
if __name__=="__main__":main()

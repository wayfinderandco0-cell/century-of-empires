#!/usr/bin/env python3
"""V260: one original-source color resample for fictional SOUTH; ART RED.

Compose V258 original-image mapping and V259 physical-cartway correction in
coordinate space, then sample the lossless original image ONCE. No synthetic
detail, roads, route-graph edits, or historical-geography claims.
"""
from pathlib import Path
import argparse, hashlib, json
import cv2
import numpy as np
from scipy.interpolate import RBFInterpolator
from scipy.spatial import cKDTree
from v258_south_road_recontact import TRACE, target_at_source_progress, mapping, PINS

NATIVE_SIZE=(1536,1024)
TARGET_V259=np.asarray([[466,0],[466,74],[470,160],[488,235],[540,310],
 [620,350],[700,400],[805,442],[930,510],[1050,550],
 [1140,585],[1200,596],[1270,605]],dtype=np.float64)
SOURCE_V259=np.asarray([[461,0],[465,74],[477,160],[502,235],[548,316],
 [620,366],[700,423],[805,469],[930,532],[1050,566],
 [1140,593],[1200,609],[1245,622]],dtype=np.float64)

def correction_maps(width=1536,height=1024):
    assert (width,height)==NATIVE_SIZE
    boundary=[]
    for x in (0,256,512,768,1024,1280,1535):boundary.extend([[x,0],[x,1023]])
    for y in (256,512,768):boundary.extend([[0,y],[1535,y]])
    boundary=np.asarray(boundary,dtype=np.float64)
    keep=boundary[np.min(np.linalg.norm(boundary[:,None,:]-TARGET_V259[None,:,:],axis=2),axis=1)>80]
    anchors=np.vstack((TARGET_V259,keep))
    shifts=np.vstack((SOURCE_V259-TARGET_V259,np.zeros_like(keep)))
    rbf=RBFInterpolator(anchors,shifts,kernel='thin_plate_spline',smoothing=6.0)
    dense=[]
    for a,b in zip(TARGET_V259[:-1],TARGET_V259[1:]):
        dense.extend(np.linspace(a,b,max(2,int(np.linalg.norm(b-a)/3)+1)))
    tree=cKDTree(np.asarray(dense))
    mapx=np.empty((height,width),np.float32)
    mapy=np.empty((height,width),np.float32)
    xs=np.arange(width,dtype=np.float64)
    for y0 in range(0,height,64):
        ys=np.arange(y0,min(y0+64,height),dtype=np.float64)
        xx,yy=np.meshgrid(xs,ys)
        pts=np.stack((xx.ravel(),yy.ravel()),axis=1)
        disp=rbf(pts)
        distances=tree.query(pts,workers=-1)[0]
        disp*=np.exp(-.5*(distances/110)**2)[:,None]
        mapx[y0:y0+len(ys)]=(pts[:,0]+disp[:,0]).reshape(len(ys),width).astype(np.float32)
        mapy[y0:y0+len(ys)]=(pts[:,1]+disp[:,1]).reshape(len(ys),width).astype(np.float32)
    return mapx,mapy

def compose_maps(base_x,base_y,corr_x,corr_y):
    """Map final image pixels directly to ORIGINAL native source coordinates."""
    assert base_x.shape==base_y.shape==corr_x.shape==corr_y.shape==(1024,1536)
    mx=cv2.remap(base_x,corr_x,corr_y,cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT_101)
    my=cv2.remap(base_y,corr_x,corr_y,cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT_101)
    return mx,my

def quality_report(mx,my):
    h,w=mx.shape;step=8
    gx=np.gradient(mx[::step,::step]);gy=np.gradient(my[::step,::step])
    jac=(gx[1]*gy[0]-gx[0]*gy[1])/(step*step)
    coverage=float(np.mean((mx>=0)&(mx<w)&(my>=0)&(my<h)))
    return {'minSampledJacobian':round(float(jac.min()),4),
      'sampledFoldedFraction':float(np.mean(jac<=0)),
      'nativeSourceCoverage':round(coverage,6),
      'noSyntheticDetailOrRoads':True,'historicalRoadVerified':False,
      'independentGeographicTiepointsVerified':False,'bridgeBanksVerified':False,
      'strictV203Passed':False,'exactArtFourBrowserPassed':False,
      'userApproved':False,'productionApproved':False}

def render(source):
    raw=Path(source).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=PINS['south']:
        raise ValueError('original SOUTH source SHA mismatch')
    image=cv2.imdecode(np.frombuffer(raw,np.uint8),cv2.IMREAD_COLOR)
    if image is None or image.shape[:2]!=(1024,1536):
        raise ValueError('source dimensions changed')
    dest=target_at_source_progress('south',TRACE['south'])
    bx,by,*_=mapping(TRACE['south'],dest,sigma=170,spacing=1.25)
    cx,cy=correction_maps()
    mx,my=compose_maps(bx,by,cx,cy)
    out=cv2.remap(image,mx,my,cv2.INTER_CUBIC,borderMode=cv2.BORDER_REFLECT_101)
    return out,quality_report(mx,my),((bx,by),(cx,cy),(mx,my))

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--south',required=True)
    p.add_argument('--out',required=True)
    args=p.parse_args();out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    result,report,_=render(args.south)
    path=out/'south-v260-single-pass-UNAPPROVED.png'
    if not cv2.imwrite(str(path),result,[cv2.IMWRITE_PNG_COMPRESSION,3]):
        raise RuntimeError('write failed')
    report.update({'version':260,'originalSourceSHA256':PINS['south'],
       'outputSHA256':hashlib.sha256(path.read_bytes()).hexdigest(),
       'singleResampleFromOriginal':True})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    assert report['sampledFoldedFraction']==0 and report['minSampledJacobian']>.24
    assert report['nativeSourceCoverage']>.997
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()

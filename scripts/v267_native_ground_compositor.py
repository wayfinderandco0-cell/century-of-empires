#!/usr/bin/env python3
"""Native oblique photographic terrain compositor; isolated unapproved V267 studies.

Keeps real photographed trees and ground. No invented roads, historic claims,
geometry warping, or edits to approved WEST/MATREI/SOUTH artwork.
"""
from __future__ import annotations
import numpy as np
import cv2
from PIL import Image
W,H=1536,1024

def ground_window(photo,focus=(.5,.6)):
    im=photo.convert("RGB")
    w,h=im.size
    if w<W or h<H:
        k=max(W/w,H/h)
        im=im.resize((int(np.ceil(w*k)),int(np.ceil(h*k))),Image.Resampling.LANCZOS)
        w,h=im.size
    x=int(np.clip((w-W)*focus[0],0,w-W))
    y=int(np.clip((h-H)*max(.94,focus[1]),0,h-H))
    crop=(x,y,x+W,y+H)
    return im.crop(crop),list(crop)

def smooth(t):
    t=np.clip(t,0,1)
    return t*t*(3-2*t)

def multiband(a,b,alpha,levels=5):
    a=a.astype(np.float32)/255
    b=b.astype(np.float32)/255
    ga=[a];gb=[b];gm=[alpha.astype(np.float32)]
    for _ in range(levels):
        ga.append(cv2.pyrDown(ga[-1]))
        gb.append(cv2.pyrDown(gb[-1]))
        gm.append(cv2.pyrDown(gm[-1]))
    la=[];lb=[]
    for i in range(levels):
        size=(ga[i].shape[1],ga[i].shape[0])
        la.append(ga[i]-cv2.pyrUp(ga[i+1],dstsize=size))
        lb.append(gb[i]-cv2.pyrUp(gb[i+1],dstsize=size))
    la.append(ga[-1]);lb.append(gb[-1])
    layers=[la[i]*(1-gm[i][...,None])+lb[i]*gm[i][...,None] for i in range(levels+1)]
    out=layers[-1]
    for i in range(levels-1,-1,-1):
        out=cv2.pyrUp(out,dstsize=(layers[i].shape[1],layers[i].shape[0]))+layers[i]
    return np.uint8(np.clip(out*255,0,255))

def seam_path(primary,donor):
    """Minimum-error photographed ground join; NOT a physical tile/road seam."""
    scale=4
    p=cv2.resize(primary,(W//scale,H//scale),interpolation=cv2.INTER_AREA)
    q=cv2.resize(donor,(W//scale,H//scale),interpolation=cv2.INTER_AREA)
    a=cv2.cvtColor(p,cv2.COLOR_RGB2LAB).astype(np.float32)
    b=cv2.cvtColor(q,cv2.COLOR_RGB2LAB).astype(np.float32)
    low,high=166,222
    diff=np.mean(np.abs(a[low:high]-b[low:high]),axis=2)
    ga=cv2.cvtColor(p,cv2.COLOR_RGB2GRAY)
    gb=cv2.cvtColor(q,cv2.COLOR_RGB2GRAY)
    ea=np.abs(cv2.Sobel(ga,cv2.CV_32F,1,0,ksize=3))+np.abs(cv2.Sobel(ga,cv2.CV_32F,0,1,ksize=3))
    eb=np.abs(cv2.Sobel(gb,cv2.CV_32F,1,0,ksize=3))+np.abs(cv2.Sobel(gb,cv2.CV_32F,0,1,ksize=3))
    costs=diff+.05*(ea[low:high]+eb[low:high])
    ys=np.arange(low,high,dtype=np.float32)
    costs+=.012*(ys[:,None]-194)**2
    rows,cols=costs.shape
    dp=costs[:,0].copy()
    parents=np.zeros((cols,rows),np.int16)
    offsets=np.arange(-1,2)
    for x in range(1,cols):
        candidates=np.stack([np.roll(dp,int(d))+abs(d)*.8 for d in offsets],axis=0)
        candidates[0,0]=1e9
        candidates[2,-1]=1e9
        pick=np.argmin(candidates,axis=0)
        parents[x]=np.arange(rows)-offsets[pick]
        dp=costs[:,x]+candidates[pick,np.arange(rows)]
    path=np.empty(cols,np.int32)
    path[-1]=np.argmin(dp)
    for x in range(cols-1,0,-1):
        path[x-1]=parents[x,path[x]]
    native=np.interp(np.arange(W),np.arange(cols)*scale,(path+low)*scale)
    return np.clip(native,640,905).astype(np.float32)

def compose(primary,secondary):
    a=np.asarray(primary.convert("RGB"),np.uint8)
    b=np.asarray(secondary.convert("RGB"),np.uint8)
    if a.shape!=(H,W,3) or b.shape!=a.shape:
        raise ValueError("Expected 1536x1024 native photographs")
    al=cv2.cvtColor(a,cv2.COLOR_RGB2LAB).astype(np.float32)
    bl=cv2.cvtColor(b,cv2.COLOR_RGB2LAB).astype(np.float32)
    delta=np.median(al[670:900].reshape(-1,3),axis=0)-np.median(bl[670:900].reshape(-1,3),axis=0)
    delta=np.clip(delta,[-18,-7,-7],[18,7,7])
    b=cv2.cvtColor(np.uint8(np.clip(bl+delta[None,None,:]*.65,0,255)),cv2.COLOR_LAB2RGB)
    path=seam_path(a,b)
    yy=np.arange(H,dtype=np.float32)[:,None]
    alpha=smooth((yy-path[None,:]+44)/88)
    out=multiband(a,b,alpha)
    return Image.fromarray(out,"RGB"),{
        "method":"native oblique ground crop; LAB material match; minimum-error terrain seam; five-level multiband photographic blend",
        "seamYRange":[round(float(path.min()),1),round(float(path.max()),1)],
        "treeGeometryWarped":False,"roadsAdded":0,"historicalRoadsVerified":0,
        "physicalTileEdgesVerified":False
    }

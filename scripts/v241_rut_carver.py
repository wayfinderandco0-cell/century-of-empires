#!/usr/bin/env python3
"""V241 isolated two-rut roadbed study, not source or historical validation.

The original V123 graph is Git-blob pinned. This leaves the center grassy and
works only in narrow wheel ruts instead of V238's continuous brown strip.
A realistic-looking road is not historical or visual approval.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path
import cv2
import numpy as np
from PIL import Image

SIZE=(1536,1024)
V123_BLOB='09f04b4062e24fbacbb645307462cdddce2b2aa3'

def read_roads(atlas):
    raw=Path(atlas).read_bytes()
    blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
    if blob!=V123_BLOB: raise ValueError('V123 immutable graph drift')
    s=raw.decode('utf-8')
    return {tile:json.loads(re.search(r'const\s+'+tile+r'Road\s*=\s*(\[.*?\]);',s,re.S).group(1))
            for tile in ('west','south')}

def route_coordinates(road):
    yy,xx=np.mgrid[:SIZE[1],:SIZE[0]]
    best=np.full((SIZE[1],SIZE[0]),np.inf,np.float32)
    signed=np.zeros_like(best)
    arc=np.zeros_like(best)
    cumulative=0.
    for a,b in zip(road[:-1],road[1:]):
        a=np.asarray(a,dtype=np.float32);b=np.asarray(b,dtype=np.float32)
        vx,vy=b-a; length=float(np.hypot(vx,vy))
        if length<.001:continue
        t=np.clip(((xx-a[0])*vx+(yy-a[1])*vy)/(length*length),0,1)
        px=a[0]+t*vx;py=a[1]+t*vy
        d2=(xx-px)**2+(yy-py)**2
        update=d2<best
        best=np.where(update,d2,best)
        signed=np.where(update,((xx-px)*(-vy)+(yy-py)*vx)/length,signed)
        arc=np.where(update,cumulative+t*length,arc)
        cumulative+=length
    return signed,arc,np.sqrt(best)

def carve(image,road):
    if image.size!=SIZE:raise ValueError('Native 1536x1024 source required')
    if len(road)<3:raise ValueError('Road missing')
    signed,arc,distance=route_coordinates(road)
    src=np.asarray(image.convert('RGB'),dtype=np.float32)
    low=cv2.GaussianBlur(src,(0,0),2.5)
    grain=np.clip(src-low,-32,32)
    width=1.5+.32*np.sin(arc/29)+.18*np.sin(arc/11)
    offset=5.6+.30*np.sin(arc/57)
    rut=np.maximum(np.exp(-.5*((signed-offset)/width)**2),
                   np.exp(-.5*((signed+offset)/width)**2))
    compression=np.exp(-.5*(signed/10.2)**4)
    soil=np.empty_like(src)
    luminance=cv2.cvtColor(src.astype(np.uint8),cv2.COLOR_RGB2GRAY).astype(np.float32)/255
    soil[:,:,0]=91+55*luminance+grain[:,:,0]*.90
    soil[:,:,1]=76+41*luminance+grain[:,:,1]*.90
    soil[:,:,2]=52+29*luminance+grain[:,:,2]*.90
    alpha=np.clip(rut*.88,0,.90)
    out=src*(1-alpha[:,:,None])+soil*alpha[:,:,None]
    out*=1-(compression*(1-rut)*.045)[:,:,None]
    bank=np.exp(-.5*((np.abs(signed)-9.5)/1.35)**2)*.055
    out=out+bank[:,:,None]*src
    out=np.where((distance<=22)[:,:,None],out,src)
    result=Image.fromarray(np.uint8(np.clip(out,0,255)))
    mask=Image.fromarray(np.uint8(np.clip(alpha*255,0,255)))
    report={
      'roadGraph':'IMMUTABLE V123','maxChangeRadiusPx':22,
      'pixelsModifiedOutside22px':int(np.count_nonzero(np.any(np.asarray(result)!=src.astype(np.uint8),axis=2)&(distance>22))),
      'sourceNativeTexturePreserved':True,
      'artMethod':'dual source-textured rut compression, not source-evidenced 1780 cartway',
      'sourceRegisteredToV123':False,'historicalRoadsVerified':False,
      'bridgeBanksVerified':False,'humanVisualApproval':False,
      'physicalIPhoneApproved':False,'gameArtApproved':False,
      'productionApproved':False}
    return result,mask,report

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--image',type=Path,required=True)
    p.add_argument('--atlas',type=Path,required=True)
    p.add_argument('--tile',choices=['west','south'],required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--source-sha256',required=True)
    a=p.parse_args()
    raw=a.image.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=a.source_sha256:raise ValueError('Source SHA256 drift')
    road=read_roads(a.atlas)[a.tile]
    out,mask,report=carve(Image.open(a.image).convert('RGB'),road)
    a.output.mkdir(parents=True,exist_ok=True)
    out.save(a.output/(a.tile+'-dual-rut-unapproved.webp'),'WEBP',quality=93,method=6)
    mask.save(a.output/(a.tile+'-edit-mask.png'))
    report['sourceSha256']=a.source_sha256
    report['roadPointsSha256']=hashlib.sha256(json.dumps(road,separators=(',',':')).encode()).hexdigest()
    (a.output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()

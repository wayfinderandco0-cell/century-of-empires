#!/usr/bin/env python3
"""Rebuild WEST-only fictional cirque/tarn photo composition; V121/V123/V94 untouched.

Run from repository root:
  python scripts/rebuild_v267_west_cirque.py
Requires Pillow, numpy, opencv-python. The generated source is deliberately
kept separate from the original WEST and Matrei images for visual review.
"""
from pathlib import Path
import cv2
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'art-reviews' / 'v267-original-source'
BASE = ASSETS / 'west-native-original.jpg'
INPUT = ASSETS / 'west-cirque-generative-source-unapproved.webp'
OUTPUT = ASSETS / 'west-cirque-lake-recomposed-unapproved.jpg'
W,H = 1536,1024
ROUTE = np.array([[275,548,550],[370,520,522],[470,552,520],[570,635,540],
 [680,589,560],[784,575,551],[890,621,535],[980,648,515],[1085,630,507],
 [1210,586,490],[1320,559,480],[1450,558,478],[1536,576,478]],dtype=np.float32)

def smooth(a):
 a=np.clip(a,0,1)
 return a*a*(3-2*a)

def registered_west():
 # V267 source-registration math reproduced from the preview. This changes
 # only the review raster, not the V123 road positions or source photography.
 im=np.array(Image.open(BASE).convert('RGB').resize((W,H),Image.Resampling.BILINEAR))
 xx=np.arange(W,dtype=np.float32)
 yy=np.arange(H,dtype=np.float32)
 shift=np.interp(xx,ROUTE[:,0],ROUTE[:,1]-ROUTE[:,2])
 edge=smooth(yy/110)*smooth((H-1-yy)/285)
 map_x=np.broadcast_to(xx[None,:],(H,W)).copy()
 map_y=np.broadcast_to(yy[:,None]+edge[:,None]*shift[None,:],(H,W)).astype(np.float32)
 map_y=np.clip(map_y,0,H-1.001)
 return cv2.remap(im,map_x,map_y,cv2.INTER_LINEAR,borderMode=cv2.BORDER_REPLICATE)

def rebuild():
 west=registered_west()
 source=np.asarray(Image.open(INPUT).convert('RGB'))
 patch=cv2.resize(source[:465,:820],(920,465),interpolation=cv2.INTER_CUBIC)
 lab=cv2.cvtColor(patch,cv2.COLOR_RGB2LAB).astype(np.float32)
 native=cv2.cvtColor(west[10:475,45:965],cv2.COLOR_RGB2LAB).astype(np.float32)
 lab[:,:,0]=np.clip(lab[:,:,0]*.92+native[:,:,0]*.08,0,255)
 patch=cv2.cvtColor(lab.astype(np.uint8),cv2.COLOR_LAB2RGB)
 yy,xx=np.mgrid[0:465,0:920]
 ellipse=((xx-455)/445)**2+((yy-225)/226)**2
 contour=.065*np.sin(xx/37)+.045*np.cos(xx/53+yy/31)
 mask=np.uint8((ellipse+contour)<.96)*255
 # Poisson blend preserves a naturally irregular transition; it does not
 # clone trees from Matrei, change the WEST cartway, or add a road stripe.
 out=cv2.seamlessClone(cv2.cvtColor(patch,cv2.COLOR_RGB2BGR),
   cv2.cvtColor(west,cv2.COLOR_RGB2BGR),mask,(515,242),cv2.NORMAL_CLONE)
 Image.fromarray(cv2.cvtColor(out,cv2.COLOR_BGR2RGB)).save(OUTPUT,quality=92,subsampling=0)
 print(f'Wrote {OUTPUT.relative_to(ROOT)} ({W}x{H})')

if __name__=='__main__':rebuild()

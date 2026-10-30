#!/usr/bin/env python3
"""V267: compose an original SOUTH photo scene using a terrain-aware, sloping seam.
The immutable V121 Matrei image and V123 road/army graph are never modified.
Both source images are independently authored fictional Alpine game-art photos.
"""
from pathlib import Path
import json, hashlib, re
import cv2
import numpy as np
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'art-reviews/v267-original-source'
BASE=SRC/'south-no-horizon-overhead-unapproved.jpg'
NATIVE=SRC/'south-bridge-contact-unapproved.webp'
OUTPUT=SRC/'south-sloping-photo-join-unapproved.webp'
HTML=ROOT/'v267-three-octagon-original-art-prototype.html'
REVIEW=ROOT/'art-reviews/v267-sloping-photo-join-review.md'
SHEET=ROOT/'art-reviews/v267-sloping-photo-source-comparison.webp'
W,H=1536,1024
MARK='V267_SLOPING_ORIGINAL_PHOTO_JOIN_20261030'
# Existing V123 cartway: immutable world-space geometry.
ROAD=np.array([[466,0],[466,74],[470,160],[488,235],[540,310],
 [620,350],[700,400],[805,442],[930,510],[1050,550],
 [1140,585],[1270,605]],dtype=np.float32)

def smooth(t):
 t=np.clip(t,0,1)
 return t*t*(3-2*t)

def distance_to_route():
 y,x=np.mgrid[:H,:W].astype(np.float32)
 d=np.full((H,W),1e6,np.float32)
 for a,b in zip(ROAD[:-1],ROAD[1:]):
  dx,dy=b-a
  u=np.clip(((x-a[0])*dx+(y-a[1])*dy)/(dx*dx+dy*dy),0,1)
  d=np.minimum(d,np.hypot(x-a[0]-u*dx,y-a[1]-u*dy))
 return d

def choose_natural_seam(base,native):
 """Dynamic-programming boundary across real source photographs, not a straight alpha stripe.
 Penalize color disagreement and crossing high-contrast tree/rock edges.
 The boundary follows the left side of the native cartway-and-river landscape.
 """
 b=cv2.GaussianBlur(base.astype(np.float32),(0,0),7)
 n=cv2.GaussianBlur(native.astype(np.float32),(0,0),7)
 mismatch=np.mean(np.abs(b-n),axis=2)
 gb=cv2.Sobel(cv2.cvtColor(base,cv2.COLOR_RGB2GRAY),cv2.CV_32F,1,1,ksize=3)
 gn=cv2.Sobel(cv2.cvtColor(native,cv2.COLOR_RGB2GRAY),cv2.CV_32F,1,1,ksize=3)
 cost=cv2.GaussianBlur(mismatch+0.055*(np.abs(gb)+np.abs(gn)),(0,0),4)
 ys=np.arange(0,891,2,dtype=np.int32)
 cx=np.interp(ys,ROAD[:,1],ROAD[:,0],left=466,right=1270)
 cx=np.where(ys>605,1270+(ys-605)*1.12,cx)
 target=np.clip(cx-260,100,1570)
 # DP over absolute x coordinates, restricted to a broad 210px band around the
 # approximate forest/cartway transition. Changes of <=14px per 2 y-pixels.
 lo=75;hi=W-15
 xs=np.arange(lo,hi+1)
 prev=np.full(len(xs),1e9,np.float64)
 trace=np.zeros((len(ys),len(xs)),np.int16)
 for j,y in enumerate(ys):
  local=cost[y,xs].astype(np.float64)+.009*(xs-target[j])**2
  local[np.abs(xs-target[j])>210]=1e8
  if j==0:
   prev=local
   continue
  best=np.full(len(xs),1e12,np.float64)
  step=np.zeros(len(xs),np.int16)
  for delta in range(-7,8):
   src=np.clip(np.arange(len(xs))+delta,0,len(xs)-1)
   cand=prev[src]+.32*abs(delta)
   take=cand<best
   best[take]=cand[take]
   step[take]=delta
  trace[j]=step
  prev=best+local
 k=int(np.argmin(prev))
 result=np.zeros(len(ys),np.float32)
 for j in range(len(ys)-1,-1,-1):
  result[j]=xs[k]
  if j>0:k=int(np.clip(k+trace[j,k],0,len(xs)-1))
 # Source region narrows to nothing at the southern border.
 full=np.interp(np.arange(H),ys,result)
 full[891:]=np.linspace(full[890],W+150,H-891)
 return full

def water_bank(native):
 hsv=cv2.cvtColor(native,cv2.COLOR_RGB2HSV)
 raw=np.uint8(((hsv[:,:,0]>=78)&(hsv[:,:,0]<=127)&
  (hsv[:,:,1]>=42)&(hsv[:,:,2]>=55))*255)
 yy,xx=np.mgrid[:H,:W]
 raw[(xx<690)|(yy>870)]=0
 n,labels,stats,_=cv2.connectedComponentsWithStats(raw,8)
 selected=np.zeros((H,W),np.uint8)
 for i in range(1,n):
  x,y,w,h,area=stats[i]
  if area>220 and x+w>800 and y<790:
   selected[labels==i]=255
 selected=cv2.morphologyEx(selected,cv2.MORPH_CLOSE,
  cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(21,21)))
 selected=cv2.dilate(selected,
  cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(141,141)))
 return cv2.GaussianBlur(selected.astype(np.float32)/255,(0,0),22)

def blend(a,b,mask,levels=5):
 aa=a.astype(np.float32)/255
 bb=b.astype(np.float32)/255
 gm=[mask.astype(np.float32)]
 ga=[aa];gb=[bb]
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
 out=la[-1]*(1-gm[-1][:,:,None])+lb[-1]*gm[-1][:,:,None]
 for i in range(levels-1,-1,-1):
  out=cv2.pyrUp(out,dstsize=(la[i].shape[1],la[i].shape[0]))
  m=gm[i][:,:,None]
  out+=la[i]*(1-m)+lb[i]*m
 return np.uint8(np.clip(out*255,0,255))

def compose():
 base=np.asarray(Image.open(BASE).convert('RGB').resize((W,H),Image.Resampling.LANCZOS))
 native=np.asarray(Image.open(NATIVE).convert('RGB').resize((W,H),Image.Resampling.LANCZOS))
 seam=choose_natural_seam(base,native)
 y,x=np.mgrid[:H,:W].astype(np.float32)
 # The photographic source dominates on the EAST of a diagonal, natural
 # tree/rock boundary. No duplicate cartway from the independent base survives.
 main=smooth((x-seam[:,None]+55)/110)
 main*=smooth((905-y)/115)
 dist=distance_to_route()
 road=smooth((154-dist)/94)
 bank=water_bank(native)
 # Original bridge is an indivisible photographic object with both approaches.
 bridge=np.exp(-(((x-1137)/215)**4+((y-578)/185)**4))
 mask=np.maximum.reduce([main,road,bank,bridge]).astype(np.float32)
 # Do not move or redraw the source cartway; retain original photographic
 # ruts and their adjacent stones, vegetation and fence lines.
 mask[dist<61]=1
 out=blend(base,native,mask,5)
 out[dist<61]=native[dist<61]
 assert np.array_equal(out[dist<61],native[dist<61])
 changed=int((np.max(np.abs(out.astype(np.int16)-native.astype(np.int16)),axis=2)>8).sum())
 assert changed>180000,changed
 return base,native,out,seam,changed

def stage(html):
 if MARK in html:return html
 needle='const southArtSource='
 if html.count(needle)!=1:
  raise RuntimeError('SOUTH source selector changed; refuse unsafe edit')
 insert=('const SOUTH_SLOPING_PHOTO_PREVIEW=SOUTH_ART_MODE==="slope"; /* '+MARK+' */\n'
  'const southArtSource=SOUTH_SLOPING_PHOTO_PREVIEW'
  ' ? "art-reviews/v267-original-source/south-sloping-photo-join-unapproved.webp" : ')
 html=html.replace(needle,insert,1)
 assert '[1536,478]' in html and '[466,0]' in html
 assert 'const southRoad=' in html and 'const westRoad=' in html
 return html

def main():
 base,native,out,seam,changed=compose()
 Image.fromarray(out).save(OUTPUT,'WEBP',quality=95,method=6)
 board=Image.new('RGB',(1536,1050),'#15231b')
 board.paste(Image.fromarray(native).resize((768,512)),(0,25))
 board.paste(Image.fromarray(out).resize((768,512)),(768,25))
 d=ImageDraw.Draw(board)
 d.text((12,5),'BEFORE: single original SOUTH corridor',fill='white')
 d.text((785,5),'AFTER: diagonal source-composed SOUTH',fill='white')
 board.paste(Image.fromarray(base).resize((768,512)),(0,537))
 annotated=Image.fromarray(out).resize((768,512))
 board.paste(annotated,(768,537))
 d.text((12,520),'SECOND ORIGINAL PHOTO: uninterrupted Alpine base',fill='white')
 d.text((785,520),'FINAL ART: no global warp, no painted road',fill='white')
 board.save(SHEET,format='WEBP',quality=83,method=6)
 current=HTML.read_text()
 revised=stage(current)
 if revised!=current:HTML.write_text(revised)
 REVIEW.write_text(
  '# SOUTH terrain-aware photographic composition — UNAPPROVED\n\n'
  'This candidate uses two independent original fictional Alpine source '
  'photographs. A dynamically selected diagonal seam follows natural '
  'material transitions, avoiding a horizontal cut through forest. '
  'The entire physical cartway, bridge, river and immediate banks are '
  'native source pixels at their existing V123 coordinates; no global '
  'terrain warp, copied Matrei scenery, painted road or duplicated trees.\n\n'
  f'Pixels changed relative to the single-source SOUTH: {changed}.\n'
  'Review: ?southArt=slope. This is original fictional 1780–1880 game art, '
  'not verified historical topography. User approval NOT given. '
  'V121, V123, V94, sprites, saves and production untouched.\n\n'
  'Sources: '+hashlib.sha256(BASE.read_bytes()).hexdigest()+' / '+
  hashlib.sha256(NATIVE.read_bytes()).hexdigest()+'\n')
 print(json.dumps({'art':str(OUTPUT.relative_to(ROOT)),
  'changed_pixels':changed,'preview':'?southArt=slope',
  'source_comparison':str(SHEET.relative_to(ROOT)),
  'status':'UNAPPROVED'}))

if __name__=='__main__':main()

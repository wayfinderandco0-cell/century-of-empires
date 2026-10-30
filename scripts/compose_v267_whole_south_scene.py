#!/usr/bin/env python3
"""Recompose one WHOLE SOUTH fictional Alpine scene from TWO independent original photos.

One uninterrupted 1536x1024 photographic base is used for every tree, hillside,
and meadow. A second *independently authored* original photo supplies the
entire V123 cartway, bridge, and river gorge with native surrounding terrain.
The original SOUTH scene is NOT globally warped, mirrored, or tiled. No
synthetic road strokes, repeated trees, or Matrei scenery are inserted.
This remains an opt-in ART candidate; never a production approval.
"""
from __future__ import annotations
import hashlib, json, re
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'art-reviews/v267-original-source'
BASE=SRC/'south-no-horizon-overhead-unapproved.jpg'
CORRIDOR=SRC/'south-bridge-contact-unapproved.webp'
OUT=SRC/'south-whole-scene-road-river-composition-unapproved.webp'
HTML=ROOT/'v267-three-octagon-original-art-prototype.html'
REPORT=ROOT/'art-reviews/v267-whole-south-composition-review.md'
W,H=1536,1024
# EXACT IMMUTABLE V123 cartway polyline; the road itself comes from photographic pixels.
ROUTE=np.array([[466,0],[466,74],[470,160],[488,235],[540,310],[620,350],
 [700,400],[805,442],[930,510],[1050,550],[1140,585],[1270,605]],np.float32)
MARK='V267_WHOLE_SOUTH_PHOTOGRAPHIC_SCENE_20261030'

def smooth(x):
 x=np.clip(x,0,1);return x*x*(3-2*x)

def road_distance():
 yy,xx=np.mgrid[:H,:W].astype(np.float32)
 d=np.full((H,W),1e7,np.float32)
 for a,b in zip(ROUTE[:-1],ROUTE[1:]):
  vx,vy=b-a;den=vx*vx+vy*vy
  t=np.clip(((xx-a[0])*vx+(yy-a[1])*vy)/den,0,1)
  d=np.minimum(d,np.hypot(xx-a[0]-t*vx,yy-a[1]-t*vy))
 return d

def blend_multiscale(a,b,alpha,levels=5):
 """Native photographic detail retained; irregular corridor edges feather by scale."""
 a=a.astype(np.float32)/255
 b=b.astype(np.float32)/255
 alpha=np.clip(alpha.astype(np.float32),0,1)
 ga=[a];gb=[b];gm=[alpha]
 for _ in range(levels):
  ga.append(cv2.pyrDown(ga[-1]));gb.append(cv2.pyrDown(gb[-1]))
  gm.append(cv2.pyrDown(gm[-1]))
 la=[];lb=[]
 for i in range(levels):
  size=(ga[i].shape[1],ga[i].shape[0])
  la.append(ga[i]-cv2.pyrUp(ga[i+1],dstsize=size))
  lb.append(gb[i]-cv2.pyrUp(gb[i+1],dstsize=size))
 la.append(ga[-1]);lb.append(gb[-1])
 mix=[]
 for i in range(levels+1):
  m=gm[i][:,:,None]
  mix.append(la[i]*(1-m)+lb[i]*m)
 out=mix[-1]
 for i in range(levels-1,-1,-1):
  out=cv2.pyrUp(out,dstsize=(mix[i].shape[1],mix[i].shape[0]))+mix[i]
 return np.uint8(np.clip(out*255,0,255))

def scene():
 base=np.asarray(Image.open(BASE).convert('RGB').resize((W,H),Image.Resampling.LANCZOS))
 native=np.asarray(Image.open(CORRIDOR).convert('RGB'))
 assert base.shape==native.shape==(H,W,3)
 dist=road_distance()
 yy,xx=np.mgrid[:H,:W].astype(np.float32)
 # The road is photographic, including adjacent ground, fence lines, boulders
 # and its original bridge. A 120-185px variable corridor follows its curves.
 # Protect the entire northern approach at (466,0), and do not create an
 # artificial tan stripe atop a mismatched meadow.
 width=125+36*smooth((yy-180)/400)
 width+=16*np.sin(yy/112+xx/230)
 road=smooth((dist-width+55)/-55)
 # The independent gorge source contains river/rock features. Retain those
 # features as whole photographic shapes rather than inventing water pixels.
 hsv=cv2.cvtColor(native,cv2.COLOR_RGB2HSV)
 water=((hsv[:,:,0]>=78)&(hsv[:,:,0]<=126)&(hsv[:,:,1]>=38)&
        (hsv[:,:,2]>=50)).astype(np.uint8)
 # Restrict to the river valley east of the cartway, and keep coherent banks.
 valley=(xx>650)&(xx<1500)&(yy<810)
 water*=valley.astype(np.uint8)
 n,lab,stats,_=cv2.connectedComponentsWithStats(water,8)
 keep=np.zeros_like(water)
 for k in range(1,n):
  x,y,w,h,area=stats[k]
  if area>120 and x+w>820 and y<760:keep[lab==k]=255
 keep=cv2.morphologyEx(keep,cv2.MORPH_CLOSE,np.ones((17,17),np.uint8))
 # Expand to riverbanks, boulders and riverside conifers: not a floating
 # isolated turquoise water stripe.
 bank=cv2.dilate(keep,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(191,191)))
 bank=cv2.GaussianBlur(bank.astype(np.float32)/255,(0,0),26)
 # The stone bridge and approaches are a single source object.
 bridge=np.exp(-(((xx-1137)/215)**4+((yy-578)/205)**4))
 # Avoid the straight source-photo horizon; no source pixels copied from it.
 # Source A is already a full overhead Alpine landscape.
 mask=np.maximum(road,np.maximum(bank*.98,bridge))
 # The second photo supplies all north-east riverbank detail, but the original
 # west forest stays one continuous native photographic scene.
 mask*=smooth((900-yy)/120)
 # The road's lower end is protected independently of the river fade.
 mask=np.maximum(mask,road)
 mask=np.clip(mask,0,1).astype(np.float32)
 # Preserve the exact photographic road center and its 55px shoulder.
 mask[dist<60]=1
 # All native SOUTH source pixels remain in place: NO geometry resampling.
 out=blend_multiscale(base,native,mask,levels=5)
 # The upper 25px road entry is kept as actual native source pixels to ensure
 # a photographed cartway reaches x466, not a procedural stroke.
 out[:25,404:529]=native[:25,404:529]
 # Never use an artificial Matrei duplicate, nor modify the 100-node graph.
 assert np.array_equal(out[:25,425:510],native[:25,425:510])
 assert out.shape==(1024,1536,3)
 # Detect whether this is a material whole-scene change, not a cosmetic tweak.
 delta=np.max(np.abs(out.astype(np.int16)-native.astype(np.int16)),axis=2)
 changed=int((delta>8).sum())
 assert changed>350000,changed
 return base,native,out,mask,changed

def stage(html):
 if MARK in html:return html
 assert 'const southArtSource=' in html
 assert 'const SOUTH_ART_MODE=' in html
 assert '[1536,478]' in html and '[466,0]' in html
 html=html.replace('const southArtSource=',
  'const SOUTH_WHOLE_SCENE_PREVIEW=SOUTH_ART_MODE==="whole"; /* '+MARK+' */\n'
  'const southArtSource=SOUTH_WHOLE_SCENE_PREVIEW'
  ' ? "art-reviews/v267-original-source/south-whole-scene-road-river-composition-unapproved.webp"'
  ' : ',1)
 return html

def main():
 original=HTML.read_text()
 base,native,out,mask,changed=scene()
 Image.fromarray(out).save(OUT,'WEBP',quality=95,method=6)
 html=stage(original)
 if html!=original:HTML.write_text(html)
 assert 'const southRoad=' in html and 'const westRoad=' in html
 review=ROOT/'art-reviews/v267-whole-south-source-before-after.jpg'
 board=Image.new('RGB',(1536,1100),'#1a2820')
 board.paste(Image.fromarray(native).resize((768,512)),(0,44))
 board.paste(Image.fromarray(out).resize((768,512)),(768,44))
 d=ImageDraw.Draw(board)
 d.text((18,18),'BEFORE: existing SOUTH original photo',fill='#f6e8cb')
 d.text((788,18),'AFTER: independently authored whole-scene candidate',fill='#f6e8cb')
 board.paste(Image.fromarray(base).resize((768,512)),(0,585))
 board.paste(Image.fromarray(np.uint8(mask*255)).convert('RGB').resize((768,512)),(768,585))
 board.save(review,quality=88)
 REPORT.write_text(
  '# Whole-scene SOUTH original-photo composition — UNAPPROVED\n\n'
  'An independent 1536×1024 near-overhead Alpine landscape now supplies the '
  'entire SOUTH forest, mountains and meadows, with a second original '
  'photographic source supplying its V123-registered road, native bridge '
  'and limestone river gorge. The 2D photographic cartway and physical '
  'riverbanks are retained as coherent objects with surrounding ground, '
  'not digital road stripes or cloned trees. No source photograph is '
  'mirrored, globally warped, tiled or borrowed from Matrei.\n\n'
  f'Source pixels changed (>8 RGB): {changed}. '
  f'Candidate: {OUT.relative_to(ROOT)}.\n\n'
  'This is fictional 1780–1880 atmosphere game art, not verified historic '
  'topography. V121/V123/V94/sprites/saves untouched. Review ONLY via '
  '?southArt=whole on the SAME isolated V267 preview. Must inspect real '
  '390×844 iPhone-sized WebKit screenshots, road joins, river and forest '
  'before any visual approval. Production RED.\n\n'
  'Source hashes: '+hashlib.sha256(BASE.read_bytes()).hexdigest()+' / '+
  hashlib.sha256(CORRIDOR.read_bytes()).hexdigest()+'\n')
 print(json.dumps({'candidate':str(OUT.relative_to(ROOT)),
  'bytes':OUT.stat().st_size,'changed_pixels':changed,
  'review':str(review.relative_to(ROOT)),'mode':'?southArt=whole',
  'status':'UNAPPROVED'}))
if __name__=='__main__':main()

#!/usr/bin/env python3
"""Original SOUTH northern forest shoulder: native conifer material, no geometry warp.

Fictional 1780–1880 Alpine game-art prototype. V121 Matrei, V123 graph,
V94 campaign, units and saves are immutable. This is not a verified map.
"""
from pathlib import Path
import base64, hashlib, io, json, re
import cv2
import numpy as np
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'art-reviews/v267-original-source'
BASE=SRC/'south-sloping-photo-join-unapproved.webp'
FOREST=SRC/'south-native-original.jpg'
OUT=SRC/'south-original-forest-continuity-unapproved.webp'
HTML=ROOT/'v267-three-octagon-original-art-prototype.html'
REVIEW=ROOT/'art-reviews/v267-original-forest-continuity-review.md'
SHEET=ROOT/'art-reviews/v267-original-forest-continuity-source.jpg'
W,H=1536,1024
MARK='V267_SOUTH_NATIVE_FOREST_CONTINUITY_20261030'
def smooth(x):
 x=np.clip(x,0,1);return x*x*(3-2*x)
def forest_cutout(donor, box, size):
 x0,y0,x1,y1=box
 crop=donor[y0:y1,x0:x1]
 crop=cv2.resize(crop,size,interpolation=cv2.INTER_CUBIC)
 # Native conifer crowns and their real photographed shadows, not green
 # procedural filler. Expand silhouettes slightly to retain ground contact.
 hsv=cv2.cvtColor(crop,cv2.COLOR_RGB2HSV)
 dark=(hsv[:,:,2]<139)&(hsv[:,:,1]>30)&(hsv[:,:,0]>22)&(hsv[:,:,0]<112)
 green=(hsv[:,:,0]>26)&(hsv[:,:,0]<100)&(hsv[:,:,1]>35)&(hsv[:,:,2]<160)
 mask=np.uint8(dark|green)*255
 mask=cv2.morphologyEx(mask,cv2.MORPH_CLOSE,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(17,17)))
 n,labels,stats,_=cv2.connectedComponentsWithStats(mask,8)
 selected=np.zeros_like(mask)
 for k in range(1,n):
  if stats[k,4]>120:selected[labels==k]=255
 selected=cv2.dilate(selected,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(13,13)))
 selected=cv2.GaussianBlur(selected.astype(np.float32)/255,(0,0),8)
 # Avoid hard rectangular photo boundaries.
 yy,xx=np.mgrid[:size[1],:size[0]].astype(np.float32)
 envelope=smooth(xx/32)*smooth((size[0]-xx)/32)*smooth(yy/35)*smooth((size[1]-yy)/35)
 return crop,selected*envelope
def put(native,donor,box,dest,size,road_x=466):
 crop,alpha=forest_cutout(donor,box,size)
 x0,y0=dest;w,h=size
 x1=min(W,x0+w);y1=min(H,y0+h)
 crop=crop[:y1-y0,:x1-x0];alpha=alpha[:y1-y0,:x1-x0]
 if x0<0 or y0<0:raise ValueError('negative placement')
 yy,xx=np.mgrid[y0:y1,x0:x1]
 # Do not alter the photographed V123 road or northern river gorge.
 road=np.abs(xx-road_x)>92+0.20*yy
 # Protect only the actual photographed water and nearby stone banks;
 # the eastern conifer hillside is NOT a river and may be reforested.
 target_rgb=native[y0:y1,x0:x1]
 water_hsv=cv2.cvtColor(target_rgb,cv2.COLOR_RGB2HSV)
 river=(water_hsv[:,:,0]>=77)&(water_hsv[:,:,0]<=127)&(water_hsv[:,:,1]>=38)&(water_hsv[:,:,2]>=52)
 river=cv2.dilate(np.uint8(river)*255,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(53,53)))>0
 protected=road & (~river)
 alpha*=protected.astype(np.float32)
 target=native[y0:y1,x0:x1]
 # Gentle photographic material matching, no scaling of trees.
 hsv_d=cv2.cvtColor(crop,cv2.COLOR_RGB2LAB).astype(np.float32)
 hsv_t=cv2.cvtColor(target,cv2.COLOR_RGB2LAB).astype(np.float32)
 shift=np.median(hsv_t.reshape(-1,3),axis=0)-np.median(hsv_d.reshape(-1,3),axis=0)
 shift=np.clip(shift,[-12,-7,-7],[12,7,7])
 crop=cv2.cvtColor(np.uint8(np.clip(hsv_d+shift,0,255)),cv2.COLOR_LAB2RGB)
 native[y0:y1,x0:x1]=np.uint8(np.clip(target*(1-alpha[:,:,None])+crop*alpha[:,:,None],0,255))
 return int(np.count_nonzero(alpha>.35))
def matrei_edge(html):
 m=re.search(r'ART_MATREI_CANONICAL="data:image/[^;]+;base64,([^"]+)"',html)
 if not m:raise RuntimeError('Missing original V121 Matrei source')
 source=np.asarray(Image.open(io.BytesIO(base64.b64decode(m.group(1)))).convert('RGB'))
 if source.shape!=(H,W,3):raise RuntimeError('V121 size changed')
 x=np.arange(W,dtype=np.float32)[None,:]
 y=np.arange(1008,1024,dtype=np.float32)[:,None]
 t=smooth((y-845)/179)
 sy=10+y*(953/H)-26*t
 sl=np.where(sy<286,385-(sy-10)*(295/276),np.where(sy>674,90+(sy-674)*(295/289),90))
 tl=np.where(y<256,256-y,np.where(y>768,y-768,0))
 tr=W-tl
 b=smooth((y-700)/324)
 sx=np.clip(sl+(x-tl)*(W-2*sl)/(tr-tl)-55*b*np.exp(-.5*((x-466)/105)**2),0,W-1.001)
 west=26*np.exp(-.5*((x-240)/400)**2)*np.exp(-.5*((y-505)/110)**2)
 return cv2.remap(source,sx.astype(np.float32),
                   np.clip(sy+west,0,H-1.001).astype(np.float32),cv2.INTER_LINEAR)
def harmonize_north(photo,edge):
 # Match broad photographed light and meadow/forest materials at the
 # ACTUAL V121 southern edge without copying/mirroring Matrei trees.
 lab=cv2.cvtColor(photo,cv2.COLOR_RGB2LAB).astype(np.float32)
 border=cv2.cvtColor(edge,cv2.COLOR_RGB2LAB).astype(np.float32)
 reference=np.median(border[-8:],axis=0)
 current=np.median(lab[:13],axis=0)
 delta=reference-current
 delta[:,0]=np.clip(delta[:,0],-24,24)
 delta[:,1:]=np.clip(delta[:,1:],-9,9)
 delta=cv2.GaussianBlur(delta.reshape(1,W,3),(0,0),63)[0]
 yy,xx=np.mgrid[:H,:W].astype(np.float32)
 fade=smooth((395-yy)/395)*.86
 # Road stays native photo; river chroma stays native photo.
 fade*=1-.43*np.exp(-.5*((xx-466)/85)**2)
 fade*=1-.48*smooth((xx-870)/110)
 out=np.uint8(np.clip(lab+fade[:,:,None]*delta[None,:,:],0,255))
 rgb=cv2.cvtColor(out,cv2.COLOR_LAB2RGB)
 rgb[fade<=0]=photo[fade<=0]
 return rgb
def main():
 html=HTML.read_text(encoding='utf-8')
 if MARK in html and OUT.exists():
  print('Candidate already staged; not reprocessing art');return
 original=np.asarray(Image.open(BASE).convert('RGB'))
 donor=np.asarray(Image.open(FOREST).convert('RGB'))
 assert original.shape==(H,W,3)
 result=original.copy()
 # Three DISTINCT native forest stands, transplanted from independent
 # SOUTH material (not from Matrei), each placed in the exposed shoulder.
 # Irregular conifer silhouettes preserve individual tree shapes.
 patches=[
  ((815,10,1125,270),(1110,30),(310,260)),
  ((35,15,335,280),(770,145),(300,265)),
  ((800,360,1130,620),(1200,245),(330,260)),
 ]
 transplanted=sum(put(result,donor,*p) for p in patches)
 result=harmonize_north(result,matrei_edge(html))
 assert transplanted>9000,transplanted
 # Preserve lower scene and the bridge entirely. Only north shoulder
 # receives forest and light continuity; no whole-tile warp or mirror.
 assert np.array_equal(result[510:],original[510:])
 delta=np.max(np.abs(result.astype(np.int16)-original.astype(np.int16)),axis=2)
 changed=int((delta>8).sum())
 assert changed>75000,changed
 Image.fromarray(result).save(OUT,'WEBP',quality=95,method=6)
 board=Image.new('RGB',(1536,555),'#17231d')
 board.paste(Image.fromarray(original).resize((768,512)),(0,35))
 board.paste(Image.fromarray(result).resize((768,512)),(768,35))
 d=ImageDraw.Draw(board)
 d.text((10,10),'BEFORE: SOUTH original slope source',fill='white')
 d.text((780,10),'AFTER: distinct native forest stands - UNAPPROVED',fill='white')
 board.save(SHEET,quality=86)
 if MARK not in html:
  assert html.count('const southArtSource=')==1
  html=html.replace('const southArtSource=',
   'const SOUTH_NATIVE_FOREST_PREVIEW=SOUTH_ART_MODE==="nativeforest"; /* '+MARK+' */\n'
   'const southArtSource=SOUTH_NATIVE_FOREST_PREVIEW'
   ' ? "art-reviews/v267-original-source/south-original-forest-continuity-unapproved.webp" : ',1)
  assert '[1536,478]' in html and '[466,0]' in html
  assert html.count('const southRoad=')==1 and html.count('const westRoad=')==1
  HTML.write_text(html,encoding='utf-8')
 REVIEW.write_text('# SOUTH original northern forest continuity — UNAPPROVED\n\n'
  'Three independent native conifer stands from the original SOUTH photographic '
  'material were composed into the sparsely forested northern shoulder. '
  'Natural canopy masks and original ground shadows avoid digital tree strokes. '
  'The native V123 cartway, stone bridge and river remain unmoved. '
  'Broad light is matched to the original Matrei southern edge; no V121 pixels '
  'are copied into SOUTH. This is fictional Alpine game art, not verified '
  'historical topography.\n\n'
  f'Native forest pixels transplanted: {transplanted}. '
  f'Changed source pixels (>8 RGB): {changed}.\n'
  'Review ?southArt=nativeforest against default at 390x844 in WebKit/Chromium. '
  'Not approved. No V121/V123/V94/sprites/saves/main changes. Production RED.\n'
  'Source hashes: '+hashlib.sha256(BASE.read_bytes()).hexdigest()+' / '+
  hashlib.sha256(FOREST.read_bytes()).hexdigest()+'\n',encoding='utf-8')
 print(json.dumps({'changed_pixels':changed,'native_forest_pixels':transplanted,
                   'art':str(OUT.relative_to(ROOT)),'status':'UNAPPROVED'}))
if __name__=='__main__':main()

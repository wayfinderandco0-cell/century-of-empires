#!/usr/bin/env python3
"""Single-source WEST/SOUTH Alpine scene reconstruction for isolated V267 review.

Keep each original photograph whole. Adapt broad illumination to the immutable
V121 Matrei edge without copying/mirroring Matrei scenery, adding road stripes,
warping trees, or changing V123 routes. Fictional 1780–1880 atlas artwork.
"""
from pathlib import Path
import base64,hashlib,io,json,re
import cv2,numpy as np
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'art-reviews/v267-original-source'
HTML=ROOT/'v267-three-octagon-original-art-prototype.html'
WEST=SRC/'west-native-restored-unapproved.jpg'
SOUTH=SRC/'south-bridge-contact-unapproved.webp'
WEST_OUT=SRC/'west-unified-native-border-unapproved.webp'
SOUTH_OUT=SRC/'south-unified-native-border-unapproved.webp'
SHEET=ROOT/'art-reviews/v267-unified-native-source-comparison.webp'
REVIEW=ROOT/'art-reviews/v267-unified-native-review.md'
MARK='V267_UNIFIED_NATIVE_SOURCE_BORDER_20261030'
W,H=1536,1024

def smooth(v):
 v=np.clip(v,0,1)
 return v*v*(3-2*v)

def matrei_photo(html):
 m=re.search(r'ART_MATREI_CANONICAL="data:image/[^;]+;base64,([^"]+)"',html)
 if not m:raise RuntimeError('Immutable Matrei source not found')
 a=np.asarray(Image.open(io.BytesIO(base64.b64decode(m.group(1)))).convert('RGB'))
 assert a.shape==(H,W,3),a.shape
 return a

def matrei_display(photo,xx,yy):
 """Sample immutable Matrei original through the existing V121 display crop."""
 xx=np.asarray(xx,dtype=np.float32)
 yy=np.asarray(yy,dtype=np.float32)
 t=smooth((yy-845)/179)
 sy=10+yy*(953/H)-26*t
 sl=np.where(sy<286,385-(sy-10)*(295/276),
     np.where(sy>674,90+(sy-674)*(295/289),90))
 tl=np.where(yy<256,256-yy,np.where(yy>768,yy-768,0))
 tr=W-tl
 b=smooth((yy-700)/324)
 sx=sl+(xx-tl)*(W-2*sl)/(tr-tl)-55*b*np.exp(-.5*((xx-466)/105)**2)
 west=26*np.exp(-.5*((xx-240)/400)**2)*np.exp(-.5*((yy-505)/110)**2)
 return cv2.remap(photo,np.clip(sx,0,W-1.001).astype(np.float32),
     np.clip(sy+west,0,H-1.001).astype(np.float32),cv2.INTER_LINEAR)

def grade_west(native,matrei):
 # The source is a SINGLE original mountain cirque photograph, no inset.
 # Match forest/rock/meadow light at the WEST->MATREI east border.
 yy=np.broadcast_to(np.arange(H,dtype=np.float32)[:,None],(H,88))
 xx=np.broadcast_to(np.arange(18,106,dtype=np.float32)[None,:],(H,88))
 edge=matrei_display(matrei,xx,yy)
 a=cv2.cvtColor(native,cv2.COLOR_RGB2LAB).astype(np.float32)
 b=cv2.cvtColor(edge,cv2.COLOR_RGB2LAB).astype(np.float32)
 ref=np.median(b,axis=1)
 own=np.median(a[:,1418:1510],axis=1)
 diff=ref-own
 for k,cap in enumerate((23,11,11)):
  diff[:,k]=np.clip(diff[:,k],-cap,cap)
 diff=cv2.GaussianBlur(diff.reshape(H,1,3),(1,0),0) if False else diff
 # Smooth vertically over 55px to preserve intact photographed crowns.
 diff=np.stack([cv2.GaussianBlur(diff[:,k].reshape(H,1),(1,0),0)[:,0]
               if False else cv2.GaussianBlur(diff[:,k].reshape(1,H),(0,0),45)[0]
               for k in range(3)],axis=1)
 xx=np.arange(W,dtype=np.float32)[None,:]
 yy=np.arange(H,dtype=np.float32)[:,None]
 fade=smooth((xx-1000)/536)*.90
 # Road is original photographed dirt, preserve rut color and contrast.
 road=smooth((np.abs(yy-478)-34)/95)
 fade=fade*(.64+.36*road)
 adjusted=np.uint8(np.clip(a+fade[:,:,None]*diff[:,None,:],0,255))
 out=cv2.cvtColor(adjusted,cv2.COLOR_LAB2RGB)
 out[:,:950]=native[:,:950]
 return out

def route_distance(points):
 """Distance to existing source-photo road; does not change V123 graph."""
 yy,xx=np.mgrid[:H,:W].astype(np.float32)
 dist=np.full((H,W),10000,np.float32)
 for (ax,ay),(bx,by) in zip(points[:-1],points[1:]):
  vx,vy=bx-ax,by-ay
  t=np.clip(((xx-ax)*vx+(yy-ay)*vy)/(vx*vx+vy*vy),0,1)
  dist=np.minimum(dist,np.hypot(xx-ax-vx*t,yy-ay-vy*t))
 return dist

def multiband(a,b,mask):
 """Blend photographic landform, not a procedural green filler."""
 a=a.astype(np.float32)/255
 b=b.astype(np.float32)/255
 m=np.clip(mask.astype(np.float32),0,1)
 aa=[a];bb=[b];mm=[m]
 for i in range(6):
  aa.append(cv2.pyrDown(aa[-1]))
  bb.append(cv2.pyrDown(bb[-1]))
  mm.append(cv2.pyrDown(mm[-1]))
 out=aa[-1]*(1-mm[-1][:,:,None])+bb[-1]*mm[-1][:,:,None]
 for i in range(5,-1,-1):
  size=(aa[i].shape[1],aa[i].shape[0])
  ga=aa[i]-cv2.pyrUp(aa[i+1],dstsize=size)
  gb=bb[i]-cv2.pyrUp(bb[i+1],dstsize=size)
  out=cv2.pyrUp(out,dstsize=size)+ga*(1-mm[i][:,:,None])+gb*mm[i][:,:,None]
 return np.uint8(np.clip(out*255,0,255))

def grade_south(native,matrei):
 """Whole SOUTH source-scene recomposition: independent meadow/limestone west,
 original forest/river/stone bridge east, one real photographed V123 cartway.
 No mirrored landscapes, global forest warp, painted roads or settlements.
 """
 base=np.asarray(Image.open(SRC/'south-no-horizon-overhead-unapproved.jpg')
                 .convert('RGB').resize((W,H),Image.Resampling.LANCZOS))
 yy,xx=np.mgrid[:H,:W].astype(np.float32)
 # The base landscape contains a differently routed source cartway. Remove
 # its entire physical trace BEFORE integrating the original V123-aligned
 # photographic road and shoulder. Otherwise two roads would remain.
 abandoned=[(515,0),(515,90),(535,175),(590,245),(705,315),
            (835,380),(960,440),(1100,483),(1260,502),(1536,528)]
 old=route_distance(abandoned)
 road_mask=np.uint8(old<43)*255
 road_mask=cv2.dilate(road_mask,np.ones((9,9),np.uint8))
 clean=cv2.inpaint(base,road_mask,18,cv2.INPAINT_TELEA)
 # Retain one native cartway, its actual surrounding grass/rocks, bridge,
 # river and eastern forest. This is a coherent landscape, not a road stripe.
 canonical=[(466,0),(466,74),(470,160),(488,235),(540,310),
            (620,350),(700,400),(805,442),(930,510),(1050,550),
            (1140,585),(1270,605)]
 d=route_distance(canonical)
 # Broad photographic native corridor around actual dirt road.
 corridor=1-smooth((d-112)/76)
 # Native forest and river form one complete eastern half; irregular edge
 # follows the alpine slope and avoids a rectangular seam through trees.
 boundary=710+42*np.sin(yy/109)+28*np.sin(yy/44)
 east=smooth((xx-boundary)/150)
 # River and bridge stay from the SAME original native photograph.
 hsv=cv2.cvtColor(native,cv2.COLOR_RGB2HSV)
 river=((hsv[:,:,0]>76)&(hsv[:,:,0]<130)&
        (hsv[:,:,1]>33)&(xx>670)&(yy<820)).astype(np.uint8)
 river=cv2.morphologyEx(river,cv2.MORPH_CLOSE,np.ones((15,15),np.uint8))
 n,lab,stats,_=cv2.connectedComponentsWithStats(river,8)
 selected=np.zeros((H,W),np.uint8)
 for k in range(1,n):
  x0,y0,w0,h0,area=stats[k]
  if area>200 and x0+w0>830: selected[lab==k]=255
 bank=cv2.dilate(selected,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(151,151)))
 bank=cv2.GaussianBlur(bank.astype(np.float32)/255,(0,0),22)
 mask=np.maximum(east,np.maximum(corridor,bank*.98))
 mask=np.maximum(mask,np.exp(-(((xx-1140)/210)**4+((yy-585)/170)**4)))
 mask=np.clip(mask,0,1)
 mask[d<54]=1
 out=multiband(clean,native,mask)
 # Original photographic dirt road and shoulders remain native exactly.
 out[d<54]=native[d<54]
 # Match the upper 300px lighting to V121 Matrei without copying Matrei
 # landscape or changing its pixels. Forest, cliffs and ruts do not warp.
 xedge=np.broadcast_to(np.arange(W,dtype=np.float32)[None,:],(24,W))
 yedge=np.broadcast_to(np.arange(1000,1024,dtype=np.float32)[:,None],(24,W))
 ref=matrei_display(matrei,xedge,yedge)
 a=cv2.cvtColor(out,cv2.COLOR_RGB2LAB).astype(np.float32)
 b=cv2.cvtColor(ref,cv2.COLOR_RGB2LAB).astype(np.float32)
 delta=np.median(b[8:22],axis=0)-np.median(a[3:20],axis=0)
 for k,cap in enumerate((26,10,10)):
  delta[:,k]=cv2.GaussianBlur(np.clip(delta[:,k],-cap,cap)[None,:],
                              (0,0),38)[0]
 depth=285+26*np.sin(np.arange(W)/93)+17*np.sin(np.arange(W)/47)
 alpha=smooth((depth[None,:]-yy)/depth[None,:])*.84
 alpha*=1-.38*np.exp(-.5*((xx-466)/65)**2)
 a+=alpha[:,:,None]*delta[None,:,:]
 out=cv2.cvtColor(np.uint8(np.clip(a,0,255)),cv2.COLOR_LAB2RGB)
 # Exact original photographed cartway geometry; no new synthetic stripe.
 assert out.shape==(H,W,3)
 return out

def stage(html,west_jpg):
 if MARK in html:
  # Keep the same isolated preview mode, replacing only its source art.
  pass
 pattern=r'(?<!\\w)ART_WEST="data:image/[^;]+;base64,[^"]+"'
 matches=list(re.finditer(pattern,html))
 if len(matches)!=1:raise RuntimeError('WEST image selector changed')
 m=matches[0]
 replacement='ART_WEST="data:image/jpeg;base64,'+base64.b64encode(west_jpg).decode()+'"'
 html=html[:m.start()]+replacement+html[m.end():]
 needle='const southArtSource='
 if html.count(needle)!=1:raise RuntimeError('SOUTH selector changed')
 if MARK not in html:
  html=html.replace(needle,
   'const SOUTH_UNIFIED_NATIVE_PREVIEW=SOUTH_ART_MODE==="coherent"; /* '+MARK+' */\n'
   'const southArtSource=SOUTH_UNIFIED_NATIVE_PREVIEW'
   ' ? "art-reviews/v267-original-source/south-unified-native-border-unapproved.webp" : ',1)
 assert html.count('const southRoad=')==1 and html.count('const westRoad=')==1
 assert '[1536,478]' in html and '[466,0]' in html
 return html

def main():
 html=HTML.read_text(encoding='utf-8')
 if MARK in html and WEST_OUT.exists() and SOUTH_OUT.exists():
  print('Updating the SAME source art; no additional preview version')
 matrei=matrei_photo(html)
 west=np.asarray(Image.open(WEST).convert('RGB'))
 south=np.asarray(Image.open(SOUTH).convert('RGB'))
 assert west.shape==south.shape==(H,W,3)
 new_west=grade_west(west,matrei)
 new_south=grade_south(south,matrei)
 assert np.array_equal(new_west[:,:950],west[:,:950])
 # New original landscape composition intentionally changes the SOUTH landforms.
 wc=int((np.max(np.abs(new_west.astype(np.int16)-west.astype(np.int16)),axis=2)>8).sum())
 sc=int((np.max(np.abs(new_south.astype(np.int16)-south.astype(np.int16)),axis=2)>8).sum())
 assert wc>70000 and sc>350000,(wc,sc)
 Image.fromarray(new_west).save(WEST_OUT,'WEBP',quality=95,method=6)
 Image.fromarray(new_south).save(SOUTH_OUT,'WEBP',quality=95,method=6)
 buff=io.BytesIO()
 Image.fromarray(new_west).save(buff,'JPEG',quality=94,subsampling=0,optimize=True)
 HTML.write_text(stage(html,buff.getvalue()),encoding='utf-8')
 board=Image.new('RGB',(1536,1058),'#19251d')
 for i,(before,after,name) in enumerate(((west,new_west,'WEST'),(south,new_south,'SOUTH'))):
  y=i*529
  board.paste(Image.fromarray(before).resize((768,512)),(0,y+17))
  board.paste(Image.fromarray(after).resize((768,512)),(768,y+17))
  d=ImageDraw.Draw(board)
  d.text((10,y+2),name+' native original source',fill='white')
  d.text((780,y+2),name+' edge-harmonized original - UNAPPROVED',fill='white')
 board.save(SHEET,'WEBP',quality=86,method=6)
 REVIEW.write_text(
  '# Original WEST cirque + reauthored SOUTH limestone valley — UNAPPROVED\n\n'
  'WEST remains a complete independent high-resolution original cirque photo, '
  'graded only near its road-bearing border. SOUTH is a materially reauthored '
  '1536x1024 photographic Alpine landscape: an independent overhead limestone '
  'and meadow source supplies its western hillside; the original native SOUTH '
  'photograph supplies the eastern conifer forest, natural river, stone bridge '
  'and the exact existing V123 cartway corridor. The abandoned base-photo '
  'road was source-inpainted before integration, preventing a duplicate road. '
  'A broad terrain-aware multiscale photo blend follows the hillside, not a '
  'rectangular green gap. No Matrei scenery is copied, no trees are warped, '
  'no artificial tan cartway is painted. This is fictional 1780-1880 game art, '
  'not verified historical topography.\n\n'
  f'WEST significantly changed pixels: {wc}; SOUTH: {sc}.\n'
  'WEST source: '+hashlib.sha256(WEST.read_bytes()).hexdigest()+'\n'
  'SOUTH source: '+hashlib.sha256(SOUTH.read_bytes()).hexdigest()+'\n'
  'Review the SAME isolated ?southArt=coherent mode, comparing WEST/MATREI/SOUTH '
  'actual 390x844 mobile WebKit and Chromium screenshots and real tap-to-march. '
  'Matrei/SOUTH horizontal boundary may still be visibly abrupt; this is '
  'not approved. V121/V123/V94, sprites, saves and production unchanged. '
  'Production RED.\n',encoding='utf-8')
 print(json.dumps({'west_changed_pixels':wc,'south_changed_pixels':sc,
  'west_art':str(WEST_OUT.relative_to(ROOT)),
  'south_art':str(SOUTH_OUT.relative_to(ROOT)),'status':'UNAPPROVED'}))

if __name__=='__main__':main()

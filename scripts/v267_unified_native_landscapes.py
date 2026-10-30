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

def grade_south(native,matrei):
 # Entire SOUTH is ONE unwarped original photo, including its original
 # cartway, forest, river, stone bridge and banks.
 xx=np.broadcast_to(np.arange(W,dtype=np.float32)[None,:],(18,W))
 yy=np.broadcast_to(np.arange(995,1013,dtype=np.float32)[:,None],(18,W))
 edge=matrei_display(matrei,xx,yy)
 a=cv2.cvtColor(native,cv2.COLOR_RGB2LAB).astype(np.float32)
 b=cv2.cvtColor(edge,cv2.COLOR_RGB2LAB).astype(np.float32)
 ref=np.median(b,axis=0)
 own=np.median(a[6:30],axis=0)
 delta=ref-own
 for k,cap in enumerate((24,10,10)):
  delta[:,k]=np.clip(delta[:,k],-cap,cap)
 delta=np.stack([cv2.GaussianBlur(delta[:,k].reshape(1,W),(0,0),57)[0]
                 for k in range(3)],axis=1)
 y,x=np.mgrid[:H,:W].astype(np.float32)
 fade=smooth((370-y)/370)*.88
 # Keep physical x466 ruts unmodified, only surrounding photo lighting.
 fade*=1-.75*np.exp(-.5*((x-466)/56)**2)
 corrected=np.uint8(np.clip(a+fade[:,:,None]*delta[None,:,:],0,255))
 out=cv2.cvtColor(corrected,cv2.COLOR_LAB2RGB)
 out[370:]=native[370:]
 # No pasted forest, river patch, gold frame, road stripe or Matrei pixels.
 return out

def stage(html,west_jpg):
 if MARK in html:raise RuntimeError('Candidate already staged')
 pattern=r'(?<!\\w)ART_WEST="data:image/[^;]+;base64,[^"]+"'
 matches=list(re.finditer(pattern,html))
 if len(matches)!=1:raise RuntimeError('WEST image selector changed')
 m=matches[0]
 replacement='ART_WEST="data:image/jpeg;base64,'+base64.b64encode(west_jpg).decode()+'"'
 html=html[:m.start()]+replacement+html[m.end():]
 needle='const southArtSource='
 if html.count(needle)!=1:raise RuntimeError('SOUTH selector changed')
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
  print('Already staged; do not create repeat cosmetic versions');return
 matrei=matrei_photo(html)
 west=np.asarray(Image.open(WEST).convert('RGB'))
 south=np.asarray(Image.open(SOUTH).convert('RGB'))
 assert west.shape==south.shape==(H,W,3)
 new_west=grade_west(west,matrei)
 new_south=grade_south(south,matrei)
 assert np.array_equal(new_west[:,:950],west[:,:950])
 assert np.array_equal(new_south[370:],south[370:])
 wc=int((np.max(np.abs(new_west.astype(np.int16)-west.astype(np.int16)),axis=2)>8).sum())
 sc=int((np.max(np.abs(new_south.astype(np.int16)-south.astype(np.int16)),axis=2)>8).sum())
 assert wc>70000 and sc>65000,(wc,sc)
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
  '# Coherent WEST and SOUTH single-source Alpine art — UNAPPROVED\n\n'
  'Both complete 1536x1024 landscape artworks retain their respective '
  'single original photographic compositions. WEST is a rocky cirque '
  'with a small mountain tarn; SOUTH is a separate meadow/river/stone '
  'bridge valley. No cloned trees, no synthetic green gaps, no whole-image '
  'warps and no artificial cartway strokes. Original photographic roads '
  'and bridge remain in place. Broad edge lighting is matched to the '
  'immutable V121 Matrei crop; Matrei pixels are not copied into either '
  'new artwork. These are fictional Alpine 1780–1880 game-art prototypes, '
  'not verified historic geography.\n\n'
  f'WEST significantly changed pixels: {wc}; SOUTH: {sc}.\n'
  'WEST source: '+hashlib.sha256(WEST.read_bytes()).hexdigest()+'\n'
  'SOUTH source: '+hashlib.sha256(SOUTH.read_bytes()).hexdigest()+'\n'
  'Preview: ?southArt=coherent (WEST is this isolated candidate default). '
  'Real iPhone-sized WebKit/Chromium comparisons and WEST→MATREI→SOUTH '
  'march required before approval. No V121, V123, V94, sprites, saves or '
  'production changes. Production RED.\n',encoding='utf-8')
 print(json.dumps({'west_changed_pixels':wc,'south_changed_pixels':sc,
  'west_art':str(WEST_OUT.relative_to(ROOT)),
  'south_art':str(SOUTH_OUT.relative_to(ROOT)),'status':'UNAPPROVED'}))

if __name__=='__main__':main()

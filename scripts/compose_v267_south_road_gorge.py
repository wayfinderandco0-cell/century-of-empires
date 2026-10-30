#!/usr/bin/env python3
"""V267 SOUTH photographic river relocation; fictional art, not historical topo.

Compose a genuinely different northern gorge using rigid native rock/meadow
replacement and photographed riverbank material. No global SOUTH warp,
warped trees, invented settlements, or changes to V121/V123/gameplay.
"""
from pathlib import Path
from PIL import Image, ImageDraw
import numpy as np, cv2, hashlib, json
R=Path(__file__).resolve().parents[1]
SRC=R/'art-reviews/v267-original-source/south-bridge-contact-unapproved.webp'
OUT=R/'art-reviews/v267-original-source/south-river-throat-recomposed-unapproved.webp'
native=np.asarray(Image.open(SRC).convert('RGB'))
H,W=native.shape[:2]; assert (W,H)==(1536,1024)
N=445
yy,xx=np.mgrid[:N,:W].astype(np.float32)
Y=[0,50,100,150,200,250,300,350,410,500]
X=[674,651,653,670,740,816,852,892,982,1050]
oldcenter=np.interp(np.arange(N),Y,X).astype(np.float32)
shift=np.interp(np.arange(N),[0,70,130,210,290,365,420,444],
                [258,258,238,171,86,16,0,0]).astype(np.float32)
def smooth(v):
 v=np.clip(v,0,1);return v*v*(3-2*v)
# Rigid, native SOUTH rocky meadow photo (x0..332), placed over old stream.
# No inpainting: photo has actual grass, boulders, shrubs and original grain.
left=535+10*np.sin(yy/53)
right=872+19*np.sin(yy/83)
bottom=335+21*np.sin(xx/79)
cover=(smooth((xx-left)/24)*smooth((right-xx)/32)*smooth((bottom-yy)/43)).astype(np.float32)
cover[:,:530]=0
rock=cv2.remap(native[:N],(xx-540).astype(np.float32),yy,cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT_101)
base=np.uint8(np.clip(native[:N].astype(np.float32)*(1-cover[:,:,None])+rock.astype(np.float32)*cover[:,:,None],0,255))
del rock
# Relocate only native photographed gorge + banks into x950 northern Matrei
# water exit. 2D native stone/forest source is sampled from its own positions.
newcenter=oldcenter+shift
donor=cv2.remap(native[:N],(xx-shift[:,None]).astype(np.float32),yy,cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT_101)
dist=np.abs(xx-newcenter[:,None])
width=np.interp(np.arange(N),[0,100,200,300,380,445],[115,123,142,157,172,180]).astype(np.float32)
alpha=(smooth((width[:,None]+28-dist)/38)*(1-smooth((yy-290)/125))).astype(np.float32)
alpha[:,:545]=0
outtop=np.uint8(np.clip(base.astype(np.float32)*(1-alpha[:,:,None])+donor.astype(np.float32)*alpha[:,:,None],0,255))
del base,donor
# Source river's original blue-green tonal variation remains intact.
out=native.copy();out[:N]=outtop;out[:,:530]=native[:,:530];out[N:]=native[N:]
assert np.array_equal(out[:,:530],native[:,:530])
assert np.array_equal(out[N:],native[N:])
changed=int(np.count_nonzero(np.max(np.abs(out.astype(np.int16)-native.astype(np.int16)),axis=2)>8))
Image.fromarray(out).save(OUT,'WEBP',quality=93,method=6)
sheet=Image.new('RGB',(1200,460),'#17231c');d=ImageDraw.Draw(sheet)
for i,(a,title) in enumerate([(native,'BEFORE native SOUTH'),(out,'AFTER relocated gorge + native meadow')]):
 im=Image.fromarray(a).crop((280,0,1280,650)).resize((585,390))
 sheet.paste(im,(i*600+7,36));d.text((i*600+12,12),title,fill='#f7e7bd')
sheet.save(R/'art-reviews/v267-river-throat-source-before-after.jpg',quality=75,optimize=True)
print(json.dumps({'changed_pixels':changed,'bytes':OUT.stat().st_size,
 'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),
 'candidate_sha256':hashlib.sha256(OUT.read_bytes()).hexdigest(),
 'road_x_below_530_unchanged':True,'y_at_or_below_445_unchanged':True}))

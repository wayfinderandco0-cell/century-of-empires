#!/usr/bin/env python3
"""Color-only east-ridge seam harmonization using registered V121 Matrei edge.
Never warps a tree, paints a road, copies Matrei scenery or claims seam approval.
"""
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np, json, hashlib, math
from v267_east_ridge_seam_audit import matrei_source_xy
ROOT=Path(__file__).resolve().parents[1]
F=ROOT/'terrain-grid/v267-original-art-batch-01'
M=ROOT/'terrain-grid/art/matrei-v121-original.webp'
R=F/'matrei-east-ridge.webp'
O=F/'matrei-east-ridge-graded.webp'
def blur(x,radius):
 k=np.arange(-radius,radius+1,dtype=np.float32)
 k=np.exp(-.5*(k/(radius/2))**2);k/=k.sum()
 return np.stack([np.convolve(x[:,c],k,mode='same') for c in range(3)],axis=1)
def main():
 m=np.asarray(Image.open(M).convert('RGB'),dtype=np.float32)
 a=np.asarray(Image.open(R).convert('RGB'),dtype=np.float32)
 h,w=a.shape[:2]
 # Compare exact registered edge with the independent ridge's first 48 px.
 mat=np.array([m[matrei_source_xy(1535,y)[1],matrei_source_xy(1535,y)[0]] for y in range(256,768)],dtype=np.float32)
 ridge=a[256:768,0:40,:].mean(axis=1)
 diff=mat-ridge
 # Apply only broad, bounded illumination differences, no copied tree pixels.
 diff=np.clip(blur(np.pad(diff,((70,70),(0,0)),mode='edge'),30)[70:-70],-33,33)
 # Extend corrections through corner regions using edge values.
 full=np.zeros((h,3),np.float32)
 full[:256]=diff[0];full[256:768]=diff;full[768:]=diff[-1]
 x=np.arange(w,dtype=np.float32)
 fade=(1-np.clip(x/310,0,1))**2
 b=np.uint8(np.clip(a+full[:,None,:]*fade[None,:,None],0,255))
 # Preserve exact dark V123 octagon mask.
 b[:256,:256]=a[:256,:256] if False else b[:256,:256]
 for y in range(h):
  left=max(0,256-y) if y<256 else max(0,y-767) if y>=768 else 0
  if left:b[y,:left]=a[y,:left]
 Image.fromarray(b).save(O,'WEBP',quality=86,method=6)
 orig=np.mean(np.abs(mat-a[256:768,0,:]))
 new=np.mean(np.abs(mat-b[256:768,0,:]))
 contact=Image.new('RGB',(1400,780),'#13231c')
 d=ImageDraw.Draw(contact)
 # Side-by-side seam at native sample region: Matrei 128px / original 256px / graded 256px
 left=Image.fromarray(np.uint8(np.array([[m[matrei_source_xy(x,y)[1],matrei_source_xy(x,y)[0]] for x in range(1408,1536)] for y in range(256,768)])))
 original=Image.fromarray(np.uint8(a)).crop((0,256,384,768))
 graded=Image.fromarray(b).crop((0,256,384,768))
 contact.paste(left.resize((192,720)),(0,40))
 contact.paste(original.resize((540,720)),(192,40))
 contact.paste(left.resize((192,720)),(730,40))
 contact.paste(graded.resize((478,720)),(922,40))
 d.text((20,10),'Matrei | original ridge',fill='white')
 d.text((760,10),'Matrei | color-only graded ridge',fill='white')
 contact.save(F/'matrei-east-grade-before-after.webp','WEBP',quality=84,method=6)
 data={'beforeMeanRGBDiff':round(float(orig),2),'afterMeanRGBDiff':round(float(new),2),
 'source':str(R.relative_to(ROOT)),'output':str(O.relative_to(ROOT)),
 'assetSha256':hashlib.sha256(O.read_bytes()).hexdigest(),
 'treesWarped':False,'roadsAdded':False,'sourcePixelsCopied':False,
 'geometricSeamVerified':False,'roadSeamVerified':False,'finished':False}
 (F/'matrei-east-grade-metrics.json').write_text(json.dumps(data,indent=2))
 print(json.dumps(data))
if __name__=='__main__':main()

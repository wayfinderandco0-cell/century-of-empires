#!/usr/bin/env python3
"""V222 isolated ARTISTIC source-quilt study; never claim surveyed geography.

Use only original V121 painting pixels, at original 1:1 scale, to construct two
distinct non-identical 1536x1024 neighboring scenic surfaces. No 2023 imagery,
generated noise, historic cartways, invented river/bridge, or change to V121/V123.
Original landscape painting is a STYLE/MATERIAL source, not west/south geography.
"""
import argparse
import base64
import hashlib
import io
import json
import random
import re
import subprocess
from collections import Counter
from pathlib import Path
from PIL import Image, ImageChops, ImageStat

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'terrain-v222/assets'
W,H=1536,1024
PATCH,STEP,OVERLAP=128,112,16
PINNED={
 'v121-octagon-1-painted-road.html':'4c6aa5cda9e7c359b6d2a49d5b5fe8a597346382',
 'terrain-grid/v123-atlas.js':'09f04b4062e24fbacbb645307462cdddce2b2aa3'
}
# Explicit natural-cover research ROIs in original 1536x1024 V121 painting.
# A crop within these bounds is NOT guaranteed to exclude every manmade pixel.
# Reviewer must inspect full-resolution generated artwork, not just this list.
AREAS={
 'rock':[(165,100,380,320),(355,35,565,205),(550,65,715,215),
         (565,250,720,390),(190,220,355,390)],
 'forest':[(150,300,350,445),(625,195,770,405),(945,700,1125,900),
           (700,785,850,960),(990,100,1155,270),(975,600,1135,765)],
 'meadow':[(150,565,350,710),(350,570,540,715),(1115,170,1290,300),
           (1110,690,1285,850),(410,780,590,940)]
}
FALSE=('sourceRegisteredToV123','historicRoadsVerified','periodSafe',
       'gameArtApproved','physicalIPhoneApproved','productionApproved')
def require(ok,why):
 if not ok:raise ValueError('V222 fail-closed: '+why)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def pinned():
 for name,expected in PINNED.items():
  actual=subprocess.check_output(['git','hash-object',name],cwd=ROOT,text=True).strip()
  require(actual==expected,'protected original changed: '+name)
def original():
 html=(ROOT/'v121-octagon-1-painted-road.html').read_text()
 match=re.search(r"source\.src='data:image/webp;base64,([^']+)'",html)
 require(match is not None,'original Matrei painting missing')
 im=Image.open(io.BytesIO(base64.b64decode(match.group(1)))).convert('RGB')
 require(im.size==(W,H),'original Matrei dimensions changed')
 return im
def choose_category(tile,x,y,rng):
 fy=(y+PATCH/2)/H
 fx=(x+PATCH/2)/W
 if tile=='west':
  weights={'rock':(0.72 if fy<.33 else .11),
           'forest':(.66 if .22<fy<.83 else .26),
           'meadow':(.72 if fy>.70 else .20)}
 else:
  weights={'rock':(.34 if fx<.30 and fy<.48 else .06),
           'forest':(.78 if fy<.54 else .26),
           'meadow':(.76 if fy>.51 else .15)}
 total=sum(weights.values());v=rng.random()*total
 for key,value in weights.items():
  v-=value
  if v<=0:return key
 return 'forest'
def candidate(source,category,rng,used):
 for _ in range(100):
  box=rng.choice(AREAS[category])
  sx=rng.randint(box[0],box[2]-PATCH)
  sy=rng.randint(box[1],box[3]-PATCH)
  key=(sx,sy)
  if key in used:continue
  return key,source.crop((sx,sy,sx+PATCH,sy+PATCH))
 raise ValueError('V222 ran out of distinct original-painting source crops')
def seam_score(canvas,patch,x,y,w,h):
 score=0.
 if x:
  old=canvas.crop((x,y,x+min(OVERLAP,w),y+h))
  new=patch.crop((0,0,min(OVERLAP,w),h))
  score+=sum(ImageStat.Stat(ImageChops.difference(old,new)).mean)/3
 if y:
  old=canvas.crop((x,y,x+w,y+min(OVERLAP,h)))
  new=patch.crop((0,0,w,min(OVERLAP,h)))
  score+=sum(ImageStat.Stat(ImageChops.difference(old,new)).mean)/3
 return score
def mask_for(w,h,left,top):
 # Source-edge feathering only, no noise, no invented pixels or new landmarks.
 m=Image.new('L',(w,h),255)
 vals=bytearray(w*h)
 for yy in range(h):
  ay=255 if not top else min(255,int(255*(yy+1)/OVERLAP))
  for xx in range(w):
   ax=255 if not left else min(255,int(255*(xx+1)/OVERLAP))
   vals[yy*w+xx]=min(ax,ay)
 m.frombytes(bytes(vals))
 return m
def compose(source,tile,used):
 rng=random.Random(22291 if tile=='west' else 22292)
 canvas=Image.new('RGB',(W,H),'#384a37')
 patches=[]
 counts=Counter()
 for y in range(0,H,STEP):
  for x in range(0,W,STEP):
   w,h=min(PATCH,W-x),min(PATCH,H-y)
   category=choose_category(tile,x,y,rng)
   options=[]
   for _ in range(28):
    key,im=candidate(source,category,rng,used)
    crop=im.crop((0,0,w,h))
    # Prefer genuine material with matching neighboring light/color at seams.
    score=seam_score(canvas,crop,x,y,w,h)
    # Discourage adjacent near-identical swatches of the same source area.
    if patches:
     previous=patches[-1]['source']
     if abs(key[0]-previous[0])+abs(key[1]-previous[1])<128:score+=18
    options.append((score,key,crop))
   score,key,crop=min(options,key=lambda v:v[0])
   require(key not in used,'source crop reused')
   used.add(key)
   region=canvas.crop((x,y,x+w,y+h))
   if x or y:
    crop=Image.composite(crop,region,mask_for(w,h,bool(x),bool(y)))
   canvas.paste(crop,(x,y))
   counts[category]+=1
   patches.append({'category':category,'source':list(key),
                   'sourceRect':[key[0],key[1],key[0]+w,key[1]+h],
                   'destinationRect':[x,y,x+w,y+h]})
 return canvas,patches,dict(counts)
def build(out):
 pinned()
 out.mkdir(parents=True,exist_ok=True)
 source=original()
 used=set()
 manifest={
  'version':222,'kind':'ISOLATED_ORIGINAL_MATREI_MATERIAL_QUILT_STUDY',
  'originalMatreiSource':'v121-octagon-1-painted-road.html',
  'originalMatreiGitBlob':PINNED['v121-octagon-1-painted-road.html'],
  'materialAttribution':'Original V121 Century of Empires painting; reuse within this game only',
  'noModernOrthophotoUsed':True,'noNoiseAdded':True,
  'noUpscaling':True,'patchSize':PATCH,'step':STEP,'overlap':OVERLAP,
  'nativeCellPixels':[W,H],'sourceRectsGloballyUnique':True,
  'sourceMaterialNotGeography':True,'westSouthTerrainNotSurveyed':True,
  'bridgeAndRoadGeometryUnchanged':True,'centerMatreiArtworkUnchanged':True,
  'allManmadeSourcePixelsExcluded':False,'humanVisualApproval':False,
  'areas':AREAS,'cells':[],**{k:False for k in FALSE}
 }
 for tile in ('west','south'):
  im,patches,counts=compose(source,tile,used)
  name=tile+'-quilt.webp'
  im.save(out/name,'WEBP',quality=82,method=6)
  raw=(out/name).read_bytes()
  # Embedding allows GitHub connector review of exact new image pixels.
  (out/(tile+'-data.js')).write_text(
   'window.V222'+tile.capitalize()+'Data="data:image/webp;base64,'+
   base64.b64encode(raw).decode('ascii')+'";\n')
  manifest['cells'].append({'tile':tile,'file':name,'dataFile':tile+'-data.js',
    'sha256':sha(raw),'patches':patches,'categories':counts,
    'nativePixels':[W,H],'sourceGeoregistered':False})
 (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 verify(out)
 print(json.dumps({'version':222,'cells':[(c['tile'],len(c['patches']),
  c['categories']) for c in manifest['cells']],'approved':False},indent=2))
def verify(out):
 pinned()
 m=json.loads((out/'manifest.json').read_text())
 require(m['version']==222 and m['sourceMaterialNotGeography'] is True,'not an artistic study')
 require(m['noModernOrthophotoUsed'] is True and m['noNoiseAdded'] is True,'wrong material')
 require(m['sourceRectsGloballyUnique'] is True and m['noUpscaling'] is True,'false source claims')
 require(m['centerMatreiArtworkUnchanged'] is True and m['bridgeAndRoadGeometryUnchanged'] is True,'protected game changed')
 require(m['allManmadeSourcePixelsExcluded'] is False and m['humanVisualApproval'] is False,'unsafe source claim')
 for f in FALSE:require(m[f] is False,'false approval '+f)
 require([c['tile'] for c in m['cells']]==['west','south'],'two distinct neighbors required')
 seen=set()
 for c in m['cells']:
  name=c['tile'];raw=(out/c['file']).read_bytes()
  require(sha(raw)==c['sha256'],'painted cell tampered: '+name)
  with Image.open(io.BytesIO(raw)) as im:require(im.size==(W,H),'resized source art')
  js=(out/c['dataFile']).read_text()
  prefix='window.V222'+name.capitalize()+'Data="data:image/webp;base64,'
  require(js.startswith(prefix) and js.endswith('";\n'),'missing embedded phone asset')
  require(base64.b64decode(js[len(prefix):-3])==raw,'phone asset not equal original output')
  require(len(c['patches'])>=100,'incomplete full-cell coverage')
  for p in c['patches']:
   rect=p['sourceRect'];xy=tuple(p['source'])
   require(xy not in seen,'duplicate original painting crop')
   seen.add(xy)
   require(any(rect[0]>=b[0] and rect[1]>=b[1] and rect[2]<=b[2] and rect[3]<=b[3]
    for b in AREAS[p['category']]),'unreviewed material region')
   dst=p['destinationRect']
   require(dst[2]>dst[0] and dst[3]>dst[1] and
           0<=dst[0]<W and 0<=dst[1]<H and dst[2]<=W and dst[3]<=H,
           'invalid patch placement')
 return True
if __name__=='__main__':
 p=argparse.ArgumentParser()
 p.add_argument('--output',type=Path,default=OUT)
 p.add_argument('--verify',action='store_true')
 a=p.parse_args()
 if a.verify:verify(a.output);print('V222 original painting provenance VERIFIED; game art approval FALSE')
 else:build(a.output)

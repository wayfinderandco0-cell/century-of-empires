#!/usr/bin/env python3
"""V224 reproducible native-pixel, LICENSED illustrative WEST/SOUTH art trial.
These photos depict Kosovo, NOT Austrian geography or the year 1780.
No source road, bridge or settlement is authenticated as playable.
"""
import argparse,base64,hashlib,io,json,subprocess
from pathlib import Path
from PIL import Image,ImageEnhance,ImageChops
ROOT=Path(__file__).resolve().parents[1]
DIR=ROOT/'terrain-v224'
W,H=1536,1024
PROTECTED={'v121-octagon-1-painted-road.html':'4c6aa5cda9e7c359b6d2a49d5b5fe8a597346382',
 'terrain-grid/v123-atlas.js':'09f04b4062e24fbacbb645307462cdddce2b2aa3'}
SOURCES={
 'west':{'file':'west-wikimedia-3072-ccby.jpg','sourceTitle':'Drone image of Sharr Mountains during Spring Season.jpg',
         'crop':[280,850,1816,1874], 'license':'CC BY 4.0','author':'SUHEJLO',
         'url':'https://commons.wikimedia.org/wiki/File:Drone_image_of_Sharr_Mountains_during_Spring_Season.jpg',
         'knownModernRoadInCrop':False},
 'south':{'file':'south-wikimedia-3072-ccby.jpg','sourceTitle':'Aerial photo of Sharr Mountains in Kosovo.jpg',
          'crop':[0,950,1536,1974],'license':'CC BY 4.0','author':'SUHEJLO',
          'url':'https://commons.wikimedia.org/wiki/File:Aerial_photo_of_Sharr_Mountains_in_Kosovo.jpg',
          'knownModernRoadInCrop':True}}
FALSE=('sourceRegisteredToV123','historicRoadsVerified','periodSafe','gameArtApproved',
       'physicalIPhoneApproved','productionApproved','bridgeBanksVerified')
def require(ok,msg):
 if not ok:raise ValueError('V224 fail closed: '+msg)
def sha(b):return hashlib.sha256(b).hexdigest()
def pinned():
 for name,expected in PROTECTED.items():
  actual=subprocess.check_output(['git','hash-object',name],cwd=ROOT,text=True).strip()
  require(actual==expected,'protected source altered: '+name)
def render(source,box):
 require(source.size[0]>=box[2] and source.size[1]>=box[3],'source bounds')
 require(box[2]-box[0]==W and box[3]-box[1]==H,'not native pixel crop')
 im=source.crop(tuple(box)).convert('RGB')
 return ImageEnhance.Brightness(ImageEnhance.Color(im).enhance(.84)).enhance(.84)
def build():
 pinned(); (DIR/'assets').mkdir(parents=True,exist_ok=True)
 manifest={'version':224,'kind':'ISOLATED_LICENSED_OBLIQUE_NATURAL_COVER_ART_STUDY',
 'nativeCellPixels':[W,H],'twoIndependentPhotoSources':True,
 'originalMatreiArtworkUnchanged':True,'V123MovementGraphUnchanged':True,
 'sourceMaterialNotGeography':True,'actualSourceRegion':'Sharr Mountains, Kosovo (NOT Austrian Alps)',
 'historicDate':'NOT 1780','modernFeaturesFullyExcluded':False,'humanVisualApproval':False,
 'knownModernRoadVisibleInSouth':True,'sources':[],**{k:False for k in FALSE}}
 for tile,plan in SOURCES.items():
  source_path=DIR/'source'/plan['file'];raw=source_path.read_bytes()
  with Image.open(io.BytesIO(raw)) as src:
   im=render(src.convert('RGB'),plan['crop']);native=list(src.size)
  target=DIR/'assets'/(tile+'.webp');im.save(target,'WEBP',quality=88,method=5)
  data=target.read_bytes();(DIR/'assets'/(tile+'-data.js')).write_text(
    'window.V224'+tile.capitalize()+'Data="data:image/webp;base64,'+
    base64.b64encode(data).decode('ascii')+'";\n')
  manifest['sources'].append({'tile':tile,'original':str(source_path.relative_to(ROOT)),
    'sourceSha256':sha(raw),'sourceDimensions':native,'sourceRect':plan['crop'],
    'output':str(target.relative_to(ROOT)),'outputSha256':sha(data),
    'dataFile':str((DIR/'assets'/(tile+'-data.js')).relative_to(ROOT)),
    'nativeOutputPixels':[W,H],'author':plan['author'],'license':plan['license'],
    'licenseUrl':'https://creativecommons.org/licenses/by/4.0/',
    'sourcePage':plan['url'],'sourceTitle':plan['sourceTitle'],
    'transformation':'Wikimedia 3072px thumbnail re-encoded as JPEG quality 62; native 1536x1024 crop, color saturation x0.84, brightness x0.84, WebP quality 88',
    'knownModernRoadInCrop':plan['knownModernRoadInCrop'],
    'historicalGeographyVerified':False})
 (DIR/'assets'/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 verify()
 print(json.dumps({'version':224,'sources':[(s['tile'],s['sourceSha256'][:16],s['outputSha256'][:16]) for s in manifest['sources']],
  'productionApproved':False},indent=2))
def verify():
 pinned();m=json.loads((DIR/'assets'/'manifest.json').read_text())
 require(m['version']==224 and m['kind']=='ISOLATED_LICENSED_OBLIQUE_NATURAL_COVER_ART_STUDY','wrong manifest')
 require(m['nativeCellPixels']==[W,H] and m['sourceMaterialNotGeography'] is True,'false geography')
 require(m['actualSourceRegion'].startswith('Sharr Mountains, Kosovo'),'false Austrian source')
 require(m['knownModernRoadVisibleInSouth'] is True and m['modernFeaturesFullyExcluded'] is False,'modern feature concealed')
 require(m['humanVisualApproval'] is False,'human approval forged')
 for f in FALSE:require(m.get(f) is False,'false approval '+f)
 require(len(m['sources'])==2 and {s['tile'] for s in m['sources']}=={'west','south'},'missing cell')
 require(len({s['sourceSha256'] for s in m['sources']})==2,'reused source identity')
 for s in m['sources']:
  plan=SOURCES[s['tile']];require(s['sourceRect']==plan['crop'] and s['sourcePage']==plan['url'],'source provenance changed')
  require(s['license']=='CC BY 4.0' and s['author']=='SUHEJLO','missing attribution')
  raw=(ROOT/s['original']).read_bytes();require(sha(raw)==s['sourceSha256'],'pinned Wikimedia derivative tampered')
  with Image.open(io.BytesIO(raw)) as im: expected=render(im.convert('RGB'),s['sourceRect'])
  encoded=(ROOT/s['output']).read_bytes();require(sha(encoded)==s['outputSha256'],'output tampered')
  with Image.open(io.BytesIO(encoded)) as im:
   require(im.size==(W,H),'output size');
   # Lossy WebP is expected; gross color/position substitution must fail.
   diff=ImageChops.difference(expected,im.convert('RGB'))
   from PIL import ImageStat
   require(max(ImageStat.Stat(diff).mean)<6,'source-derived visual pixel drift')
  js=(ROOT/s['dataFile']).read_text();require(base64.b64decode(js.split('base64,',1)[1].split('"',1)[0])==encoded,'embedded image drift')
 require(next(s for s in m['sources'] if s['tile']=='south')['knownModernRoadInCrop'] is True,'modern road hidden')
 return m
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--verify',action='store_true');a=p.parse_args();verify() if a.verify else build()

#!/usr/bin/env python3
"""V263: build a self-contained, offline, playable V249 original-art experiment.
No changes to V249/V121/V123/V94, army sprites, campaigns, or user saves.
All imagery is fictional, unregistered, unapproved; no production promotion.
"""
import argparse, base64, hashlib, json, re
from pathlib import Path
from PIL import Image

PINS={'west':'36a32828a74453ac105faf8af3729c46a42acd55d12d381d8a667d7022e1e1a7',
      'south':'d63f5f056a682f976bafff95f04b2b71e0bb4077f34f18e9a95b32cd72fb5ccb'}
SCRIPTS=['terrain-grid/v122-seam-engine.js','terrain-grid/v123-atlas.js',
 'terrain-grid/v152-survey-limits.js','terrain-grid/v144-geo-material.js',
 'terrain-v224/assets/west-data.js','terrain-v224/assets/south-data.js',
 'terrain-grid/v224-licensed-oblique-neighbors.js',
 'terrain-grid/v225-cartway-ground-contact.js',
 'terrain-grid/v226-artwork-contract.js','terrain-grid/v227-art-ingest.js',
 'terrain-grid/v236-authored-alpine.js']

def build(root,west,south,out):
 root=Path(root);html=(root/'v249-pinned-source-art-review.html').read_text()
 matrei=(root/'v121-octagon-1-painted-road.html').read_text()
 manifest=json.loads((root/'terrain-v224/assets/manifest.json').read_text())
 assert "const ROADS=" in matrei and 'source.src=' in matrei
 for name in SCRIPTS:
  tag=f'<script src="{name}"></script>'
  assert html.count(tag)==1,(name,'script tag missing/duplicated')
  script=(root/name).read_text()
  script=re.sub(r'</script',r'<\/script',script,flags=re.I)
  if name=='terrain-grid/v224-licensed-oblique-neighbors.js':
   original="const response=await fetch('terrain-v224/assets/manifest.json',{cache:'no-store'});"
   assert script.count(original)==1
   script=script.replace(original,'const response={ok:true,json:async()=>V263_MANIFEST};')
  html=html.replace(tag,'<script>\n'+script+'\n</script>')
 images={}
 for tile,path in [('west',west),('south',south)]:
  raw=Path(path).read_bytes();digest=hashlib.sha256(raw).hexdigest()
  assert digest==PINS[tile],(tile,'wrong original-image SHA256',digest)
  with Image.open(path) as im:assert im.size==(1536,1024) and im.format=='PNG'
  images[tile]=base64.b64encode(raw).decode('ascii')
 original="const html=await(await fetch('v121-octagon-1-painted-road.html')).text();"
 assert html.count(original)==1
 html=html.replace(original,'const html=V263_MATREI_HTML;')
 assert html.count('await loadPinnedPairFromQuery();')==1
 html=html.replace('await loadPinnedPairFromQuery();','await V263ImportPair();')
 html=html.replace('V249 PINNED SOURCE ART REVIEW','V263 OFFLINE EXACT-ART PLAYABLE CANDIDATE')
 html=html.replace('Photo-grade art imports render above rejected fallback · V123 cartways unchanged · NOT APPROVED',
  'Original V258 WEST + V260 SOUTH + protected Matrei · V123 unchanged · FICTIONAL ART · NOT APPROVED')
 html=html.replace('Default CC BY 4.0 rejected V224 source; imported art has NO VERIFIED LICENSE or geography · original V123 roads only',
  'V263 original fictional art · NOT surveyed geography or 1780 roads · V123 movement unchanged · PRODUCTION RED')
 # Only this isolated clone: show the actual baked cartway, not a thick fake highway.
 # Navigation/click targets and original Matrei roads remain EXACTLY as before.
 original="if(!rawArtReview||!imported){\n     for(const pts of Object.values(t.roads))paintNaturalTrailFinish(pts);\n    }else{"
 replacement="if(imported&&!rawArtReview){\n     // V263: show native physical cartway, not synthetic V194 highway ink.\n     // Original V123 movement and optional debug route remain unchanged.\n    }else if(!rawArtReview||!imported){\n     for(const pts of Object.values(t.roads))paintNaturalTrailFinish(pts);\n    }else{"
 assert html.count(original)==1,'V249 road overlay guard changed'
 html=html.replace(original,replacement)
 html=html.replace('get productionApproved(){return false}',
  'get v263ExactArtLoaded(){return V227ArtIngest.snapshot().cells.filter(Boolean).length===2},get productionApproved(){return false}')
 assert html.count('get v263ExactArtLoaded()')==1
 fallback=(Path(__file__).with_name('v263_sha256_fallback.js')).read_text()
 prelude=(fallback+'\nconst V263_MANIFEST='+json.dumps(manifest,separators=(',',':'))+
  ';\nconst V263_MATREI_HTML='+json.dumps(matrei).replace('<','\\u003c')+
  ';\nconst V263_PINS='+json.dumps(PINS,separators=(',',':'))+
  ';\nconst V263_IMAGES='+json.dumps(images,separators=(',',':'))+';\n')
 assert html.count("<script>\n'use strict';")==1
 html=html.replace("<script>\n'use strict';",'<script>\n'+prelude+"'use strict';")
 injector='''
async function V263ImportPair(){
 try{
  for(const id of ['west','south']){
   const bin=atob(V263_IMAGES[id]);const raw=new Uint8Array(bin.length);
   for(let i=0;i<bin.length;i++)raw[i]=bin.charCodeAt(i);
   const file=new File([raw],id+'-v263-UNAPPROVED.png',{type:'image/png'});
   await V227ArtIngest.importFile(id,file,artContract,{
    expectedSha256:V263_PINS[id],provenance:'ORIGINAL_FICTIONAL_UNVERIFIED'
   });
   delete V263_IMAGES[id];
  }
  rawArtReview=false;showPainted=true;staticDirty=true;renderDirty=true;
  statusEl.textContent='V263 two ORIGINAL images verified; V123 movement playable · ART UNAPPROVED';
 }catch(err){
  V227ArtIngest.reset();rawArtReview=true;staticDirty=true;renderDirty=true;
  statusEl.textContent='V263 ORIGINAL ART REJECTED: '+err.message;
  throw err;
 }
}
'''
 assert html.count('async function boot(){')==1
 html=html.replace('async function boot(){',injector+'\nasync function boot(){')
 assert 'await V263ImportPair();' in html
 assert 'get productionApproved(){return false}' in html
 assert 'if(last&&moving&&!rawArtReview)' in html
 out=Path(out);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(html)
 return {'version':263,'output':str(out),'bytes':out.stat().st_size,
  'exactSourceSHA256':PINS,'originalV249Changed':False,'offline':True,
  'historicalGeographyVerified':False,'bridgeBanksVerified':False,
  'strictV203Passed':False,'webkitTested':False,
  'userVisualApproval':False,'productionApproved':False}

if __name__=='__main__':
 p=argparse.ArgumentParser()
 p.add_argument('--root',required=True)
 p.add_argument('--west',required=True)
 p.add_argument('--south',required=True)
 p.add_argument('--out',required=True)
 a=p.parse_args()
 print(json.dumps(build(a.root,a.west,a.south,a.out),indent=2))

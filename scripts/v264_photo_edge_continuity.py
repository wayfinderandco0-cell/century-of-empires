#!/usr/bin/env python3
"""V264 isolated fictional source-pixel edge underlay; NO georegistration or approval.

Only derived pixels from the two exact local original PNGs are used. This is an
artistic border infill for an unapproved playable study, NOT 1780 geography.
No changes to Matrei source, V123 graph, original renderer or campaign.
"""
from pathlib import Path
from PIL import Image
import numpy as np
import base64
import hashlib
import argparse
import io

W,H=1536,1024
EXPECTED={
 'west':'36a32828a74453ac105faf8af3729c46a42acd55d12d381d8a667d7022e1e1a7',
 'south':'d63f5f056a682f976bafff95f04b2b71e0bb4077f34f18e9a95b32cd72fb5ccb'
}
def sha(p):
 return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def smoothstep(t):
 t=np.clip(t,0,1)
 return t*t*(3-2*t)

def make_patch(west,south,inner=140,outer=375):
 """Reflect source pixels into the Matrei alpha-mask outskirts, fading to zero.
 The reflected terrain is NOT a surveyed continuation. No new routes or roads.
 """
 if not (80<=inner<outer<=460):raise ValueError('bad fade geometry')
 w=np.asarray(Image.open(west).convert('RGB'),dtype=np.float32)
 s=np.asarray(Image.open(south).convert('RGB'),dtype=np.float32)
 if w.shape!=(H,W,3) or s.shape!=(H,W,3):
  raise ValueError('unexpected source dimensions')
 patch=np.zeros((H,W,4),dtype=np.uint8)
 xs=np.arange(outer)
 wa=(1-smoothstep((xs-inner)/(outer-inner))).astype(np.float32)
 sa=(1-smoothstep((np.arange(outer)-inner)/(outer-inner))).astype(np.float32)
 # At the western join, center x=0 samples WEST x=1535.
 # At the southern join, center y=1023 samples SOUTH y=0.
 wrgb=w[:,W-1-xs,:]
 srgb=s[np.arange(outer),:,:]
 rgb=np.zeros((H,W,3),dtype=np.float32)
 weights=np.zeros((H,W),dtype=np.float32)
 rgb[:,:outer,:]+=wrgb*wa[None,:,None]
 weights[:,:outer]+=wa[None,:]
 for d in range(outer):
  y=H-1-d
  rgb[y,:,:]+=srgb[d,:,:]*sa[d]
  weights[y,:]+=sa[d]
 valid=weights>1e-6
 patch[valid,:3]=np.clip(rgb[valid]/weights[valid,None],0,255).astype(np.uint8)
 alpha=np.zeros((H,W),dtype=np.float32)
 alpha[:,:outer]=wa[None,:]
 alpha[H-outer:,:]=np.maximum(alpha[H-outer:,:],sa[::-1,None])
 patch[:,:,3]=np.uint8(np.round(255*alpha))
 return Image.fromarray(patch,'RGBA')

def build(v263,west,south,output,patch_out=None):
 for k,p in [('west',west),('south',south)]:
  if sha(p)!=EXPECTED[k]:raise ValueError(f'{k} SHA256 mismatch')
 src=Path(v263).read_text()
 if 'V263ImportPair' not in src or 'if(showPainted)V227ArtIngest.paint(cx);' not in src:
  raise ValueError('unexpected V263 renderer')
 if 'V264_SEAM_UNDERLAY' in src:raise ValueError('already patched')
 patch=make_patch(west,south)
 if patch_out:patch.save(patch_out,optimize=True)
 b=io.BytesIO();patch.save(b,format='PNG',optimize=True)
 uri='data:image/png;base64,'+base64.b64encode(b.getvalue()).decode()
 source='const V264_SEAM_UNDERLAY=new Image();V264_SEAM_UNDERLAY.src="'+uri+'";\n'
 anchor='let staticFrame=null,staticDirty=true,staticBuilds=0,cacheHits=0,dynamicFrames=0;'
 if src.count(anchor)!=1:raise ValueError('unexpected static frame anchor')
 src=src.replace(anchor,source+anchor,1)
 needle='if(showPainted)V227ArtIngest.paint(cx);'
 replacement=needle+'''
 // V264 fictional source-pixel underlay beneath original Matrei; no original art edits.
 // The source-registered road graph is NOT implied; no new playable route.
 if(showPainted && V227ArtIngest.snapshot().cells.filter(Boolean).length===2 &&
    V264_SEAM_UNDERLAY.complete && V264_SEAM_UNDERLAY.naturalWidth===1536)
   cx.drawImage(V264_SEAM_UNDERLAY,1536,0,1536,1024);
'''
 src=src.replace(needle,replacement,1)
 src=src.replace('V263 OFFLINE EXACT-ART','V264 PHOTO-SEAM EXPERIMENT',2)
 src=src.replace('V263 two ORIGINAL images verified; V123 movement playable · ART UNAPPROVED',
  'V264 source-pixel seam study; original roads and V123 unchanged · ART UNAPPROVED')
 src=src.replace('V263 original fictional art','V264 reflected source-pixel underlay · fictional art')
 Path(output).parent.mkdir(parents=True,exist_ok=True)
 Path(output).write_text(src)
 return {'patch_bytes':len(b.getvalue()),'html_bytes':len(src),
         'patch_sha256':hashlib.sha256(b.getvalue()).hexdigest(),
         'originalRoadGraphChanged':False,'historicalGeographyVerified':False,
         'bridgeBanksVerified':False,'strictV203Passed':False,
         'userVisualApproval':False,'productionApproved':False}

if __name__=='__main__':
 ap=argparse.ArgumentParser()
 ap.add_argument('v263')
 ap.add_argument('west')
 ap.add_argument('south')
 ap.add_argument('output')
 ap.add_argument('--patch')
 args=ap.parse_args()
 print(build(args.v263,args.west,args.south,args.output,args.patch))

#!/usr/bin/env python3
"""V265: Recover existing SOUTH image shadow microstructure without relocating pixels.

Experimental fictional art ONLY; not historical/geographic verification or user approval.
The original V260 source is SHA-pinned. V123, V121, V94 and gameplay are untouched.
"""
import argparse
import base64
import hashlib
import json
import re
from pathlib import Path
import cv2
import numpy as np
from PIL import Image

ORIGINAL_SOUTH_SHA='d63f5f056a682f976bafff95f04b2b71e0bb4077f34f18e9a95b32cd72fb5ccb'
ORIGINAL_WEST_SHA='36a32828a74453ac105faf8af3729c46a42acd55d12d381d8a667d7022e1e1a7'
SIZE=(1536,1024)

def digest(data):return hashlib.sha256(data).hexdigest()

def recover(source, clip=1.25):
    """Only remap LAB luminance at the SAME source pixel, no geometric resampling.

    CLAHE increases visibility of EXISTING native shadows; no noise/stamps/roads.
    Never treat higher V203 numeric scores as proof of human visual realism.
    """
    if not (1.0<=clip<=1.65):raise ValueError('clip must be in conservative source-detail range')
    if source.ndim!=3 or source.shape!=(1024,1536,3) or source.dtype!=np.uint8:
        raise ValueError('requires 1536x1024 uint8 RGB source')
    lab=cv2.cvtColor(source,cv2.COLOR_RGB2LAB)
    L=lab[:,:,0].astype(np.float32)
    local=cv2.createCLAHE(clipLimit=clip,tileGridSize=(12,8)).apply(lab[:,:,0]).astype(np.float32)
    lifted=255*np.power(L/255,0.82)
    weight=np.clip((165-L)/120,0,1)*0.80
    result=np.clip(0.15*L+0.85*lifted+0.75*weight*(local-L),0,255).astype(np.uint8)
    adjusted=lab.copy();adjusted[:,:,0]=result
    return cv2.cvtColor(adjusted,cv2.COLOR_LAB2RGB)

def replace_js_object(src,name,mutator):
    m=re.search(r'const '+re.escape(name)+r'=(\{[^;]*\});',src)
    if not m or src.count('const '+name+'=')!=1:raise ValueError('missing or duplicated '+name)
    obj=json.loads(m.group(1));mutator(obj)
    return src[:m.start(1)]+json.dumps(obj,separators=(',',':'))+src[m.end(1):]

def build(v263_html,south_source,south_out,html_out, *, expected_south=ORIGINAL_SOUTH_SHA,clip=1.25):
    original=Path(south_source).read_bytes()
    if digest(original)!=expected_south:raise ValueError('original SOUTH SHA256 mismatch')
    with Image.open(south_source) as im:
        if im.format!='PNG' or im.size!=SIZE:raise ValueError('wrong SOUTH format/size')
        rgb=np.asarray(im.convert('RGB'))
    recovered=recover(rgb,clip)
    Path(south_out).parent.mkdir(parents=True,exist_ok=True)
    Image.fromarray(recovered,'RGB').save(south_out,format='PNG',compress_level=6)
    result_bytes=Path(south_out).read_bytes()
    html=Path(v263_html).read_text()
    if 'V264_SEAM_UNDERLAY' in html:raise ValueError('reflected V264 seam overlay must not be silently inherited')
    if 'V263ImportPair' not in html or 'get productionApproved(){return false}' not in html:
        raise ValueError('unexpected playable V263 base')
    def pin(o):
        if o.get('south')!=expected_south or o.get('west')!=ORIGINAL_WEST_SHA:
            raise ValueError('unexpected original artwork pin')
        o['south']=digest(result_bytes)
    def image(o):
        if digest(base64.b64decode(o.get('south',''),validate=True))!=expected_south:
            raise ValueError('embedded original SOUTH does not match pinned source')
        o['south']=base64.b64encode(result_bytes).decode('ascii')
    html=replace_js_object(html,'V263_PINS',pin)
    html=replace_js_object(html,'V263_IMAGES',image)
    html=html.replace('V263 OFFLINE EXACT-ART PLAYABLE CANDIDATE','V265 SOUTH SHADOW DETAIL RECOVERY - UNAPPROVED')
    html=html.replace('Original V258 WEST + V260 SOUTH + protected Matrei',
                      'Original V258 WEST + tonally recovered V260 SOUTH + protected Matrei')
    html=html.replace('V263 two ORIGINAL images verified; V123 movement playable · ART UNAPPROVED',
                      'V265 SOUTH recovered shadow detail; V123 unchanged · ART UNAPPROVED')
    html=html.replace('V263 original fictional art',
                      'V265 tone-recovered fictional SOUTH · no historic route evidence')
    if html.count('get productionApproved(){return false}')<1:raise ValueError('production approval guard missing')
    Path(html_out).parent.mkdir(parents=True,exist_ok=True)
    Path(html_out).write_text(html)
    return {'version':265,'southOriginalSHA256':expected_south,'southRecoveredSHA256':digest(result_bytes),
            'southSize':SIZE,'noPixelRelocation':True,'V123Changed':False,'V94Changed':False,
            'historicalGeographyVerified':False,'bridgeBanksVerified':False,
            'fourBrowserExactArtPassed':False,'humanVisualApproval':False,'productionApproved':False}

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('v263_html');ap.add_argument('south_original');ap.add_argument('south_output');ap.add_argument('html_output')
    a=ap.parse_args();print(json.dumps(build(a.v263_html,a.south_original,a.south_output,a.html_output),indent=2))

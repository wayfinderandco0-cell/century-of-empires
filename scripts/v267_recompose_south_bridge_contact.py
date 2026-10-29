#!/usr/bin/env python3
"""Recompose one source-native SOUTH stone-bridge contact candidate on isolated V267.

This is NOT a road-registered release. The stone bridge and adjacent gorge move
together as one rigid photographic landscape, with no bent or scaled trees.
A low-cost, color-matched image seam fills the newly exposed upper apron.
The source art, Matrei V121, V123 road graph, V94 engine/saves and sprites
are never overwritten. The northern cartway is still OFF the V123 route.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import re
import cv2
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"art-reviews/v267-original-source/south-gorge-bridge-original-unapproved.webp"
OUTPUT=ROOT/"art-reviews/v267-original-source/south-bridge-contact-unapproved.webp"
MANIFEST=ROOT/"art-reviews/v267-original-source/south-bridge-contact-unapproved.json"
HTML=ROOT/"v267-three-octagon-original-art-prototype.html"
W,H=1536,1024

def minimal_native_seam(source:np.ndarray)->np.ndarray:
    h,w=source.shape[:2]
    if (w,h)!=(W,H):
        raise ValueError("Source art must be 1536x1024")
    yy,xx=np.mgrid[:h,:w].astype(np.float32)
    # Entire source translates as one rigid photograph: no global or local
    # x-warp, y-warp, tree scaling, synthetic road stripe, or fake bridge.
    bridge=cv2.remap(source,xx+50,yy-85,cv2.INTER_LINEAR,
                     borderMode=cv2.BORDER_REFLECT_101)
    upper=cv2.remap(source,xx+50,yy,cv2.INTER_LINEAR,
                    borderMode=cv2.BORDER_REPLICATE)
    # Exposed top: use only native pixels from the same original artwork.
    # Minimize the visible transition with a 1D photo-seam through the
    # grass/river/forest material, rather than stretching or blurring trees.
    lo,hi=85,170
    a=cv2.cvtColor(upper[lo:hi],cv2.COLOR_BGR2LAB).astype(np.float32)
    b=cv2.cvtColor(bridge[lo:hi],cv2.COLOR_BGR2LAB).astype(np.float32)
    cost=np.mean((a-b)**2,axis=2)
    cost+=((np.arange(lo,hi)[:,None]-125)/50)**2*150
    n,m=cost.shape
    dp=np.zeros_like(cost)
    parent=np.zeros((n,m),np.int8)
    dp[:,0]=cost[:,0]
    for x in range(1,m):
        prev=np.stack((np.r_[dp[0,x-1]+100,dp[:-1,x-1]],
                       dp[:,x-1],
                       np.r_[dp[1:,x-1],dp[-1,x-1]+100]),axis=1)
        choice=np.argmin(prev,axis=1)
        dp[:,x]=cost[:,x]+prev[np.arange(n),choice]+(choice!=1)*90
        parent[:,x]=choice-1
    seam=np.zeros(m,np.int32)
    seam[-1]=lo+int(np.argmin(dp[:,-1]))
    for x in range(m-1,0,-1):
        seam[x-1]=seam[x]+int(parent[seam[x]-lo,x])
    seam=cv2.GaussianBlur(seam.astype(np.float32).reshape(1,-1),
                          (0,0),12).ravel()
    alpha=np.clip((yy-seam[None,:]+1.5)/3,0,1)
    composite=np.uint8(upper*(1-alpha[:,:,None])+bridge*alpha[:,:,None])
    # On the last 50px of the eastern OUTER edge, native original pixels
    # are preferable to the mirror repetition from rigid translation.
    east=cv2.remap(source,xx,yy-85,cv2.INTER_LINEAR,
                   borderMode=cv2.BORDER_REPLICATE)
    weight=np.clip((xx-1468)/45,0,1)
    weight=weight*weight*(3-2*weight)
    composite=np.uint8(composite*(1-weight[:,:,None])+east*weight[:,:,None])
    return composite

def update_preview(html:str)->str:
    if "SOUTH_BRIDGE_CONTACT_PREVIEW" in html:
        return html
    expected='const SOUTH_ORIGINAL_PREVIEW=new URLSearchParams(location.search).get("southArt")==="original";'
    replacement=('const SOUTH_ART_MODE=new URLSearchParams(location.search).get("southArt");\n'
                 'const SOUTH_BRIDGE_CONTACT_PREVIEW=SOUTH_ART_MODE==="bridge";\n'
                 'const SOUTH_ORIGINAL_PREVIEW=SOUTH_ART_MODE==="original"||SOUTH_BRIDGE_CONTACT_PREVIEW;')
    if html.count(expected)!=1: raise RuntimeError("Original SOUTH mode changed; stop")
    html=html.replace(expected,replacement,1)
    old=('const southArtSource=SOUTH_ORIGINAL_PREVIEW\n'
         '  ? "art-reviews/v267-original-source/south-gorge-bridge-original-unapproved.webp"\n'
         '  : ART_SOUTH;')
    new=('const southArtSource=SOUTH_BRIDGE_CONTACT_PREVIEW\n'
         '  ? "art-reviews/v267-original-source/south-bridge-contact-unapproved.webp"\n'
         '  : SOUTH_ORIGINAL_PREVIEW\n'
         '  ? "art-reviews/v267-original-source/south-gorge-bridge-original-unapproved.webp"\n'
         '  : ART_SOUTH;')
    if html.count(old)!=1: raise RuntimeError("Original SOUTH source selection changed; stop")
    html=html.replace(old,new,1)
    old='<button id="southsource">New SOUTH art</button>'
    if html.count(old)!=1: raise RuntimeError("Missing SOUTH art button")
    html=html.replace(old,old+'<button id="southbridge">Bridge contact</button>',1)
    marker='document.getElementById("southsource").onclick=()=>{'
    if html.count(marker)!=1: raise RuntimeError("Missing SOUTH art toggle")
    new_handler=('document.getElementById("southbridge").onclick=()=>{\n'
                 ' const url=new URL(location.href);\n'
                 ' if(SOUTH_BRIDGE_CONTACT_PREVIEW)url.searchParams.delete("southArt");\n'
                 ' else url.searchParams.set("southArt","bridge");\n'
                 ' location.assign(url.href);\n'
                 '};\n'+marker)
    html=html.replace(marker,new_handler,1)
    old='if(SOUTH_ORIGINAL_PREVIEW){\n  document.querySelector("header small").textContent='
    if html.count(old)!=1: raise RuntimeError("Missing alternate source status")
    html=html.replace(old,
       'if(SOUTH_ORIGINAL_PREVIEW){\n  document.querySelector("header small").textContent=',
       1)
    # The alternate remains an opt-in art study with V123 yellow overlay
    # and no fake road join. Never modify the original route arrays.
    assert 'const southRoad=' in html and 'const westRoad=' in html
    assert 'ART_MATREI_CANONICAL=' in html
    return html

def main():
    original=cv2.imread(str(SOURCE),cv2.IMREAD_COLOR)
    if original is None: raise FileNotFoundError(SOURCE)
    image=minimal_native_seam(original)
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    Image.fromarray(cv2.cvtColor(image,cv2.COLOR_BGR2RGB)).save(
        OUTPUT,"WEBP",quality=91,method=6)
    source_digest=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    art_digest=hashlib.sha256(OUTPUT.read_bytes()).hexdigest()
    text=HTML.read_text(encoding="utf-8")
    changed=update_preview(text)
    if changed!=text:HTML.write_text(changed,encoding="utf-8")
    MANIFEST.write_text(json.dumps({
      "status":"UNAPPROVED; NOT road-aligned; production RED",
      "provenance":"fictional original Alpine game artwork",
      "source":str(SOURCE.relative_to(ROOT)),
      "source_sha256":source_digest,
      "candidate":str(OUTPUT.relative_to(ROOT)),
      "candidate_sha256":art_digest,
      "dimensions":[W,H],
      "art_registration":"rigid native photo move -50px x, +85px y; native photo seam",
      "bridge_expected_graph":[1140,585],
      "northern_graph_entry":[466,0],
      "northern_photo_entry_still_wrong":True,
      "known_visual_defects":[
        "northern photographed cartway still west of V123 x466",
        "outer right forest edge needs manual source-art reconstruction",
        "Matrei-SOUTH material seam remains unapproved"
      ],
      "protected":"V121/V123/V94, sprites, saves, production main unchanged"
    },indent=2)+"\n")
    print("Source-native SOUTH bridge-contact candidate:",len(OUTPUT.read_bytes()),
          "bytes; SHA256",art_digest,"; playable preview opt-in only")

if __name__=="__main__":main()

#!/usr/bin/env python3
"""Recompose one source-native SOUTH stone-bridge contact candidate on isolated V267.

This is an UNAPPROVED road-contact artwork study. The stone bridge and gorge move
together as one rigid photographic landscape, with no bent or scaled trees.
A low-cost, color-matched image seam fills the newly exposed upper apron.
The source art, Matrei V121, V123 road graph, V94 engine/saves and sprites
are never overwritten. The northern cartway is now locally registered to x466.
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
    """Rebuild SOUTH as a continuous *photographed* dirt road to the V123 edge.

    First move the original gorge and stone bridge rigidly, then transplant
    the actual source-cartway ruts in a narrow meadow corridor. The abandoned
    upper road is replaced by nearby native meadow pixels. All trees and
    river outside that corridor retain their original shape. This is a
    fictional, UNAPPROVED art prototype, not a historical topographic claim.
    """
    h,w=source.shape[:2]
    if (w,h)!=(W,H):
        raise ValueError("Source art must be 1536x1024")
    yy,xx=np.mgrid[:h,:w].astype(np.float32)
    bridge=cv2.remap(source,xx+50,yy-85,cv2.INTER_LINEAR,
                     borderMode=cv2.BORDER_REFLECT_101)
    upper=cv2.remap(source,xx+50,yy,cv2.INTER_LINEAR,
                    borderMode=cv2.BORDER_REPLICATE)
    # Source-native seam between the rigid bridge translation and upper
    # photographed landscape. Do not stretch or mirror a single tree.
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

    # Keep native forest at the outer right edge; the rigid translation
    # otherwise reflects the last 50 source columns. Avoid a vertically
    # replicated flat strip at the upper right.
    east=cv2.remap(source,xx,yy-85,cv2.INTER_LINEAR,
                   borderMode=cv2.BORDER_REPLICATE)
    weight=np.clip((xx-1468)/45,0,1)
    weight=weight*weight*(3-2*weight)
    composite=np.uint8(composite*(1-weight[:,:,None])+east*weight[:,:,None])
    native_edge=cv2.remap(source,xx,yy,cv2.INTER_LINEAR,
                          borderMode=cv2.BORDER_REPLICATE)
    edge_weight=np.clip((xx-1420)/100,0,1)
    edge_weight=edge_weight*edge_weight*(3-2*edge_weight)
    edge_weight*=np.clip((235-yy)/85,0,1)
    composite=np.uint8(composite*(1-edge_weight[:,:,None])+
                       native_edge*edge_weight[:,:,None])

    # Photographed cartway centreline, read from the actual bridge-contact
    # source, and the smooth local eastward relocation needed to reach the
    # immutable SOUTH V123 entry (466,0). This is a ROAD-ONLY copy, not a
    # global x-warp of trees, cliffs, or river.
    knots=np.array([0,80,160,200,250,300,340,380,430,480,530,560],
                   np.float32)
    road_center=np.array([329,330,330,339,364,420,477,553,670,805,974,1060],
                         np.float32)
    road_shift=np.array([137,136,133,120,105,82,68,55,38,20,5,0],
                        np.float32)
    old=np.interp(np.arange(h),knots,road_center).astype(np.float32)
    delta=np.interp(np.arange(h),knots,road_shift).astype(np.float32)
    assert round(old[0]+delta[0])==466

    # Restore meadow at the old dirt track from an adjacent native-meadow
    # photograph. A feathered real-pixel patch retains grass, stones and
    # shrubs without inpaint blur, repeated trees, or a painted green stripe.
    old_mask=np.zeros((h,w),np.uint8)
    for j in range(561):
        if delta[j]<2: continue
        width=36 if j<200 else (49 if j<420 else 38)
        cv2.line(old_mask,(int(old[j]-width),j),
                 (int(old[j]+width),j),255,1)
    old_mask=cv2.GaussianBlur(old_mask,(0,0),1.2)
    old_mask=np.uint8(old_mask>100)*255
    meadow=cv2.remap(composite,xx-100,yy,cv2.INTER_LINEAR,
                     borderMode=cv2.BORDER_REFLECT_101)
    fade=cv2.GaussianBlur(old_mask.astype(np.float32)/255,
                          (0,0),12)[:,:,None]
    base=np.uint8(composite*(1-fade)+meadow*fade)

    # The actual rutted cartway is sampled from the untouched photograph.
    # Feather only its natural grass shoulders; at y>=560 the source and
    # destination are identical, preserving the original stone bridge.
    road=cv2.remap(composite,xx-delta[:,None],yy,cv2.INTER_LINEAR,
                   borderMode=cv2.BORDER_REFLECT_101)
    road_width=np.where(yy<200,28,np.where(yy<380,32,30)).astype(np.float32)
    distance=np.abs(xx-(old+delta)[:,None])
    a=np.clip((road_width+12-distance)/13,0,1)
    a=a*a*(3-2*a)
    a*=np.clip((560-yy)/45,0,1)
    return np.uint8(base*(1-a[:,:,None])+road*a[:,:,None])

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
      "status":"UNAPPROVED; northern road and stone bridge photo-registered; production RED",
      "provenance":"fictional original Alpine game artwork",
      "source":str(SOURCE.relative_to(ROOT)),
      "source_sha256":source_digest,
      "candidate":str(OUTPUT.relative_to(ROOT)),
      "candidate_sha256":art_digest,
      "dimensions":[W,H],
      "art_registration":"rigid native bridge move -50px x,+85px y; original rutted cartway transplanted locally to V123 north entry x466; abandoned track restored with native meadow",
      "bridge_expected_graph":[1140,585],
      "northern_graph_entry":[466,0],
      "northern_photo_entry_still_wrong":False,
      "known_visual_defects":[
        "northern cartway now reaches x466; verify on real iPhone at high zoom",
        "outer right forest edge may still show material discontinuity",
        "Matrei-SOUTH material seam and photographic road curvature remain unapproved"
      ],
      "protected":"V121/V123/V94, sprites, saves, production main unchanged"
    },indent=2)+"\n")
    print("Source-native SOUTH bridge-contact candidate:",len(OUTPUT.read_bytes()),
          "bytes; SHA256",art_digest,"; playable preview opt-in only")

if __name__=="__main__":main()

#!/usr/bin/env python3
"""Eight *original photographic layered-composition* scenic atlas studies.

This is the V267 method of whole-scene, multi-source, non-repeated natural
photographic material and regional light matching. NOT aerial-photo tiles,
synthetic road stripes, historically surveyed terrain, or approved gameplay.
Never uses pixels from protected WEST/MATREI/SOUTH. Source rights checked.
"""
from __future__ import annotations
import hashlib, io, json, math, re, time, urllib.parse, urllib.request
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance, ImageDraw

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"terrain-grid/v267-neighbor-original-art"
W,H=1536,1024
REF="456107f28c8db1f87522bbc7511809b2a215f6fb"
# Eight DISTINCT CC0 primary landscape photographs; regional resemblance only.
# None establishes an eighteenth- or nineteenth-century road or settlement.
SPEC=[
 ("east-matrei","Forested mountain valley (Unsplash).jpg",(3072,0),"wooded-alpine-valley",(.52,.57)),
 ("east-south","Alpine valley (Unsplash).jpg",(3072,1024),"limestone-pasture",(.50,.63)),
 ("west-south","Alpine landscape (Unsplash).jpg",(0,1024),"alpine-foothills",(.43,.55)),
 ("south-west","Gray clouds over green valley (Unsplash).jpg",(0,2048),"misty-high-valley",(.48,.64)),
 ("south-central","Alpine ridge (Unsplash).jpg",(1536,2048),"alpine-ridge",(.52,.53)),
 ("south-east","Alpine glacier (Unsplash).jpg",(3072,2048),"high-alpine-ice",(.53,.53)),
 ("far-east-north","Flachau mountain valley (Unsplash).jpg",(4608,0),"mountain-winter-valley",(.51,.61)),
 ("far-east-south","Shallow mountain valley (Unsplash).jpg",(4608,1024),"lower-alpine-meadow",(.49,.61))
]
UA="CenturyOfEmpiresOriginalArt/1.0 (CC0 provenance audit; github.com/wayfinderandco0-cell/century-of-empires/issues/9)"
def get(url):
    last=None
    for pause in (0,15,35):
        if pause:time.sleep(pause)
        try:
            req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"application/json,image/*"})
            with urllib.request.urlopen(req,timeout=65) as response:return response.read()
        except Exception as e:last=e
    raise RuntimeError("Source unavailable; no invented replacement: "+str(last))
def commons(title):
    params=urllib.parse.urlencode({"action":"query","format":"json","prop":"imageinfo",
       "titles":"File:"+title,"iiprop":"url|size|extmetadata","iiurlwidth":"2400"})
    data=json.loads(get("https://commons.wikimedia.org/w/api.php?"+params))
    pages=list(data["query"]["pages"].values())
    if len(pages)!=1 or "imageinfo" not in pages[0]:raise RuntimeError("No source "+title)
    info=pages[0]["imageinfo"][0]
    md=info.get("extmetadata",{})
    license_text=re.sub("<[^>]*>","",md.get("LicenseShortName",{}).get("value","")).upper()
    if "CC0" not in license_text and "CC-ZERO" not in license_text:
        raise RuntimeError("Source not verified CC0: "+title+" / "+license_text)
    # Original file CDN often has a different throttle from Commons thumbnails.
    # Never replace a failed source with a different image or unlicensed bytes.
    try:
        raw=get(info["url"])
        source_url=info["url"]
    except RuntimeError:
        try:
            raw=get(info.get("thumburl") or info["url"])
            source_url=info.get("thumburl") or info["url"]
        except RuntimeError:
            # Wikimedia CDN 429 on shared CI IPs: a read-through cache may
            # fetch the SAME Commons CC0 original, not a replacement source.
            # Do not accept proxy output without a decoded image + source record.
            proxy="https://wsrv.nl/?"+urllib.parse.urlencode({
                "url":info["url"],"w":"2400","output":"jpg"})
            raw=get(proxy)
            source_url=proxy
    im=Image.open(io.BytesIO(raw)).convert("RGB")
    if im.width<1600 or im.height<1050:raise RuntimeError("Insufficient source resolution "+title)
    return im,{"title":title,"page":"https://commons.wikimedia.org/wiki/File:"+
      urllib.parse.quote(title.replace(" ","_")),"sourceSha256":hashlib.sha256(raw).hexdigest(),
      "license":"CC0 1.0","licenseUrl":"https://creativecommons.org/publicdomain/zero/1.0/",
      "download":source_url,"sourceDimensions":list(im.size)}
def window(im,focus):
    """Single camera-perspective crop; never nonuniformly stretch trees."""
    w,h=im.size
    if w<W or h<H:
        k=max(W/w,H/h)
        im=im.resize((math.ceil(w*k),math.ceil(h*k)),Image.Resampling.LANCZOS)
        w,h=im.size
    x=round((w-W)*focus[0]);y=round((h-H)*focus[1])
    x=max(0,min(w-W,x));y=max(0,min(h-H,y))
    return im.crop((x,y,x+W,y+H)),[x,y,x+W,y+H]
def compose(primary,secondary,index):
    """Whole-scene foreground exchange with a *broad natural terrain boundary*.

    Different camera scenes can have mismatched perspective: this is precisely
    why assets remain unapproved until visual review. No fake cartways, towns,
    rivers, bridges, or 3D tree meshes are drawn.
    """
    p=np.asarray(primary,dtype=np.float32)
    q=np.asarray(secondary,dtype=np.float32)
    # Gently match the donor's overall illumination before source-land blending.
    pm=np.median(p[580:930].reshape(-1,3),axis=0)
    qm=np.median(q[580:930].reshape(-1,3),axis=0)
    q=np.clip(q+(pm-qm)*.55,0,255)
    xs=np.arange(W,dtype=np.float32)[None,:]
    ys=np.arange(H,dtype=np.float32)[:,None]
    boundary=740+33*np.sin(xs/149+index*1.3)+16*np.sin(xs/57+index*.8)
    # Feather over 170 pixels so individual foreground features are not warped.
    alpha=np.clip((ys-boundary)/175,0,1)
    alpha=alpha*alpha*(3-2*alpha)*.66
    merged=np.uint8(np.clip(p*(1-alpha[:,:,None])+q*alpha[:,:,None],0,255))
    scene=Image.fromarray(merged,"RGB")
    scene=ImageEnhance.Color(scene).enhance(.92)
    scene=ImageEnhance.Contrast(scene).enhance(1.035)
    return scene
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    sources=[commons(spec[1]) for spec in SPEC]
    if len({m["sourceSha256"] for _,m in sources})!=8:
        raise RuntimeError("Duplicate source landscape; refuse cloned artwork")
    cells=[]
    for i,(ident,title,origin,biome,focus) in enumerate(SPEC):
        original,src=sources[i]
        secondary,donor=sources[(i+3)%len(sources)]
        primary,crop=window(original,focus)
        donor_scene,donor_crop=window(secondary,(.37+.07*(i%3),.60))
        scene=compose(primary,donor_scene,i)
        target=OUT/(ident+".webp")
        scene.save(target,"WEBP",quality=91,method=6)
        raw=target.read_bytes()
        cells.append({
            "id":ident,"origin":list(origin),"biome":biome,
            "art":"terrain-grid/v267-neighbor-original-art/"+target.name,
            "assetSha256":hashlib.sha256(raw).hexdigest(),
            "visualGrammar":"v267-original-layered-landscape",
            "originalArtComposed":True,"sourcePrimary":dict(src,crop=crop),
            "sourceForeground":dict(donor,crop=donor_crop),
            "sourceMethod":"Two independently licensed, distinct oblique natural landscape sources; broad irregular nonrepeating foreground blend, source lighting grade, no drawn roads or synthetic trees",
            "scenicSettlements":[],"strategicNodes":[],"provinceIds":[],
            "roadPorts":[],"roadSeamsVerified":False,"riverCrossingsVerified":False,
            "geoVerified":False,"historicalVerified":False,"historicallyVerified":False,
            "visuallyReviewed":False,"mobileWebkitRendered":False,
            "nativePlayable":False,"userApproved":False,
            "notes":"Regional art candidate only; not surveyed 1780-1880 geography; source photograph may contain modern features; road-free"
        })
    if len({c["assetSha256"] for c in cells})!=8:raise RuntimeError("Duplicate composed output")
    manifest={"schema":"coe-v267-original-art-batch/v1","referenceCommit":REF,
       "status":"original-photo-layered-unapproved-neighbor-study",
       "scenario":"fictional Alpine scenic composition, not historical topography",
       "cells":cells,"links":[],"decorativeInlays":[],
       "generatedCandidates":8,"originalArtComposed":8,
       "visuallyReviewed":0,"roadConnected":0,"mobileWebkitRendered":0,
       "historicallyVerified":0,"nativePlayable":0,"userApproved":0,
       "netFinishedToday":0}
    (OUT/"batch.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+"\n")
    board=Image.new("RGB",(1536,4*550),(20,30,26));draw=ImageDraw.Draw(board)
    for i,c in enumerate(cells):
        x=(i%2)*768;y=(i//2)*550
        im=Image.open(ROOT/c["art"]).resize((768,512),Image.Resampling.LANCZOS)
        board.paste(im,(x,y+24))
        draw.text((x+8,y+5),c["id"]+" · "+c["biome"],fill="#f5e2bd")
        draw.text((x+8,y+538),"ORIGINAL LAYERED CANDIDATE — NOT APPROVED",fill="#f5e2bd")
    board.save(OUT/"eight-scene-contact.webp","WEBP",quality=87,method=6)
    print(json.dumps({"originalComposed":len(cells),"uniquePrimarySources":len(sources),
      "roads":0,"historicallyVerified":0,"nativePlayable":0,"finished":0}))
if __name__=="__main__":main()

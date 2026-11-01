#!/usr/bin/env python3
"""V267 EAST-01 native landscape cartway candidate. Does NOT alter protected art.

Uses the already-authored east ridge / riparian V4 landscape. Adds a narrow,
weathered cartway sampled from the registered Matrei road palette, plus a
SEPARATE reversible display overlay for Matrei's last 185px. This is not
a surveyed historical road, a verified seam, or an enabled V123 army route.
"""
from __future__ import annotations
import hashlib, json
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter, ImageDraw
from v267_east01_riparian_v4 import registered_matrei

ROOT=Path(__file__).resolve().parents[1]
DIR=ROOT/"terrain-grid/v267-original-art-batch-01"
MATREI=ROOT/"terrain-grid/art/matrei-v121-original.webp"
BASE=DIR/"matrei-east-riparian-v4.webp"
W,H=1536,1024

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def curve_distance(points):
    yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
    best=np.full((H,W),1e7,dtype=np.float32)
    for (ax,ay),(bx,by) in zip(points[:-1],points[1:]):
        dx,dy=bx-ax,by-ay
        t=np.clip(((xx-ax)*dx+(yy-ay)*dy)/(dx*dx+dy*dy),0,1)
        dist=np.hypot(xx-(ax+t*dx),yy-(ay+t*dy))
        np.minimum(best,dist,out=best)
    return best

def paint(scene,points,soil,seed,allowed_x=None,overlay=False):
    rng=np.random.default_rng(seed)
    dist=curve_distance(points)
    yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
    # Native narrow double-rut dirt track. No straight graphic highway stripe.
    noise=Image.fromarray(rng.integers(0,256,(H,W),dtype=np.uint8),"L")
    fine=(np.asarray(noise.filter(ImageFilter.GaussianBlur(1.7)),dtype=np.float32)-127)/40
    broad=(np.asarray(noise.filter(ImageFilter.GaussianBlur(13)),dtype=np.float32)-127)/18
    irregular=1.7*np.sin(xx/24+yy/39)+1.2*np.sin(xx/8+yy/27)
    width=17+1.9*np.sin(xx/81)+1.4*np.sin(xx/33)+irregular
    core=np.clip((width-dist)/3.5+.5,0,1)
    core=core*core*(3-2*core)
    shoulder=np.clip((width+7-dist)/6,0,1)*(1-core)
    if allowed_x is not None:
        active=(xx>=allowed_x).astype(np.float32)
        core*=active;shoulder*=active
    src=np.asarray(scene.convert("RGB"),dtype=np.float32)
    earth=np.empty_like(src)
    # Ground remains shaded by underlying original relief; road surface is
    # earth-tinted, NOT a flat opaque painted band.
    for c in range(3):
        earth[:,:,c]=src[:,:,c]*.30+soil[c]*.70+fine*3.4+broad*2.8
    ruts=np.exp(-.5*((dist-width*.52)/2.8)**2)
    earth-=ruts[:,:,None]*np.array([15,13,9],dtype=np.float32)
    grass_center=np.exp(-.5*(dist/3.2)**2)
    earth+=grass_center[:,:,None]*np.array([-8,4,-9],dtype=np.float32)
    src=src*(1-core[:,:,None]*.85)+earth*core[:,:,None]*.85
    src*=1-shoulder[:,:,None]*.07
    out=Image.fromarray(np.uint8(np.clip(src,0,255)),"RGB")
    if not overlay:return out,None
    alpha=np.uint8(np.clip((core*.94+shoulder*.14)*255,0,255))
    rgba=out.convert("RGBA")
    rgba.putalpha(Image.fromarray(alpha,"L"))
    return out,rgba

def generate():
    for p in (MATREI,BASE):
        if not p.is_file():raise SystemExit("Missing original art: "+str(p))
    protected_before=sha(MATREI)
    matrei=Image.open(MATREI).convert("RGB")
    east=Image.open(BASE).convert("RGB")
    if matrei.size!=(W,H) or east.size!=(W,H):
        raise SystemExit("Native artwork must be 1536x1024")
    registered=Image.fromarray(registered_matrei(matrei),"RGB")
    # Palette samples from the existing southeastern road; no new invented
    # source landscape, castle, village, or river crossing.
    arr=np.asarray(registered)
    samples=np.array([arr[y,x] for x,y in
                      [(1210,617),(1266,650),(1304,673),(1340,695),(1351,749)]],
                     dtype=np.float32)
    native=np.median(samples,axis=0)
    soil=np.clip(.25*native+.75*np.array([139,114,77]),[96,78,48],[170,146,111])
    # Keep the approved Matrei source byte-identical. Extension is a reversible
    # overlay only for the new candidate comparison, never the default game.
    matrei_points=[(1351,749),(1408,749),(1462,750),(1535,749)]
    _,overlay=paint(registered,matrei_points,soil,2671500,allowed_x=1351,overlay=True)
    east_points=[(0,749),(70,749),(142,744),(220,730),
                 (312,712),(414,693),(520,680),(610,665)]
    candidate,_=paint(east,east_points,soil,2671501)
    target=DIR/"matrei-east-riparian-v5-road-study.webp"
    overlay_path=DIR/"matrei-east-v5-road-extension-overlay.png"
    contact_path=DIR/"matrei-east-v5-road-contact.webp"
    candidate.save(target,"WEBP",quality=91,method=6)
    # Transparent overlay retains ONLY road pixels, no source landscape clone.
    overlay.save(overlay_path,"PNG",optimize=True)
    left=registered.copy();left.alpha_composite(overlay) if left.mode=="RGBA" else None
    left=Image.alpha_composite(left.convert("RGBA"),overlay).convert("RGB")
    contact=Image.new("RGB",(3072,1024),(18,31,24))
    contact.paste(left,(0,0));contact.paste(candidate,(1536,0))
    draw=ImageDraw.Draw(contact)
    draw.line([(1536,256),(1536,768)],fill=(223,180,102),width=2)
    contact.save(contact_path,"WEBP",quality=87,method=6)
    if sha(MATREI)!=protected_before:raise RuntimeError("Protected V121 art changed")
    evidence={
      "schema":"coe-v267-east-road-study/v1",
      "baseLandscape":"matrei-east-riparian-v4.webp",
      "sourceMatrei":"terrain-grid/art/matrei-v121-original.webp",
      "candidate":target.name,"matreiDisplayOverlay":overlay_path.name,
      "contact":contact_path.name,"candidateSha256":sha(target),
      "matreiSourceSha256":protected_before,
      "eastRoadPoints":east_points,"matreiOverlayPoints":matrei_points,
      "roadPortContract":{"matrei":[1536,749],"east":[0,749],
                          "endpointGapPx":0,"geometryPairedOnly":True},
      "fictionalExperimentalRoute":True,"sourceOriginalsUnchanged":True,
      "physicalRoadSeamVerified":False,"riverSeamVerified":False,
      "roadAppearanceVisuallyApproved":False,"mobileWebkitRendered":False,
      "historicallyVerified":False,"nativePlayable":False,
      "userApproved":False,"finished":False,
      "notes":"Original east landscape with native-scale soil-colored track. Overlay is opt-in; source Matrei and V123 graph unchanged. Geometry alone does not verify visible cartway continuity."
    }
    (DIR/"matrei-east-v5-road-evidence.json").write_text(json.dumps(evidence,indent=2)+"\n")
    print(json.dumps({"candidate":str(target),"bytes":target.stat().st_size,
      "roadOverlay":str(overlay_path),"contact":str(contact_path),
      "protectedMatreiUnchanged":True,"newPlayable":0}))
if __name__=="__main__":generate()

#!/usr/bin/env python3
"""EAST-01 V6 source-textured cartway: preserve all approved Matrei pixels.

V5 visual QA showed an unacceptable uniform ribbon. V6 maps the ACTUAL
painted Matrei southeast dirt-track texture into a narrow, curved EAST-01
corridor and fades it into the existing original forest. No flat synthetic
road color, heightmesh, cloned landscape, invented historical feature,
bridge, or enabled army link. Candidate remains unapproved.
"""
from __future__ import annotations
import hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
from v267_east01_riparian_v4 import registered_matrei
ROOT=Path(__file__).resolve().parents[1]
DIR=ROOT/"terrain-grid/v267-original-art-batch-01"
MATREI=ROOT/"terrain-grid/art/matrei-v121-original.webp"
EAST=DIR/"matrei-east-riparian-v4.webp"
W,H=1536,1024
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def cumulative(points):
    p=np.asarray(points,dtype=np.float32)
    lens=np.hypot(np.diff(p[:,0]),np.diff(p[:,1]))
    return np.concatenate(([0],np.cumsum(lens)))
def texture_map(src,dst,source_points,target_points):
    sp=np.asarray(source_points,dtype=np.float32)
    tp=np.asarray(target_points,dtype=np.float32)
    s_cum=cumulative(sp);t_cum=cumulative(tp)
    yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
    dist=np.full((H,W),1e8,dtype=np.float32)
    signed=np.zeros((H,W),dtype=np.float32)
    along=np.zeros((H,W),dtype=np.float32)
    for i in range(len(tp)-1):
        ax,ay=tp[i];bx,by=tp[i+1]
        dx,dy=bx-ax,by-ay;length=float(np.hypot(dx,dy))
        t=np.clip(((xx-ax)*dx+(yy-ay)*dy)/(length*length),0,1)
        nx=xx-(ax+t*dx);ny=yy-(ay+t*dy)
        d=np.hypot(nx,ny)
        better=d<dist
        dist=np.where(better,d,dist)
        signed=np.where(better,(-dy*nx+dx*ny)/length,signed)
        along=np.where(better,t_cum[i]+t*length,along)
    # Sample an actual original Matrei road section, not random background.
    src_distance=s_cum[0]+np.clip(along/t_cum[-1],0,1)*(s_cum[-1]-s_cum[0])
    sx=np.interp(src_distance,s_cum,sp[:,0])
    sy=np.interp(src_distance,s_cum,sp[:,1])
    before=np.maximum(0,src_distance-2)
    after=np.minimum(s_cum[-1],src_distance+2)
    tx=np.interp(after,s_cum,sp[:,0])-np.interp(before,s_cum,sp[:,0])
    ty=np.interp(after,s_cum,sp[:,1])-np.interp(before,s_cum,sp[:,1])
    norm=np.maximum(1,np.hypot(tx,ty))
    sx=np.clip(sx-ty/norm*signed,0,W-1.001)
    sy=np.clip(sy+tx/norm*signed,0,H-1.001)
    arr=np.asarray(src.convert("RGB"),dtype=np.float32)
    x0=np.floor(sx).astype(np.int32);y0=np.floor(sy).astype(np.int32)
    fx=(sx-x0)[...,None];fy=(sy-y0)[...,None]
    sampled=(1-fy)*((1-fx)*arr[y0,x0]+fx*arr[y0,x0+1])+fy*((1-fx)*arr[y0+1,x0]+fx*arr[y0+1,x0+1])
    original=np.asarray(dst.convert("RGB"),dtype=np.float32)
    # Narrow, feathered native road. Fade where it enters existing forest;
    # do not overwrite whole trees with an opaque, ruler-straight stripe.
    width=15.0+1.4*np.sin(along/47)+.9*np.sin(along/15)
    edge=np.clip((width-dist)/4+.5,0,1)
    edge=edge*edge*(3-2*edge)
    progress=np.clip(along/t_cum[-1],0,1)
    forest_fade=np.clip((1-progress)/.24,0,1)
    forest_fade=forest_fade*forest_fade*(3-2*forest_fade)
    alpha=edge*.88*forest_fade
    # Preserve original relief lighting, with the real Matrei road texture
    # supplying ruts, stones, dirt and small-scale irregularity.
    sample_luma=np.mean(sampled,axis=2)
    original_luma=np.mean(original,axis=2)
    lighting=np.clip((original_luma-sample_luma)*.17,-13,13)
    sampled=np.clip(sampled+lighting[:,:,None],0,255)
    out=np.uint8(np.clip(original*(1-alpha[:,:,None])+sampled*alpha[:,:,None],0,255))
    return Image.fromarray(out,"RGB"),int(np.count_nonzero(alpha>.3))
def main():
    for p in (MATREI,EAST):
        if not p.is_file():raise SystemExit("Missing source art: "+str(p))
    before=sha(MATREI)
    with Image.open(MATREI) as mat,Image.open(EAST) as east:
        if mat.size!=(W,H) or east.size!=(W,H):raise RuntimeError("Wrong source dimensions")
        m=Image.fromarray(registered_matrei(mat.convert("RGB")),"RGB")
        src=[(1150,568),(1185,594),(1226,621),(1266,650),
             (1304,673),(1340,695),(1352,727),(1351,749)]
        target=[(0,749),(72,748),(148,741),(227,725),
                (306,706),(386,672),(458,634),(526,598),(601,567)]
        art,pixels=texture_map(m,east,src,target)
    path=DIR/"matrei-east-riparian-v6-source-road.webp"
    contact=DIR/"matrei-east-v6-source-road-contact.webp"
    art.save(path,"WEBP",quality=92,method=6)
    board=Image.new("RGB",(3072,1024),(18,31,24))
    board.paste(m,(0,0));board.paste(art,(1536,0))
    ImageDraw.Draw(board).line([(1536,256),(1536,768)],fill=(225,183,107),width=2)
    board.save(contact,"WEBP",quality=87,method=6)
    assert sha(MATREI)==before
    data={"schema":"coe-v267-east-source-cartway/v1",
      "sourceOriginal":"matrei-east-riparian-v4.webp",
      "sourceRoadMaterial":"actual registered V121 Matrei southeast route",
      "candidate":path.name,"contact":contact.name,
      "candidateSha256":sha(path),"matreiSourceSha256":before,
      "eastRoadPoints":target,"sourceRoadPoints":src,
      "paintedRoadPixels":pixels,"matreiDisplayOverlay":None,
      "protectedOriginalsUnchanged":True,
      "roadPortContract":{"matrei":[1536,749],"east":[0,749],
        "endpointGapPx":0,"geometryPairedOnly":True},
      "fictionalExperimentalRoute":True,"physicalRoadSeamVerified":False,
      "riverSeamVerified":False,"visualQualityApproved":False,
      "mobileWebkitRendered":False,"historicallyVerified":False,
      "nativePlayable":False,"userApproved":False,"finished":False,
      "notes":"Source-textured original east artwork; no alteration to approved Matrei, no fabricated historical roads. Road/river seam and visual ground contact remain unverified."}
    (DIR/"matrei-east-v6-road-evidence.json").write_text(json.dumps(data,indent=2)+"\n")
    print(json.dumps({"newCandidate":path.name,"bytes":path.stat().st_size,
      "paintedRoadPixels":pixels,"protectedMatreiUnchanged":True,"finished":0}))
if __name__=="__main__":main()

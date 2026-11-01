#!/usr/bin/env python3
"""EAST-01 V7: source-textured cartway embedded in a physically cleared corridor.

This is a reversible fictional terrain candidate. V121/V123/V94 and approved
WEST/MATREI/SOUTH files are never written. Unlike V6, tree crowns are replaced
with original meadow ground *before* the Matrei road material is applied.
The source landscape is the already-authored EAST V4 ridge, not screenshot crops.
"""
from __future__ import annotations
import hashlib, json
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from v267_east01_riparian_v4 import registered_matrei

ROOT=Path(__file__).resolve().parents[1]
DIR=ROOT/"terrain-grid/v267-original-art-batch-01"
MAT=ROOT/"terrain-grid/art/matrei-v121-original.webp"
EAST=DIR/"matrei-east-riparian-v4.webp"
W,H=1536,1024
# One continuous world-space contract, with exact paired x=1536, y=749.
ROUTE=[(1351,749),(1425,750),(1536,749),(1615,747),(1705,739),
       (1785,723),(1865,700),(1948,667),(2024,628),(2105,592),
       (2180,567),(2250,559)]
SOURCE=[(1150,568),(1185,594),(1226,621),(1266,650),
        (1304,673),(1340,695),(1352,727),(1351,749)]

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def arclength(points):
    p=np.asarray(points,dtype=np.float32)
    return np.r_[0,np.cumsum(np.hypot(np.diff(p[:,0]),np.diff(p[:,1])))]

def bilinear(arr,x,y):
    hh,ww=arr.shape[:2]
    x=np.clip(x,0,ww-1.001);y=np.clip(y,0,hh-1.001)
    x0=np.floor(x).astype(np.int32);y0=np.floor(y).astype(np.int32)
    fx=(x-x0)[...,None];fy=(y-y0)[...,None]
    return ((1-fy)*((1-fx)*arr[y0,x0]+fx*arr[y0,x0+1])
            +fy*((1-fx)*arr[y0+1,x0]+fx*arr[y0+1,x0+1]))

def geometry(offset):
    yy,xx=np.mgrid[:H,:W].astype(np.float32)
    worldx=xx+offset
    dist=np.full((H,W),1e6,dtype=np.float32)
    signed=np.zeros_like(dist);along=np.zeros_like(dist)
    cumulative=arclength(ROUTE)
    for i,((ax,ay),(bx,by)) in enumerate(zip(ROUTE[:-1],ROUTE[1:])):
        dx,dy=bx-ax,by-ay;length=float(np.hypot(dx,dy))
        t=np.clip(((worldx-ax)*dx+(yy-ay)*dy)/(length*length),0,1)
        nx=worldx-(ax+t*dx);ny=yy-(ay+t*dy)
        d=np.hypot(nx,ny);pick=d<dist
        dist=np.where(pick,d,dist)
        signed=np.where(pick,(-dy*nx+dx*ny)/length,signed)
        along=np.where(pick,cumulative[i]+t*length,along)
    return xx,yy,dist,signed,along

def material(registered,along,signed):
    pts=np.asarray(SOURCE,dtype=np.float32)
    lengths=arclength(SOURCE)
    route_length=float(arclength(ROUTE)[-1])
    s=np.clip(along/route_length,0,1)*lengths[-1]
    sx=np.interp(s,lengths,pts[:,0]);sy=np.interp(s,lengths,pts[:,1])
    before=np.maximum(0,s-3);after=np.minimum(lengths[-1],s+3)
    tx=np.interp(after,lengths,pts[:,0])-np.interp(before,lengths,pts[:,0])
    ty=np.interp(after,lengths,pts[:,1])-np.interp(before,lengths,pts[:,1])
    norm=np.maximum(1,np.hypot(tx,ty))
    sx-=ty/norm*signed;sy+=tx/norm*signed
    return bilinear(registered,sx,sy)

def compose(base,registered,offset):
    xx,yy,dist,signed,along=geometry(offset)
    original=np.asarray(base.convert("RGB"),dtype=np.float32)
    source=np.asarray(registered.convert("RGB"),dtype=np.float32)
    # Original meadow/soil microtexture, not replicated mountains or trees.
    # Clear only a narrow cartway corridor; preserve adjacent intact canopies.
    if offset==0:
        # Matrei's meadow beside the protected southeast approach.
        gx=1040+np.mod(xx*.53+yy*.16,265)
        gy=585+np.mod(xx*.11+yy*.27,105)
        ground=bilinear(source,gx,gy)
    else:
        # East ridge's naturally open meadow, right of the existing forest.
        gx=1190+np.mod(xx*.53+yy*.16,265)
        gy=804+np.mod(xx*.11+yy*.27,102)
        ground=bilinear(original,gx,gy)
    # Smooth-edged clearing removes trees BEFORE road painting.
    width=44+3.5*np.sin(along/67)+1.8*np.sin(along/19)
    clear=np.clip((width-dist)/12+.5,0,1)
    clear=clear*clear*(3-2*clear)
    # Grass remains locally shaded, with no artificially bright green stripe.
    ground=np.clip(ground*.88+np.array([8.,8.,3.]),0,255)
    cleared=original*(1-clear[:,:,None])+ground*clear[:,:,None]
    # Natural cartway uses actual registered Matrei road surface.
    road=material(source,along,signed)
    core_width=15.5+1.5*np.sin(along/48)+.8*np.sin(along/13)
    road_alpha=np.clip((core_width-dist)/5+.5,0,1)
    road_alpha=road_alpha*road_alpha*(3-2*road_alpha)
    road_alpha*=.985
    # Slight earth shoulder, entirely inside the tree-free ground corridor.
    shoulder=np.clip((core_width+10-dist)/8,0,1)*(1-road_alpha)
    earth=road*.58+ground*.42
    scene=cleared*(1-shoulder[:,:,None]*.42)+earth*shoulder[:,:,None]*.42
    scene=scene*(1-road_alpha[:,:,None])+road*road_alpha[:,:,None]
    # A single seam material contract: identical road texture at x=1536.
    # No historic bridge or geographic road verification implied.
    return Image.fromarray(np.uint8(np.clip(scene,0,255)),"RGB"),clear,road_alpha

def main():
    for path in (MAT,EAST):
        if not path.is_file():raise SystemExit("Missing original source: "+str(path))
    protected=sha(MAT)
    with Image.open(MAT) as src,Image.open(EAST) as ridge:
        if src.size!=(W,H) or ridge.size!=(W,H):raise RuntimeError("Wrong source dimensions")
        mat=Image.fromarray(registered_matrei(src.convert("RGB")),"RGB")
        new,_,east_road=compose(ridge,mat,W)
        left,left_clear,left_road=compose(mat,mat,0)
    # The Matrei display-only overlay is limited to x>=1351 and the
    # cleared route. The approved V121 file is not altered.
    left_pixels=np.asarray(left,dtype=np.uint8)
    mat_pixels=np.asarray(mat,dtype=np.uint8)
    alpha=np.uint8(np.clip(left_clear*255,0,255))
    alpha[:,:1351]=0
    overlay=Image.fromarray(np.dstack([left_pixels,alpha]),"RGBA")
    output=DIR/"matrei-east-riparian-v7-grounded-road.webp"
    overlay_path=DIR/"matrei-east-v7-matrei-display-overlay.png"
    comparison=DIR/"matrei-east-v7-grounded-contact.webp"
    evidence=DIR/"matrei-east-v7-grounded-evidence.json"
    new.save(output,"WEBP",quality=93,method=6)
    overlay.save(overlay_path,"PNG",optimize=True)
    board=Image.new("RGB",(W*2,H),(17,30,23))
    board.paste(Image.alpha_composite(mat.convert("RGBA"),overlay).convert("RGB"),(0,0))
    board.paste(new,(W,0))
    ImageDraw.Draw(board).line([(W,256),(W,768)],fill=(219,174,100),width=2)
    board.save(comparison,"WEBP",quality=88,method=6)
    if sha(MAT)!=protected:raise RuntimeError("Protected V121 art changed")
    assert int(np.count_nonzero(east_road>.5))>5000
    assert int(np.count_nonzero(alpha))>2000
    data={"schema":"coe-v267-east-v7-grounded/v1","art":output.name,
          "matreiOverlay":overlay_path.name,"comparison":comparison.name,
          "candidateSha256":sha(output),"matreiSourceSha256":protected,
          "source":"existing original authored V4 east ridge and registered V121 dirt-road material",
          "roadWorldPoints":ROUTE,"roadPortContract":{"matrei":[1536,749],
          "east":[0,749],"endpointGapPx":0,"geometryPairedOnly":True},
          "clearedCorridor":True,"roadMaterialFromOriginalMatrei":True,
          "protectedOriginalsUnchanged":True,"fictionalExperimentalRoute":True,
          "visualQualityApproved":False,"physicalRoadSeamVerified":False,
          "riverSeamVerified":False,"mobileWebkitRendered":False,
          "historicallyVerified":False,"nativePlayable":False,
          "userApproved":False,"finished":False,
          "notes":"V7 clears tree canopy beneath the road before laying original Matrei cartway material. Review at full zoom; not a certified road or playable expansion."}
    evidence.write_text(json.dumps(data,indent=2)+"\n")
    print(json.dumps({"art":str(output),"bytes":output.stat().st_size,
          "overlay":str(overlay_path),"contact":str(comparison),
          "protectedMatreiUnchanged":True,"newFinished":0}))
if __name__=="__main__":main()

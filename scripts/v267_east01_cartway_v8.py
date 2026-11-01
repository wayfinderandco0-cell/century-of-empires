#!/usr/bin/env python3
"""V267 EAST-01 V8: remove V7's broad bright berm and bridge-plank road texture.

A narrow, shaded, irregular ground cut under a dirt cartway sampled from the
registered Matrei WEST *dirt* road (not the southeast wooden bridge). Original
EAST V4 ridge art and protected V121 source remain unchanged. QA candidate only.
"""
from __future__ import annotations
import hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
import v267_east01_cartway_v7 as v7
from v267_east01_riparian_v4 import registered_matrei

ROOT=v7.ROOT;DIR=v7.DIR;MAT=v7.MAT;EAST=v7.EAST
W,H=v7.W,v7.H
v7.SOURCE=[(99,478),(160,477),(216,489),(268,511),
           (328,529),(396,536),(448,529),(484,518)]

def compose(base,matrei,offset):
    xx,yy,dist,signed,along=v7.geometry(offset)
    original=np.asarray(base.convert("RGB"),dtype=np.float32)
    source=np.asarray(matrei.convert("RGB"),dtype=np.float32)
    if offset==0:
        gx=1040+np.mod(xx*.53+yy*.16,265)
        gy=585+np.mod(xx*.11+yy*.27,105)
        ground=v7.bilinear(source,gx,gy)
    else:
        gx=1190+np.mod(xx*.53+yy*.16,265)
        gy=804+np.mod(xx*.11+yy*.27,102)
        ground=v7.bilinear(original,gx,gy)
    # V7's ~90px meadow band was visually rejected. V8 has a narrow,
    # darkened cartway cut; tree crowns remain full-scale at its edges.
    clearing_width=25+2.1*np.sin(along/51)+1.3*np.sin(along/17)
    mask=np.clip((clearing_width-dist)/13+.5,0,1)
    mask=mask*mask*(3-2*mask)
    ground=np.clip(ground*.64+original*.18+np.array([3.,4.,2.]),0,255)
    scene=original*(1-mask[:,:,None]*.93)+ground*mask[:,:,None]*.93
    road=v7.material(source,along,signed)
    road_width=12.4+1.3*np.sin(along/44)+.6*np.sin(along/12)
    core=np.clip((road_width-dist)/5+.5,0,1)
    core=core*core*(3-2*core)
    shoulder=np.clip((road_width+7-dist)/7,0,1)*(1-core)
    # Dark earth shoulders, not raised bright-green ribbon.
    earth=np.clip(road*.53+ground*.35+original*.12,0,255)
    scene=scene*(1-shoulder[:,:,None]*.47)+earth*shoulder[:,:,None]*.47
    scene=scene*(1-core[:,:,None]*.97)+road*core[:,:,None]*.97
    return Image.fromarray(np.uint8(np.clip(scene,0,255)),"RGB"),mask,core

def main():
    before=v7.sha(MAT)
    with Image.open(MAT) as source,Image.open(EAST) as ridge:
        if source.size!=(W,H) or ridge.size!=(W,H):raise RuntimeError("Native dimensions required")
        mat=Image.fromarray(registered_matrei(source.convert("RGB")),"RGB")
        new,_,east_road=compose(ridge,mat,W)
        left,mat_mask,_=compose(mat,mat,0)
    alpha=np.uint8(np.clip(mat_mask*255,0,255))
    alpha[:,:1351]=0
    overlay=Image.fromarray(np.dstack([np.asarray(left),alpha]),"RGBA")
    output=DIR/"matrei-east-riparian-v8-narrow-dirt.webp"
    overlay_path=DIR/"matrei-east-v8-matrei-display-overlay.png"
    comparison=DIR/"matrei-east-v8-narrow-dirt-contact.webp"
    evidence=DIR/"matrei-east-v8-narrow-dirt-evidence.json"
    new.save(output,"WEBP",quality=93,method=6)
    overlay.save(overlay_path,"PNG",optimize=True)
    board=Image.new("RGB",(3072,1024),(17,30,23))
    board.paste(Image.alpha_composite(mat.convert("RGBA"),overlay).convert("RGB"),(0,0))
    board.paste(new,(W,0))
    ImageDraw.Draw(board).line([(W,256),(W,768)],fill=(219,174,100),width=2)
    board.save(comparison,"WEBP",quality=88,method=6)
    if v7.sha(MAT)!=before:raise RuntimeError("Protected Matrei changed")
    assert np.count_nonzero(east_road>.5)>3000
    data={"schema":"coe-v267-east-v8-narrow-dirt/v1",
          "sourceOriginal":"matrei-east-riparian-v4.webp",
          "art":output.name,"matreiOverlay":overlay_path.name,
          "comparison":comparison.name,"candidateSha256":v7.sha(output),
          "matreiSourceSha256":before,"roadWorldPoints":v7.ROUTE,
          "sourceRoadPoints":v7.SOURCE,
          "roadPortContract":{"matrei":[1536,749],"east":[0,749],
                              "endpointGapPx":0,"geometryPairedOnly":True},
          "v7BrightBermNarrowed":True,"v7BridgePlankMaterialReplaced":True,
          "protectedOriginalsUnchanged":True,"fictionalExperimentalRoute":True,
          "visualQualityApproved":False,"physicalRoadSeamVerified":False,
          "riverSeamVerified":False,"mobileWebkitRendered":False,
          "nativeCanvasRendered":False,"historicallyVerified":False,
          "nativePlayable":False,"userApproved":False,"finished":False,
          "notes":"V8 review-only original east ridge with narrow shaded dirt cartway; no certified route or bridge."}
    evidence.write_text(json.dumps(data,indent=2)+"\n")
    print(json.dumps({"candidate":str(output),"bytes":output.stat().st_size,
                      "protectedMatreiUnchanged":True,"finished":0}))
if __name__=="__main__":main()

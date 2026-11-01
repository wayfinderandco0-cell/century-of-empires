#!/usr/bin/env python3
"""SOUTH -> southeast source-textured cartway candidate, not gameplay-approved.

Works only on separate candidate art; immutable V267 SOUTH and V123 are never
written. Source: original V267 SOUTH photo and COUNTRYSIDE-04 landscape.
No historical road or town is claimed. Output must pass visual/WebKit review
before any movement seam may be enabled.
"""
from pathlib import Path
import hashlib, json
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT=Path(__file__).resolve().parents[1]
SOUTH=ROOT/"art-reviews/v267-original-source/south-unified-native-border-unapproved.webp"
BASE=ROOT/"terrain-grid/v267-countryside-original/forest-clearing-04-master.webp"
OUT=ROOT/"terrain-grid/v267-southeast-road-01"
W,H=1536,1024
# Exact SOUTH east border (x=1536, local y=578), in world pixel coordinates.
# Candidate road remains a fictional proposal, not a verified historical route.
PATH=[(0,578),(90,580),(210,589),(345,602),(470,613),
      (600,619),(735,609),(865,586),(1010,567),(1140,553)]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def smooth(a): a=np.clip(a,0,1);return a*a*(3-2*a)
def paint(base,south):
    # Work in a tight region; keep every other source pixel untouched.
    rgb=np.asarray(base.convert("RGB")).copy()
    src=np.asarray(south.convert("RGB"))
    x0,x1,y0,y1=0,1210,485,710
    yy,xx=np.mgrid[y0:y1,x0:x1].astype(np.float32)
    distance=np.full(xx.shape,1e8,np.float32)
    signed=np.zeros_like(distance)
    along=np.zeros_like(distance)
    run=0.0
    for (ax,ay),(bx,by) in zip(PATH[:-1],PATH[1:]):
        dx,dy=bx-ax,by-ay;length=float(np.hypot(dx,dy))
        t=np.clip(((xx-ax)*dx+(yy-ay)*dy)/(length*length),0,1)
        vx=xx-(ax+t*dx);vy=yy-(ay+t*dy)
        d=np.hypot(vx,vy)
        pick=d<distance
        distance=np.where(pick,d,distance)
        signed=np.where(pick,(-dy*vx+dx*vy)/length,signed)
        along=np.where(pick,run+t*length,along)
        run+=length
    original=rgb[y0:y1,x0:x1].astype(np.float32)
    # Sample intact meadow from the SAME new countryside photograph, not
    # a flat synthetic green or a duplicate of the SOUTH mountain scene.
    gx=np.clip(750+xx*.17+np.sin(yy*.027)*19,0,W-2).astype(int)
    gy=np.clip(750+(yy-600)*.27+np.sin(xx*.011)*17,0,H-2).astype(int)
    ground=rgb[gy,gx].astype(np.float32)
    clear=smooth((47-distance)/15)
    cleared=original*(1-clear[...,None])+ground*clear[...,None]
    # Natural photographic ruts from SOUTH's real cartway, travelling from
    # its rightmost edge inward toward the stone bridge. Do not clone terrain.
    source_x=np.clip(1535-along*.265,1205,1535).astype(int)
    source_center=578-(1535-source_x)*.061
    source_y=np.clip(source_center+signed,1,H-2).astype(int)
    road=src[source_y,source_x].astype(np.float32)
    # Two worn earth ruts with a grassy center, not a single highway stripe.
    rut=np.maximum(np.exp(-.5*((np.abs(signed)-9)/6)**2),
                   .35*np.exp(-.5*(signed/14)**2))
    road_alpha=smooth((25-distance)/8)*(.42+.55*rut)
    shoulder=smooth((35-distance)/9)*(1-road_alpha)*.30
    earth=road*.65+ground*.35
    scene=cleared*(1-shoulder[...,None])+earth*shoulder[...,None]
    scene=scene*(1-road_alpha[...,None])+road*road_alpha[...,None]
    # Pixel-accurate edge material registration around the physical exit:
    # SOUTH's rightmost photo pixels appear at the new tile's x=0.
    # Fade away within 55 px; never overwrite the protected SOUTH file.
    band=smooth((65-np.abs(yy-578))/18)
    horizontal=smooth((58-xx)/58)
    seam=band*horizontal
    sx=np.clip(1535-xx,0,1535).astype(int)
    seam_pixels=src[yy.astype(int),sx].astype(np.float32)
    scene=scene*(1-seam[...,None])+seam_pixels*seam[...,None]
    rgb[y0:y1,x0:x1]=np.uint8(np.clip(scene,0,255))
    return Image.fromarray(rgb,"RGB")
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    before={str(p.relative_to(ROOT)):sha(p) for p in (SOUTH,BASE)}
    with Image.open(SOUTH) as south,Image.open(BASE) as base:
        assert south.size==base.size==(W,H)
        result=paint(base,south)
        result.save(OUT/"southeast-01-roaded-candidate.webp","WEBP",quality=90,method=6)
        result.resize((768,512),Image.Resampling.LANCZOS).save(
            OUT/"southeast-01-roaded-mobile.webp","WEBP",quality=80,method=6)
        # Contact sheet: source SOUTH right border beside the new west border.
        sheet=Image.new("RGB",(1100,660),(18,29,27))
        dr=ImageDraw.Draw(sheet)
        left=south.convert("RGB").crop((980,360,1536,900)).resize((550,540))
        right=result.crop((0,360,556,900)).resize((550,540))
        sheet.paste(left,(0,65));sheet.paste(right,(550,65))
        dr.text((20,22),"APPROVED SOUTH right edge (unaltered)",fill="#f6dfaa")
        dr.text((565,22),"SOUTHEAST-01 roaded CANDIDATE",fill="#f6dfaa")
        sheet.save(OUT/"southeast-01-seam-contact.webp","WEBP",quality=87)
        s=np.asarray(south.convert("RGB"))
        e=np.asarray(result)
        mismatch=float(np.abs(s[560:597,1535].astype(float)-e[560:597,0].astype(float)).mean())
    assert all(sha(ROOT/p)==h for p,h in before.items()),"Protected source changed"
    meta={"schema":"coe-v267-southeast-roaded-candidate/v1",
      "image":"terrain-grid/v267-southeast-road-01/southeast-01-roaded-candidate.webp",
      "mobileImage":"terrain-grid/v267-southeast-road-01/southeast-01-roaded-mobile.webp",
      "sourceArt":[*before],"sourceSHA256":before,
      "worldOrigin":[3072,1024],"worldSize":[W,H],
      "southExit":[1536,578],"newWestEntry":[0,578],
      "proposedRoadLocal":PATH,
      "pixelSeamMeanRGBError":round(mismatch,3),
      "physicalSeamReviewed":False,"roadSurfaceApproved":False,
      "gameplayEnabled":False,"historicallyVerified":False,"userApproved":False,
      "finished":False,
      "notes":"Original landscape is countryside-04. Separate source-textured derivative; not a fifth unique terrain. Edge RGB alone cannot certify road continuity or movement."}
    (OUT/"southeast-01-source.json").write_text(json.dumps(meta,indent=2)+"\n")
    print(json.dumps({"candidate":meta["image"],"pixelRGBError":mismatch,
      "protectedSourceUnchanged":True,"playable":False}))
if __name__=="__main__":main()

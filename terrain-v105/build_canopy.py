#!/usr/bin/env python3
"""V105 isolated material study: geographically anchored reconstructed canopy.
Uses existing V97 terrain/woods and V102 base. No new geographical measurements.
All canopy and its shadowing are period-style illustrative, not verified forests.
"""
from pathlib import Path
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy.ndimage import map_coordinates, gaussian_filter, zoom

root=Path(__file__).resolve().parents[1]
out=root/"terrain-v105";out.mkdir(exist_ok=True)
src=json.loads((root/"terrain-v97/brenner-data.json").read_text())
feats=json.loads((root/"terrain-v102/features.json").read_text())
west,south,east,north=src["boundsLonLat"]
gw,gh=src["heightGrid"]
woods=np.array(src["treeGrid"],dtype=np.float32).reshape(gh,gw)
dem=np.array(src["elevationM"],dtype=np.float32).reshape(gh,gw)
w,s,e,n=[11.43,47.075,11.625,47.19]
SIZE=2048
rng=np.random.default_rng(105)
longrid=np.linspace(w,e,SIZE,dtype=np.float32)[None,:]
latgrid=np.linspace(n,s,SIZE,dtype=np.float32)[:,None]
# Explicitly broadcast coordinate grids to avoid cubic-resampling offsets.
x=np.broadcast_to((longrid-west)/(east-west)*(gw-1),(SIZE,SIZE))
y=np.broadcast_to((north-latgrid)/(north-south)*(gh-1),(SIZE,SIZE))
h=map_coordinates(dem,[y,x],order=1,mode="nearest")
forest=map_coordinates(gaussian_filter(woods,.65),[y,x],order=1,mode="nearest")
# Independent seeded noise at compatible geographical scales.
def nfield(n,scale=1.):
    return gaussian_filter(zoom(rng.random((n,n),dtype=np.float32),SIZE/n,order=1)[:SIZE,:SIZE],scale)
macro=nfield(20,2)
mid=nfield(90,1.5)
fine=nfield(410,.6)
grain=gaussian_filter(rng.random((SIZE,SIZE),dtype=np.float32),1)
sy,sx=np.gradient(h,(n-s)*111320/SIZE,(e-w)*75735/SIZE)
slope=np.hypot(sx,sy)
# Dense forest masses aligned with V97 woodland and contours; variable gaps.
density=np.clip((forest*.95+macro*.30+mid*.13-.34)*2.3,0,1)
density*=np.clip((2310-h)/420,0,1)
density*=np.clip((1.1-slope)/.7,0,1)
density*=np.clip((1.0-(h-1900)/1400),.2,1)
density*=np.clip(.60+mid*.70,0,1)
density=gaussian_filter(density,2.0)
# Clear modern mapped geographic streams, treating their paths only as guides.
mask=Image.new("L",(SIZE,SIZE),0);dr=ImageDraw.Draw(mask)
def pix(q):return ((q[0]-w)/(e-w)*(SIZE-1),(n-q[1])/(n-s)*(SIZE-1))
for ft in feats["waterways"]:
    if ft["type"] in ("river","stream"):
        pts=[pix(p) for p in ft["coords"]]
        if len(pts)>1:dr.line(pts,fill=240,width=5 if ft["type"]=="river" else 3,joint="curve")
if len(feats["trail"]["coords"])>1:
    dr.line([pix(p) for p in feats["trail"]["coords"]],fill=250,width=3,joint="curve")
gap=np.asarray(mask.filter(ImageFilter.GaussianBlur(5)),dtype=np.float32)/255
density*=1-.76*gap
# Continuous 3D-looking treetop surface: broad dark crowns, modest highlights,
# and multi-scale self-shadowing. Not thousands of isolated identical sprites.
heightfield=gaussian_filter((mid-.5)*.72+(fine-.5)*.55+(grain-.5)*.28,1.35)
gx=np.gradient(heightfield,axis=1)
gy=np.gradient(heightfield,axis=0)
light=np.clip(.87-(gx+gy)*2.15+(mid-.5)*.27+(fine-.5)*.20,.63,1.15)
dark=np.array([41.,69.,45.],dtype=np.float32)
sun=np.array([85.,109.,70.],dtype=np.float32)
mix=np.clip(.45+mid*.38+fine*.20,0,1)
canopy=dark[None,None,:]*(1-mix[...,None])+sun[None,None,:]*mix[...,None]
canopy*=light[...,None]
# Texture exists geographically where forest is expected; rock and clearing remain.
floor=np.asarray(Image.open(root/"terrain-v102/navis-material.webp").convert("RGB"),dtype=np.float32)
if floor.shape[:2]!=(SIZE,SIZE):raise RuntimeError("V102 material size unexpected")
blend=(density*.87)[...,None]
final=np.clip(floor*(1-blend)+canopy*blend,0,255).astype(np.uint8)
Image.fromarray(final,"RGB").save(out/"navis-canopy.webp",quality=93,method=6)
# Small diagnostics to prevent claiming a materially different forest where none baked.
diag={"version":105,"width":SIZE,"height":SIZE,"forestCoverMean":round(float(density.mean()),4),
      "strongForestFraction":round(float((density>.60).mean()),4),
      "artMethod":"continuous multi-scale canopy shade; no repeated tree billboards",
      "sources":"V97 elevation/woodland, V102 local base image and water/trail geographic guides",
      "historicalStatus":"illustrative; no claims of surveyed 1800 vegetation"}
(out/"canopy-report.json").write_text(json.dumps(diag,indent=2)+"\n")
print(json.dumps(diag),flush=True)

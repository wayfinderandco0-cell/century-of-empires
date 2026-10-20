#!/usr/bin/env python3
"""Generate the first high-resolution local terrain panel for Century of Empires.
Uses real Mapzen AWS Terrarium DEM zoom 9, resampled to the same rectangular
equirectangular geographic projection used by the game.
This tile overlays the coarse V89 atlas at zoom: other regions retain V89.
"""
import concurrent.futures
import io
import json
import math
from pathlib import Path
import time
import numpy as np
import requests
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"terrain-detail"
OUT.mkdir(exist_ok=True)
WEST,EAST,SOUTH,NORTH=7.,19.,44.,57.
FULL_W,FULL_H=1448,1086
X=(WEST+14.)/63.*FULL_W
Y=(75.-NORTH)/49.*FULL_H
W=(EAST-WEST)/63.*FULL_W
H=(NORTH-SOUTH)/49.*FULL_H
OUTPUT_W=3072
OUTPUT_H=round(OUTPUT_W*H/W)
ZOOM=9;TILE=256;N=1<<ZOOM

def merc_y(lat):
    return (1.-math.asinh(math.tan(math.radians(lat)))/math.pi)*N/2.
def mer_x(lon):return (lon+180.)/360.*N
x0,x1=int(mer_x(WEST)),int(mer_x(EAST))
y0,y1=int(merc_y(NORTH)),int(merc_y(SOUTH))
mosaic=np.zeros(((y1-y0+1)*TILE,(x1-x0+1)*TILE),dtype=np.float32)
coords=[(x,y) for y in range(y0,y1+1) for x in range(x0,x1+1)]
errors=[]
def download(coord):
    x,y=coord
    url=f"https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{ZOOM}/{x}/{y}.png"
    for retry in range(3):
        try:
            r=requests.get(url,timeout=22)
            if r.status_code==404:return x,y,None,None
            r.raise_for_status()
            a=np.asarray(Image.open(io.BytesIO(r.content)).convert("RGB"),dtype=np.float32)
            return x,y,a[:,:,0]*256+a[:,:,1]+a[:,:,2]/256-32768,None
        except Exception as e:
            if retry==2:return x,y,None,str(e)
            time.sleep(retry+1)
    return x,y,None,"Unexpected error"
print("Central Europe geographic DEM tiles:",len(coords),flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=20) as pool:
    for ix,(x,y,a,err) in enumerate(pool.map(download,coords),1):
        if a is not None:
            i=(y-y0)*TILE;j=(x-x0)*TILE
            mosaic[i:i+TILE,j:j+TILE]=a
        if err:errors.append((x,y,err))
        if ix%80==0:print("Downloaded",ix,"/",len(coords),flush=True)
if len(errors)>4:raise RuntimeError("DEM tile download failed "+repr(errors[:5]))

# Sample directly from DEM at output resolution, never upscale V89's raster.
lons=np.linspace(WEST,EAST,OUTPUT_W,dtype=np.float32)
lats=np.linspace(NORTH,SOUTH,OUTPUT_H,dtype=np.float32)
gx=(lons+180)/360*N*TILE-x0*TILE
gy=np.asarray([merc_y(float(y))*TILE-y0*TILE for y in lats],dtype=np.float32)
gx=np.clip(gx,0,mosaic.shape[1]-1.001);gy=np.clip(gy,0,mosaic.shape[0]-1.001)
xx=gx.astype(np.int32);yy=gy.astype(np.int32)
fx=gx-xx;fy=gy-yy
dem=np.empty((OUTPUT_H,OUTPUT_W),dtype=np.float32)
for r in range(OUTPUT_H):
    a=mosaic[yy[r],xx]*(1-fx)+mosaic[yy[r],xx+1]*fx
    b=mosaic[yy[r]+1,xx]*(1-fx)+mosaic[yy[r]+1,xx+1]*fx
    dem[r]=a*(1-fy[r])+b*fy[r]
del mosaic

# Measured terrain derivatives in metres/metre at each pixel.
dx=(EAST-WEST)/(OUTPUT_W-1)*111320*np.maximum(.3,np.cos(np.radians(lats)))
dy=(NORTH-SOUTH)/(OUTPUT_H-1)*111320
slope_x=np.gradient(dem,axis=1)/dx[:,None]
slope_y=-np.gradient(dem,axis=0)/dy
shade=np.clip(.78+np.clip((-.83*slope_x-.56*slope_y)*3.0,-.38,.38),.48,1.20)
rock=np.clip((np.maximum(0,dem)-350)/1900,0,1)
snow=np.clip((np.maximum(0,dem)-2400)/1200,0,1)
rgb=np.empty((OUTPUT_H,OUTPUT_W,3),dtype=np.uint8)
for channel,(base,rock_delta,peak_delta) in enumerate([(182,-43,74),(192,-57,74),(162,-46,73)]):
    rgb[:,:,channel]=np.clip((base+rock_delta*rock+peak_delta*snow)*shade,0,255).astype('uint8')
del shade,rock,snow,slope_x,slope_y

# Coastline pixels use the same prebuilt Natural Earth 50m geometry as V89.
geo=json.loads((ROOT/"terrain-v89-land.json").read_text())
mask=Image.new("L",(OUTPUT_W,OUTPUT_H),0)
brush=ImageDraw.Draw(mask)
for poly in geo["polygons"]:
    coord=[((x-X)/W*OUTPUT_W,(y-Y)/H*OUTPUT_H) for x,y in poly]
    if len(coord)>=3:brush.polygon(coord,fill=255)
a=np.asarray(mask,dtype=np.float32)/255.
ocean=np.array([26,77,100],dtype=np.float32)
rgb=np.clip(rgb.astype(np.float32)*a[:,:,None]+ocean*(1-a[:,:,None]),0,255).astype('uint8')
del a
rgba=np.empty((OUTPUT_H,OUTPUT_W,4),dtype=np.uint8)
rgba[:,:,:3]=rgb
# Feather panel edges to prevent a hard rectangular seam against V89.
margin=96
alpha_x=np.minimum(np.arange(OUTPUT_W),OUTPUT_W-1-np.arange(OUTPUT_W))/margin
alpha_y=np.minimum(np.arange(OUTPUT_H),OUTPUT_H-1-np.arange(OUTPUT_H))/margin
alpha_x=np.clip(alpha_x,0,1)
alpha_y=np.clip(alpha_y,0,1)
rgba[:,:,3]=np.round(np.minimum(alpha_y[:,None],alpha_x[None,:])*255).astype('uint8')
out=OUT/"central-europe-v90.webp"
Image.fromarray(rgba,'RGBA').save(out,'WEBP',quality=89,method=5)
manifest={
 "source":"Mapzen/AWS elevation-tiles-prod Terrarium z9",
 "projection":"equirectangular",
 "bboxLonLat":[WEST,SOUTH,EAST,NORTH],
 "image":"terrain-detail/central-europe-v90.webp",
 "imageWidth":OUTPUT_W,"imageHeight":OUTPUT_H,
 "x":round(X,6),"y":round(Y,6),"width":round(W,6),"height":round(H,6),
 "gameWidth":FULL_W,"gameHeight":FULL_H,
 "lastVerifiedDEMZoom":ZOOM
}
(OUT/"central-europe-v90.json").write_text(json.dumps(manifest,indent=2)+"\n")
assert OUTPUT_W>=3000 and OUTPUT_H>=3000
assert out.stat().st_size>300_000
print("BUILD VERIFIED",out.name,out.stat().st_size,OUTPUT_W,OUTPUT_H,flush=True)

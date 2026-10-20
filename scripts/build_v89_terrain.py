#!/usr/bin/env python3
"""Build a georeferenced Europe terrain atlas from Mapzen/AWS DEM tiles.
Outputs the SAME geographic projection for map artwork, land mask, and game heights.
Sources: AWS Open Data Mapzen Terrain Tiles and Natural Earth 50m land TopoJSON.
"""
import concurrent.futures, io, json, math, os, time
from pathlib import Path
import numpy as np
import requests
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parents[1]
WEST, EAST, SOUTH, NORTH = -14., 49., 26., 75.
MW, MH = 1448, 1086
W, H = 4096, 3072
ZOOM = 7
N = 1 << ZOOM
TILE = 256

def mercator_y(lat):
    lat = max(-85.0, min(85.0, lat))
    rad = math.radians(lat)
    return (1. - math.asinh(math.tan(rad)) / math.pi) * N / 2.

def tile_x(lon):
    return (lon + 180.) / 360. * N

x0, x1 = int(tile_x(WEST)), int(tile_x(EAST))
y0, y1 = int(mercator_y(NORTH)), int(mercator_y(SOUTH))
print("DEM tiles", (x0, x1, y0, y1), "count", (x1-x0+1)*(y1-y0+1), flush=True)
mosaic = np.zeros(((y1-y0+1)*TILE, (x1-x0+1)*TILE), dtype=np.float32)
failures = []

def tile_work(coord):
    tx, ty = coord
    url = f"https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{ZOOM}/{tx}/{ty}.png"
    for attempt in range(3):
        try:
            r = requests.get(url, timeout=22)
            if r.status_code == 404:
                return tx, ty, None, "404"
            r.raise_for_status()
            rgb = np.asarray(Image.open(io.BytesIO(r.content)).convert("RGB"), dtype=np.float32)
            height = rgb[:,:,0]*256 + rgb[:,:,1] + rgb[:,:,2]/256 - 32768
            return tx, ty, height, None
        except Exception as exc:
            if attempt == 2:
                return tx, ty, None, str(exc)
            time.sleep(1.2 * (attempt+1))

with concurrent.futures.ThreadPoolExecutor(max_workers=18) as pool:
    coordinates = [(x,y) for y in range(y0,y1+1) for x in range(x0,x1+1)]
    for index, (x,y,heights,error) in enumerate(pool.map(tile_work, coordinates), 1):
        if heights is not None:
            row=(y-y0)*TILE;col=(x-x0)*TILE
            mosaic[row:row+TILE,col:col+TILE]=heights
        else:
            failures.append((x,y,error))
        if index % 80 == 0:
            print("Downloaded",index,"/",len(coordinates),flush=True)
if len(failures) > 8:
    raise RuntimeError(f"Too many DEM tiles missing: {len(failures)}; examples: {failures[:5]}")
print("DEM download finished; missing ocean tiles:",len(failures),flush=True)

# Each row of the output is an equal increment of latitude, not Mercator.
lon = np.linspace(WEST,EAST,W,dtype=np.float32)
lat = np.linspace(NORTH,SOUTH,H,dtype=np.float32)
global_x = (lon+180)/360*N*TILE - x0*TILE
global_y = np.array([mercator_y(float(y))*TILE-y0*TILE for y in lat],dtype=np.float32)
ix=np.clip(global_x,0,mosaic.shape[1]-1.001)
iy=np.clip(global_y,0,mosaic.shape[0]-1.001)
xi=ix.astype(np.int32);yi=iy.astype(np.int32)
fx=ix-xi;fy=iy-yi
DEM=np.empty((H,W),dtype=np.float32)
for r in range(H):
    a=mosaic[yi[r],xi]*(1-fx)+mosaic[yi[r],xi+1]*fx
    b=mosaic[yi[r]+1,xi]*(1-fx)+mosaic[yi[r]+1,xi+1]*fx
    DEM[r]=a*(1-fy[r])+b*fy[r]

url="https://raw.githubusercontent.com/cublya/world-atlas/master/land-50m.json"
world=requests.get(url,timeout=40)
world.raise_for_status()
topo=world.json()
scale=topo["transform"]["scale"];trans=topo["transform"]["translate"]
arcs=topo["arcs"]
decoded={}
def arc_points(index):
    if index in decoded: return decoded[index]
    raw=arcs[index if index>=0 else ~index]
    x=y=0;coords=[]
    for dx,dy in raw:
        x+=dx;y+=dy
        lon_=x*scale[0]+trans[0];lat_=y*scale[1]+trans[1]
        coords.append((lon_,lat_))
    if index<0:coords.reverse()
    decoded[index]=coords
    return coords

def projected(poly,width,height):
    return [((p[0]-WEST)/(EAST-WEST)*width,(NORTH-p[1])/(NORTH-SOUTH)*height) for p in poly]

land=Image.new("L",(W,H),0);draw=ImageDraw.Draw(land)
outlines=[]
for shape in topo["objects"]["land"]["arcs"]:
    for ridx,ring in enumerate(shape):
        pts=[]
        for arcid in ring:
            segment=arc_points(arcid)
            if pts and segment and pts[-1]==segment[0]:pts.extend(segment[1:])
            else:pts.extend(segment)
        if len(pts)<3:continue
        coords=projected(pts,W,H)
        draw.polygon(coords,fill=255 if ridx==0 else 0)
        if ridx==0:
            simple=projected(pts,MW,MH)
            outlines.append([[round(x,2),round(y,2)] for x,y in simple])
land_np=np.asarray(land,dtype=np.float32)/255.
print("Land polygons:",len(outlines),flush=True)

# Geographic sun shading; slopes are computed from measured DEM, not noise.
# Horizontal distances are latitude-dependent (Earth curvature).
earth_m_per_deg=111320.
dx=(EAST-WEST)/(W-1)*earth_m_per_deg*np.maximum(.25,np.cos(np.radians(lat)))
dy=(NORTH-SOUTH)/(H-1)*earth_m_per_deg
gx=np.gradient(DEM,axis=1)/dx[:,None]
gy=-np.gradient(DEM,axis=0)/dy
shade=(.78+np.clip((-.83*gx-.56*gy)*3.0,-.35,.35))
sun=np.clip(shade,.51,1.18)
elev=np.clip(DEM,0,4200)
rock=np.clip((elev-350)/1900,0,1)
snow=np.clip((elev-2400)/1200,0,1)
# Subtle green lowlands, tawny uplands, grayish ridges, light alpine summits.
rgb=np.zeros((H,W,3),dtype=np.uint8)
for channel,(base,rockdelta,peakdelta) in enumerate([(182,-43,74),(192,-57,74),(162,-46,73)]):
    value=(base+rockdelta*rock+peakdelta*snow)*sun
    rgb[:,:,channel]=np.clip(value,0,255).astype(np.uint8)
del gx,gy,shade,sun,rock,snow,elev
# Coastal ocean uses navy; land and offshore seamlessly share a projection.
ocean=np.array([26,77,100],dtype=np.float32)
rgb=np.clip(rgb.astype(np.float32)*land_np[:,:,None]+ocean*(1-land_np[:,:,None]),0,255).astype(np.uint8)
img=Image.fromarray(rgb,"RGB")
path=HERE/"terrain-v89.webp"
img.save(path,"WEBP",quality=88,method=5)
print("Atlas saved:",path.name,round(path.stat().st_size/1024),"KiB",flush=True)
print("Height range:",round(float(np.nanmin(DEM))),round(float(np.nanmax(DEM))),flush=True)
low=Image.fromarray(DEM,mode="F").resize((256,192),Image.Resampling.BILINEAR)
heights=[int(round(float(x))) for x in np.asarray(low).flatten()]
(HERE/"terrain-v89-height.json").write_text(json.dumps({
 "source":"Mapzen/AWS Terrarium DEM", "projection":"equirectangular",
 "extent":[WEST,SOUTH,EAST,NORTH], "width":256,"height":192, "heights":heights
},separators=(",",":")),encoding="utf-8")
(HERE/"terrain-v89-land.json").write_text(json.dumps({
 "source":"Natural Earth 50m TopoJSON", "projection":"equirectangular",
 "width":MW,"height":MH,"polygons":outlines
},separators=(",",":")),encoding="utf-8")
print("DONE: artwork, elevation grid, and coastline overlay share the same geographic coordinates.",flush=True)

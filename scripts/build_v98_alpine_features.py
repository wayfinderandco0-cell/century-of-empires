#!/usr/bin/env python3
"""V98 alpine streams and tree-canopy terrain overlays.
Grounded geometry only: mapped OSM waterways and ESA WorldCover 2021 tree-cover class.
The textured canopy is a cartographic visualization, NOT a survey of individual trees.
"""
import json, time
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter
import rasterio
from rasterio.enums import Resampling
from rasterio.transform import from_bounds
from rasterio.warp import reproject
import requests

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"terrain-v98"
OUT.mkdir(exist_ok=True)
WEST,SOUTH,EAST,NORTH=11.26,46.80,11.80,47.42
W,H=2400,2760
ESA="https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/map/ESA_WorldCover_10m_2021_v200_N45E009_Map.tif"
cover=np.zeros((H,W),dtype=np.uint8)
with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR",CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif",GDAL_HTTP_MAX_RETRY="4",GDAL_HTTP_RETRY_DELAY="2"):
    with rasterio.open("/vsicurl/"+ESA) as ds:
        reproject(source=rasterio.band(ds,1),destination=cover,src_transform=ds.transform,src_crs=ds.crs,
            dst_transform=from_bounds(WEST,SOUTH,EAST,NORTH,W,H),dst_crs="EPSG:4326",dst_nodata=0,
            resampling=Resampling.nearest,num_threads=2)
valid=float((cover>0).mean());forest=(cover==10)
if valid<.98 or not (.05<float(forest.mean())<.90):raise RuntimeError("Unreliable WorldCover mask; refusing preview")
print("ESA coverage",valid,"tree cover fraction",float(forest.mean()),flush=True)

rng=np.random.default_rng(5210)
# Spatially coherent canopy-height variation, rather than cartoony standalone tree icons.
fine=np.asarray(Image.fromarray(rng.integers(0,256,(H,W),dtype=np.uint8)).filter(ImageFilter.GaussianBlur(2.1)),dtype=np.float32)
broad=np.asarray(Image.fromarray(rng.integers(0,256,(H,W),dtype=np.uint8)).filter(ImageFilter.GaussianBlur(13)),dtype=np.float32)
# Scale tonal variation after blurring: both shadowed crowns and gaps become perceptible.
val=np.clip((fine-128)*1.5+(broad-128)*3, -38,38)
r=np.clip(54+val*.50,0,255).astype(np.uint8)
g=np.clip(102+val*.85,0,255).astype(np.uint8)
b=np.clip(69+val*.60,0,255).astype(np.uint8)
rgba=np.empty((H,W,4),dtype=np.uint8)
rgba[:,:,0]=r;rgba[:,:,1]=g;rgba[:,:,2]=b
mask=Image.fromarray((forest.astype(np.uint8)*255),'L').filter(ImageFilter.GaussianBlur(1.2))
rgba[:,:,3]=(np.asarray(mask,dtype=np.float32)*.78).astype(np.uint8)
image=OUT/"brenner-canopy.webp"
Image.fromarray(rgba,'RGBA').save(image,'WEBP',quality=86,method=5)
if image.stat().st_size<75000:raise RuntimeError("Unexpectedly small woodland image")
print("Canopy layer:",image.stat().st_size,"bytes",flush=True)

query='[out:json][timeout:90];way["waterway"~"^(stream|river|canal|brook|ditch)$"](46.80,11.26,47.42,11.80);out geom;'
endpoints=["https://overpass.private.coffee/api/interpreter","https://overpass.kumi.systems/api/interpreter","https://overpass-api.de/api/interpreter"]
data=None;errors=[]
for url in endpoints:
    try:
        print("Reading geographically mapped waterways:",url,flush=True)
        response=requests.post(url,data={'data':query},headers={'User-Agent':'CenturyOfEmpiresTerrainTest/0.98 (educational game cartography)'},timeout=125)
        response.raise_for_status()
        data=response.json()
        if not isinstance(data.get('elements'),list):raise ValueError("No features list")
        break
    except Exception as exc:
        errors.append(str(exc)[:250]);time.sleep(2)
if data is None:raise RuntimeError("Could not retrieve real stream geometry "+str(errors))
seen=set();lines=[]
for item in data['elements']:
    if item.get('type')!='way' or item.get('id') in seen:continue
    seen.add(item.get('id'))
    pts=item.get('geometry') or []
    if len(pts)<2:continue
    lonlat=[[round(float(p['lon']),6),round(float(p['lat']),6)] for p in pts]
    if len(lonlat)>1200:lonlat=lonlat[::2]+[lonlat[-1]]
    lines.append({'id':item['id'],'name':item.get('tags',{}).get('name',''),
        'type':item.get('tags',{}).get('waterway','stream'),'coordinates':lonlat})
if len(lines)<60:raise RuntimeError("Local stream network incomplete: "+str(len(lines))+" ways")
# Pick a local wooded, stream-side reference in mountainous stretch near Brenner.
candidate=None;best=-1e10
for line in lines:
    if line['type'] not in ('stream','brook'):continue
    for lon,lat in line['coordinates'][::max(1,len(line['coordinates'])//18)]:
        if not (11.30<lon<11.77 and 46.93<lat<47.31):continue
        x=min(W-1,max(0,int((lon-WEST)/(EAST-WEST)*W)))
        y=min(H-1,max(0,int((NORTH-lat)/(NORTH-SOUTH)*H)))
        local=forest[max(0,y-12):min(H,y+13),max(0,x-12):min(W,x+13)].mean()
        score=3*local-abs(lon-11.51)*2-abs(lat-47.13)*2
        if score>best:best=score;candidate=[lon,lat]
if candidate is None:raise RuntimeError("Could not find forested stream sample to inspect")
dataout={'source':'OpenStreetMap waterway ways via Overpass','licence':'Open Database License; © OpenStreetMap contributors',
 'bboxLonLat':[WEST,SOUTH,EAST,NORTH],'focusLonLat':candidate,'ways':lines}
(OUT/'streams.json').write_text(json.dumps(dataout,separators=(',',':')))
manifest={'sourceForest':'ESA WorldCover 2021 v200, class 10 tree cover, 10m',
 'sourceWaterways':'OpenStreetMap waterway stream/river ways from Overpass',
 'note':'Canopy texture is illustrative and not a survey of individual trees; modern streams/woods are not verified for 1780',
 'imageSize':[W,H],'forestFraction':round(float(forest.mean()),4),
 'waterwayWays':len(lines),'streamFocus':candidate}
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('V98 ASSETS VALIDATED',manifest,flush=True)

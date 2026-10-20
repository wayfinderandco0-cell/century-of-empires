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


# Use a focused request instead of a broad Alpine extract. If Overpass is down,
# fall back to EXISTING measured named Natural Earth rivers, never invented streams.
query='[out:json][timeout:20];way["waterway"~"^(stream|river|brook)$"](46.99,11.40,47.16,11.64);out geom;'
data=None
try:
    url="https://overpass.private.coffee/api/interpreter"
    response=requests.post(url,data={"data":query},timeout=27)
    response.raise_for_status()
    parsed=response.json()
    if len(parsed.get("elements",[]))>=2:data=parsed
except Exception as exc:
    print("Overpass unavailable; limited major-river fallback:",str(exc)[:250],flush=True)
lines=[]
if data is not None:
    seen=set()
    for item in data["elements"]:
        if item.get("type")!="way" or item.get("id") in seen:continue
        seen.add(item.get("id"))
        pts=item.get("geometry") or []
        if len(pts)<2:continue
        coords=[[round(p["lon"],6),round(p["lat"],6)] for p in pts]
        lines.append({"id":item["id"],"name":item.get("tags",{}).get("name",""),
                      "type":item.get("tags",{}).get("waterway","stream"),"coordinates":coords})
    source="OpenStreetMap local waterways via Overpass"
else:
    import re
    ne=json.loads((ROOT/"terrain-v94"/"rivers.json").read_text())
    for n,item in enumerate(ne["rivers"]):
        if item.get("name") not in ("Inn","Adige","Drau","Isar","Salzach"):continue
        nums=[float(k) for k in re.findall(r'-?\\d+(?:\\.\\d+)?',item["d"])]
        coords=[[-14.+nums[i]/1448*63,75.-nums[i+1]/1086*49] for i in range(0,len(nums)-1,2)]
        if not any(WEST<lon<EAST and SOUTH<lat<NORTH for lon,lat in coords):continue
        lines.append({"id":"ne-"+str(n),"name":item["name"],"type":"river",
                      "coordinates":[[round(lon,6),round(lat,6)] for lon,lat in coords]})
    source="Natural Earth 10m major rivers only (OSM small streams unavailable)"
if not lines:raise RuntimeError("Neither local OSM waterways nor Natural Earth mapped rivers available")
candidate=None
best=-1e10
for line in lines:
    for lon,lat in line["coordinates"][::max(1,len(line["coordinates"])//20)]:
        if not(WEST<lon<EAST and SOUTH<lat<NORTH):continue
        x=min(W-1,max(0,int((lon-WEST)/(EAST-WEST)*W)))
        y=min(H-1,max(0,int((NORTH-lat)/(NORTH-SOUTH)*H)))
        coverage=float(forest[max(0,y-12):min(H,y+13),max(0,x-12):min(W,x+13)].mean())
        score=3*coverage-abs(lon-11.51)*2-abs(lat-47.13)*2
        if score>best:best=score;candidate=[lon,lat]
if candidate is None:candidate=[11.51,47.13]
dataout={"source":source,"licence":"Natural Earth public domain" if data is None else "© OpenStreetMap contributors, ODbL",
         "coverage":"major rivers only" if data is None else "local waterways","bboxLonLat":[WEST,SOUTH,EAST,NORTH],
         "focusLonLat":candidate,"ways":lines}
(OUT/'streams.json').write_text(json.dumps(dataout,separators=(',',':')))
manifest={'sourceForest':'ESA WorldCover 2021 v200, class 10 tree cover, 10m',
 'sourceWaterways':source,
 'note':'Canopy texture is illustrative and not a survey of individual trees; modern streams/woods are not verified for 1780',
 'imageSize':[W,H],'forestFraction':round(float(forest.mean()),4),
 'waterwayWays':len(lines),'streamFocus':candidate}
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('V98 ASSETS VALIDATED',manifest,flush=True)

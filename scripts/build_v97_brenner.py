#!/usr/bin/env python3
"""Build V97 Brenner alpine preview from real Copernicus DEM and ESA WorldCover.

Isolated assets, not a game release. Modern land cover is NOT a 1780 forest survey.
"""
import json
import math
from pathlib import Path

import numpy as np
import rasterio
from PIL import Image
from rasterio.enums import Resampling
from rasterio.transform import from_bounds
from rasterio.warp import reproject

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"terrain-v97"
OUT.mkdir(exist_ok=True)
WEST,SOUTH,EAST,NORTH=11.26,46.80,11.80,47.42
WIDTH,HEIGHT=1552,1782
TRANSFORM=from_bounds(WEST,SOUTH,EAST,NORTH,WIDTH,HEIGHT)
COG="https://copernicus-dem-30m.s3.eu-central-1.amazonaws.com"
URLS=[f"{COG}/Copernicus_DSM_COG_10_N{lat}_00_E011_00_DEM/Copernicus_DSM_COG_10_N{lat}_00_E011_00_DEM.tif" for lat in (46,47)]
WORLD="https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/map/ESA_WorldCover_10m_2021_v200_N45E009_Map.tif"

def load_raster(url,output,method,init=False):
    print("Opening publicly hosted geographic data:",url,flush=True)
    with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR",
                      CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif",
                      GDAL_HTTP_MAX_RETRY="4", GDAL_HTTP_RETRY_DELAY="2"):
        with rasterio.open("/vsicurl/"+url) as ds:
            print("Source dimensions",ds.width,ds.height,"CRS",ds.crs,flush=True)
            reproject(
                source=rasterio.band(ds,1),destination=output,
                src_transform=ds.transform,src_crs=ds.crs,src_nodata=ds.nodata,
                dst_transform=TRANSFORM,dst_crs="EPSG:4326",
                dst_nodata=-32768 if output.dtype==np.float32 else 0,
                init_dest_nodata=init,resampling=method,
                num_threads=2
            )

dem=np.full((HEIGHT,WIDTH),-32768,dtype=np.float32)
for url in URLS:
    load_raster(url,dem,Resampling.bilinear,init=False)
valid=(dem>-1000)&np.isfinite(dem)
coverage=float(valid.mean())
print("Height coverage",coverage,flush=True)
if coverage<0.98:raise RuntimeError("Missing high-resolution DEM coverage")
dem=np.where(valid,dem,float(np.median(dem[valid]))).astype(np.float32)

cover=np.zeros((HEIGHT,WIDTH),dtype=np.uint8)
load_raster(WORLD,cover,Resampling.nearest,init=True)
land_coverage=float((cover>0).mean())
print("ESA WorldCover coverage",land_coverage,flush=True)
if land_coverage<0.98:raise RuntimeError("Missing WorldCover tile coverage")
forest=cover==10
shrub=cover==20

meters_x=111320*math.cos(math.radians((SOUTH+NORTH)/2))*(EAST-WEST)/WIDTH
meters_y=111320*(NORTH-SOUTH)/HEIGHT
down,east=np.gradient(dem,meters_y,meters_x)
# Approximate directional slope shadow: shaded relief at high detail.
nx=-east;ny=down;nz=np.ones_like(dem)
norm=np.sqrt(nx*nx+ny*ny+nz*nz)
light=np.clip((nx*(-.50)+ny*.49+nz*.72)/norm,0.05,1)
shade=np.clip(.63+.58*(light-.30),.39,1.22)
alt=np.clip((dem-530)/2500,0,1)
low=np.asarray((154.,166.,136.),dtype=np.float32)
high=np.asarray((205.,204.,183.),dtype=np.float32)
rgb=(low*(1-alt[...,None])+high*alt[...,None])*shade[...,None]
trees=np.asarray((66.,106.,75.),dtype=np.float32)
rgb[forest]=rgb[forest]*.66+trees*.34
rgb[shrub]=rgb[shrub]*.87+trees*.13
snow=cover==70
rgb[snow]=np.minimum(250,rgb[snow]*.45+125)
rgb=np.clip(rgb,0,255).astype("uint8")
image=OUT/"brenner-relief.webp"
Image.fromarray(rgb,"RGB").save(image,"WEBP",quality=88,method=5)
print("Saved relief",image,image.stat().st_size,flush=True)

# Reduced numeric terrain grid for route calculations; native image retains pixel detail.
GW,GH=260,300
hgrid=np.asarray(Image.fromarray(dem,"F").resize((GW,GH),Image.Resampling.BILINEAR)).round().astype("int16")
forest_grid=np.asarray(Image.fromarray(forest.astype("uint8")*255,"L").resize((GW,GH),Image.Resampling.NEAREST))
data={
 "boundsLonLat":[WEST,SOUTH,EAST,NORTH],
 "image":"terrain-v97/brenner-relief.webp",
 "imageSize":[WIDTH,HEIGHT],
 "heightGrid":[GW,GH],
 "elevationM":hgrid.ravel().tolist(),
 "treeGrid":(forest_grid>0).astype("uint8").ravel().tolist(),
 "elevationSource":"Copernicus DEM GLO-30 Public 2021",
 "landCoverSource":"ESA WorldCover 2021 v200",
 "note":"Modern woodland proxy, not verified 1780 forest distribution",
 "coverage":{"elevation":round(coverage,5),"landCover":round(land_coverage,5)},
 "minElevation":round(float(dem.min()),1),
 "maxElevation":round(float(dem.max()),1)
}
(OUT/"brenner-data.json").write_text(json.dumps(data,separators=(",",":")))
manifest={k:v for k,v in data.items() if k not in ("elevationM","treeGrid")}
(OUT/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
assert image.stat().st_size>150000
assert hgrid.max()>2000 and hgrid.min()>300
assert forest.any() and not forest.all()
print("V97 build validated",manifest,flush=True)

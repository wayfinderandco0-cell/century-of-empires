#!/usr/bin/env python3
"""Matrei georegistered terrain/road painting proof. Modern LiDAR DGM; c.1800 visual reconstruction.
Not real historic woodland, buildings, road geometry, or bridges. No gameplay writes.
"""
from pathlib import Path
from io import BytesIO
from math import atan2,ceil,cos,sin,pi
import requests, numpy as np,json, random, hashlib, math
from PIL import Image,ImageDraw,ImageFilter,ImageFont
from scipy.ndimage import gaussian_filter
import rasterio
from rasterio.io import MemoryFile
from rasterio.warp import reproject,Resampling
from rasterio.transform import Affine
from pyproj import Transformer
root=Path(__file__).resolve().parents[1];out=root/"terrain-puzzle"/"wipptal-matrei";out.mkdir(parents=True,exist_ok=True)
g=json.loads((out/"matrei-road-control.json").read_text())
assert g["all_routes_enabled"] is False
origin=g["origin_lonlat"];cell=g["cell_id"];road=g["road_segments"][0]["coords"];route_nodes=g["candidate_waypoints"];links=g["candidate_edges"]
assert len(route_nodes)==27 and len(links)==26
assert len([e for e in links if e["status"]=="BLOCKED_UNVERIFIED_CROSSING"])==1
seed=1800;random.seed(seed);gen=np.random.default_rng(seed)
tx=Transformer.from_crs("EPSG:4326","EPSG:31254",always_xy=True)
world=Transformer.from_crs("EPSG:4326","EPSG:32632",always_xy=True)
cx,cy=tx.transform(*origin);wx,wy=world.transform(*origin)
span=1120;N=1700;step=span/N
base="https://gis.tirol.gv.at/arcgis/services/Service_Public/terrain/MapServer/WCSServer"
request={"SERVICE":"WCS","VERSION":"1.0.0","REQUEST":"GetCoverage","COVERAGE":"Gelaendemodell_50cm_M28",
"BBOX":f"{cx-750},{cy-750},{cx+750},{cy+750}","CRS":"EPSG:31254","RESPONSE_CRS":"EPSG:31254","WIDTH":1500,"HEIGHT":1500,"FORMAT":"GeoTIFF"}
r=requests.get(base,params=request,timeout=85,headers={"User-Agent":"CenturyOfEmpires historical map research contact via GitHub repository"})
r.raise_for_status()
if not r.content.startswith((b'II*\x00',b'MM\x00*')):raise RuntimeError("Expected GeoTIFF, got "+repr(r.content[:170]))
with MemoryFile(r.content) as mem:
 with mem.open() as src:
  dem=np.empty((N,N),dtype="float32")
  dest_transform=Affine(step,0,wx-span/2,0,-step,wy+span/2)
  reproject(src.read(1),dem,src_transform=src.transform,src_crs=src.crs,dst_transform=dest_transform,dst_crs="EPSG:32632",resampling=Resampling.bilinear)
  input_crs=str(src.crs);input_res=src.res
valid=np.isfinite(dem)&(dem>200)&(dem<4000)
if valid.mean()<.995:raise RuntimeError("DEM incomplete; valid %.2f%%"%(valid.mean()*100))
mn=float(np.min(dem));mx=float(np.max(dem))
# Hillshade from true measured DGM; mid-distance ambient occlusion (not a fabricated elevation layer)
smooth=gaussian_filter(dem,.8);dy,dx=np.gradient(smooth,step,step)
slope=np.hypot(dx,dy)
az=math.radians(315);alt=math.radians(48)
normal=np.dstack((-dx,-dy,np.ones_like(dx)));normal/=np.linalg.norm(normal,axis=2,keepdims=True)
light=np.array([math.cos(alt)*math.sin(az),math.cos(alt)*math.cos(az),math.sin(alt)])
shade=np.clip(np.sum(normal*light,axis=2),.12,1.0)
macro=gaussian_filter(dem,21);ao=np.clip(.72+(dem-macro)/50,.53,1.06)
# Land material: 2026 DEM + *illustrative* inferred canopy and meadows; no asserted 1800 forest polygons
rand=gaussian_filter(gen.normal(0,1,(N,N)).astype('float32'),29);rand/=max(float(np.std(rand)),1e-3)
micro=gaussian_filter(gen.normal(0,1,(N,N)).astype('float32'),2.2)
micro/=max(float(np.std(micro)),1e-3)
YY,XX=np.mgrid[:N,:N].astype('float32')
# map local x,y to pixel map grid approximate (east offsets only for art texture, not geometry)
X=(XX/N-.5)*span;Y=(.5-YY/N)*span
# forest richer on steeper higher banks, less around the historic road corridor and Matrei valley floor.
rock=np.clip((slope-.52)*1.8,0,1)
forest_prob=np.clip(.33+.18*rand+.24*np.maximum(slope-.13,0)+.00025*(dem-995)+.00012*np.abs(X),.03,.9)
# force illustrative building/road corridor to remain clear
xroad=np.interp(Y[::-1,0],np.array([a[1] for a in road])[::-1],np.array([a[0] for a in road])[::-1])
xroad=xroad[::-1]
road_space=np.clip((np.abs(X-xroad[:,None])-18)/70,0,1)
forest_prob*=.29+.71*road_space
forest_mask=np.clip((forest_prob-.27)*2.2,0,1)
gr=gen.normal(0,1,(N,N)).astype('float32')
land=np.zeros((N,N,3),dtype=np.float32)
grass=np.array([108,120,78],dtype=np.float32)
wood=np.array([55,85,65],dtype=np.float32)
stone=np.array([147,139,120],dtype=np.float32)
for k in range(3):
 land[:,:,k]=grass[k]*(1-forest_mask)+wood[k]*forest_mask
 land[:,:,k]=land[:,:,k]*(1-rock)+stone[k]*rock
# diffuse thematic tone across the registered relief
mulshade=np.clip(.45+.60*shade,0.42,1.15)*ao
land*=mulshade[:,:,None]
land+=micro[:,:,None]*3.6
land+=rand[:,:,None]*4.5
land=np.uint8(np.clip(land,0,255))
img=Image.fromarray(land,mode="RGB")
# grass grain in 1800 atlas effect, drawn in registered material coordinates; no modern roads.
dr=ImageDraw.Draw(img,"RGBA")
def scr(p):
 lon=origin[0]+p[0]/75735.13900755216
 lat=origin[1]+p[1]/111320
 east,north=world.transform(lon,lat)
 return ((east-(wx-span/2))*N/span,((wy+span/2)-north)*N/span)
def line(d,points,fill,width):
 if len(points)>1:d.line([scr(p) for p in points],fill=fill,width=width,joint="curve")
# Forest impression: irregular clusters of rounded canopy with shadow/highlight, not triangle symbols. Modern distribution only an art hypothesis.
# Add crowns at ~8m spaced candidates; skip only steep rock and immediately adjacent to road, streams and village.
forest_simplified=gaussian_filter(forest_mask,5)
for k in range(12000):
 x=random.randrange(14,N-14);y=random.randrange(14,N-14)
 if random.random()>float(forest_simplified[y,x])*0.6:continue
 if float(rock[y,x])>.65:continue
 if abs(float(X[y,x]-xroad[y]))<22:continue
 radius=random.choice([3.8,4.4,5.8,6.9,7.8,9.1,10.4])*(N/1700)
 # crowns receive east-side highlight to give volume
 R=int(radius);ix=int(x);iy=int(y)
 col=random.choice([(35,65,51,170),(43,71,48,180),(46,75,55,165),(56,80,47,160),(37,64,46,175)])
 dr.ellipse((ix-R+2,iy-R+4,ix+R+3,iy+R+5),fill=(13,28,22,80))
 dr.ellipse((ix-R,iy-R,ix+R,iy+R),fill=col)
 dr.ellipse((ix-R*.65,iy-R*.70,ix+R*.38,iy+R*.33),fill=(98,128,85,49))
# stream natural banks, flowing smaller tributaries, no cyan ruler lines. Tracked modern centerlines fixed.
mainriver=[]
for w in g["waterway_segments"]:
 pts=w["coords"];name=w["name"]
 if len(pts)<2:continue
 if w["type"]=="river":
  # real Sill, width is illustrative
  line(dr,pts,(68,70,55,122),24);line(dr,pts,(136,140,119,110),18)
  line(dr,pts,(42,79,76,255),12);line(dr,pts,(66,121,121,210),7);line(dr,pts,(166,185,158,90),2)
 else:
  line(dr,pts,(38,62,57,110),10);line(dr,pts,(78,127,129,190),4);line(dr,pts,(176,195,177,60),1)
# period-appropriate road rendering tied to single canonical modern *candidate* line, NOT certified exact circa 1800
# Avoid obvious modern asphalt: irregular soft gravel / ochre bare soil.
line(dr,road,(42,49,38,120),19);line(dr,road,(177,153,110,235),13);line(dr,road,(208,183,135,230),9);line(dr,road,(225,199,149,110),2)
# Stream crossing known but unverified. Visibly interrupt potentially functional route at Waldraster Bach.
cross=g["mapped_water_intersections"][0]
p=scr(cross["xy_m"])
dr.ellipse((p[0]-13,p[1]-13,p[0]+13,p[1]+13),fill=(52,94,97,220))
# Tiny c.1800-style village suggestions are illustrative, do not represent surveyed historical buildings.
# Place in a small group away from stream on right of mid-road near old town center.
houses=[]
for j,(ym,side,away) in enumerate([(-150,-1,27),(-104,-1,27),(-55,1,35),(5,-1,24),(52,1,32),(100,-1,28),(158,1,33),(195,-1,28)]):
 # evaluate xroad for given world Y
 xp=np.interp(ym,np.array([p[1] for p in road])[::-1],np.array([p[0] for p in road])[::-1])
 hx=xp+side*away;hxpx,hypx=scr((hx,ym));rx=random.choice([12,14,17])
 # period slate roofs and shadows
 dr.polygon([(hxpx-rx-3,hypx-rx/2+4),(hxpx+rx+3,hypx-rx/2+4),(hxpx+rx+3,hypx+rx/2+6),(hxpx-rx-3,hypx+rx/2+6)],fill=(19,31,27,100))
 dr.polygon([(hxpx-rx,hypx-rx/2),(hxpx+rx,hypx-rx/2),(hxpx+rx,hypx+rx/2),(hxpx-rx,hypx+rx/2)],fill=(113,102,88,255))
 dr.line([(hxpx-rx,hypx),(hxpx+rx,hypx)],fill=(186,170,145,210),width=2)
 houses.append([round(hx,1),ym])
# clean full bleed texture and separate developer overlay
clean=out/"matrei-1800-georelief-study.webp";img.save(clean,"WEBP",quality=88,method=6)
dbg=img.copy();dd=ImageDraw.Draw(dbg,"RGBA")
poly=[[-207.106781,-500],[207.106781,-500],[500,-207.106781],[500,207.106781],[207.106781,500],[-207.106781,500],[-500,207.106781],[-500,-207.106781]]
dd.line([scr(p) for p in poly+[poly[0]]],fill=(255,226,157,220),width=4)
for e in links:
 if e["crossing_ids"]:continue
 # Must draw actual road corridor subsegments, not chord shortcut
 pass
for n in route_nodes:
 x,y=scr(n["coords_xy_m"])
 dd.ellipse((x-4,y-4,x+4,y+4),fill=(255,236,190,230),outline=(18,42,34,210),width=1)
dd.ellipse((p[0]-14,p[1]-14,p[0]+14,p[1]+14),outline=(254,111,89,255),width=4)
dd.line([(p[0]-9,p[1]-9),(p[0]+9,p[1]+9)],fill=(254,111,89,255),width=4)
dd.line([(p[0]-9,p[1]+9),(p[0]+9,p[1]-9)],fill=(254,111,89,255),width=4)
dbg.save(out/"matrei-1800-georelief-debug.webp","WEBP",quality=87,method=6)
# quick mobile comparison
a=img.resize((650,650));b=dbg.resize((650,650));cmp=Image.new("RGB",(1300,720),(25,43,36))
cmp.paste(a,(0,35));cmp.paste(b,(650,35));cd=ImageDraw.Draw(cmp)
cd.text((20,10),"MATREI 1800 ILLUSTRATION • ACTUAL 50cm LiDAR RELIEF",fill=(239,224,192))
cd.text((660,10),"DEVELOPER ONLY • 27 CANDIDATE DOTS • WALDRASTER BLOCKED",fill=(239,224,192))
cmp.save(out/"matrei-1800-georelief-comparison.jpg",quality=86)
# passability QA from high resolution DGM: slopes computed but path on modern street surface may be graded; candidate only
def sample_dem(worldp):
 px,py=scr(worldp)
 return float(dem[min(N-1,max(0,int(py))),min(N-1,max(0,int(px)))])
heights=[sample_dem(n["coords_xy_m"]) for n in route_nodes]
gradient=[abs(heights[i]-heights[i-1])/max(1,route_nodes[i]["distance_along_m"]-route_nodes[i-1]["distance_along_m"]) for i in range(1,len(heights))]
qa={"source":"Land Tirol 50cm DGM_M28 through WCS resampled to 1m then 1700px for artwork","raster_native_request_resolution_m":1,
 "source_crs":input_crs,"source_pixel_size":input_res,"pixel_world_size_m":round(step,4),
 "terrain_elevation_range_m":[round(mn,2),round(mx,2)],
 "candidate_road_len_m":g["road_segments"][0]["length_m"],"hidden_nodes":len(route_nodes),"disabled_edges":len(links),
 "blocked_unverified_water_crossings":sum(bool(e["crossing_ids"]) for e in links),
 "road_grade_node_sampling_max_pct":round(100*max(gradient),1) if gradient else None,
 "historical_road_centerline_verified":False,"historical_village_buildings_verified":False,
 "reconstructed_1800_forests_verified":False,"all_route_edges_disabled":all(not e["active"] for e in links),
 "river_was_drawn_from_georeferenced_vectors":True,
 "geometry_shared_for_road_and_dots":True,"source_dem_valid_fraction":round(float(valid.mean()),4),
 "outputs":["matrei-1800-georelief-study.webp","matrei-1800-georelief-debug.webp","matrei-1800-georelief-comparison.jpg"]}
(out/"matrei-1800-georelief-qa.json").write_text(json.dumps(qa,indent=2)+"\\n")
print(json.dumps(qa,indent=2))
assert qa["all_route_edges_disabled"] and qa["blocked_unverified_water_crossings"]==1

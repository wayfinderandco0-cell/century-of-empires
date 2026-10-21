#!/usr/bin/env python3
"""Matrei historical-corridor geographic-control build.
Uses *modern* OSM street data for a guide and archived V97 broad DEM,
never certifies the modern street centerline as the c.1800 road.
All route edges remain gameplay-disabled. No alterations to campaign code.
"""
from __future__ import annotations
from pathlib import Path
from urllib.request import Request, urlopen
from xml.etree import ElementTree as ET
from datetime import datetime, timezone
import base64,io,json,math,re
from PIL import Image,ImageDraw,ImageFilter
from shapely.geometry import LineString,Polygon,Point
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"terrain-puzzle"/"wipptal-matrei";OUT.mkdir(parents=True,exist_ok=True)
ORIGIN=(11.453056,47.130278) # Wikimedia Commons photograph of historic Matrei Brennerstraße
MLAT=111320.0;MLON=75735.139
PITCH=1000.0;CORNER=PITCH/(2+math.sqrt(2));H=PITCH/2-CORNER
POLY=[(-H,-500),(H,-500),(500,-H),(500,H),(H,500),(-H,500),(-500,H),(-500,-H)]
POLYGON=Polygon(POLY)
CELL="WIP:O:0:0"
def metric(lon,lat):return ((lon-ORIGIN[0])*MLON,(lat-ORIGIN[1])*MLAT)
def geodist(a,b):return math.hypot(a[0]-b[0],a[1]-b[1])
def rnd(p):return [round(p[0],5),round(p[1],5)]
# Trim to a slight out-of-cell buffer, and preserve provenance of each line.
bbox=[ORIGIN[0]-0.012,ORIGIN[1]-0.008,ORIGIN[0]+0.012,ORIGIN[1]+0.008]
url="https://api.openstreetmap.org/api/0.6/map?bbox="+",".join(map(str,bbox))
response=urlopen(Request(url,headers={"User-Agent":"CenturyOfEmpiresHistoricalAtlasStudy/0.1 (open source terrain experiment)"}),timeout=55)
raw=response.read(13_000_000)
if not raw.startswith(b'<?xml') and not raw.startswith(b'<osm'):raise RuntimeError("Expected OSM XML")
root=ET.fromstring(raw)
nodes={x.get("id"):(float(x.get("lon")),float(x.get("lat"))) for x in root.findall("node")}
roads=[];streams=[]
for w in root.findall("way"):
 tags={t.get("k"):t.get("v") for t in w.findall("tag")}
 ids=[n.get("ref") for n in w.findall("nd")]
 if len(ids)<2 or any(i not in nodes for i in ids):continue
 pts=[metric(*nodes[i]) for i in ids]
 name=tags.get("name","")
 hw=tags.get("highway","")
 ref=tags.get("ref","")
 # Only an identified modern mapped Brenner street is allowed as a candidate historic alignment.
 qualifies=hw in {"primary","secondary","tertiary","unclassified","residential","living_street"} and (
  "brennerstra" in name.lower().replace("ß","ss").replace(" ","") or
  bool(re.search(r'(^|[;, ])B\s*182($|[;, ])',ref,re.I)) or
  ("hauptstra" in name.lower().replace("ß","ss").replace(" ","")))
 if qualifies:
  roads.append({"osm_way_id":w.get("id"),"name":name,"modern_ref":ref,"modern_highway_class":hw,"coords":pts})
 water=tags.get("waterway") in {"stream","river"}
 if water:
  streams.append({"osm_way_id":w.get("id"),"name":name,"kind":tags.get("waterway","water"),"coords":pts})
if not roads:raise RuntimeError("No mapped Brennerstraße / B182 candidate in Matrei footprint. Do not invent road.")
# Clip candidate road parts to the actual octagon; keep all disconnected segments separate.
def parts(line):
 inter=LineString(line).intersection(POLYGON)
 if inter.is_empty:return []
 return [inter] if inter.geom_type=="LineString" else list(inter.geoms) if inter.geom_type=="MultiLineString" else []
road_lines=[]
for r in roads:
 for p in parts(r["coords"]):
  if p.length>12:road_lines.append({**{k:v for k,v in r.items() if k!="coords"},"coords":[rnd(a) for a in p.coords],"length_m":round(p.length,2)})
if not road_lines:raise RuntimeError("Brennerstraße modern path not within this octagon; location correction needed")

# Join successive modern road *ways* at their actual shared endpoints.
# OpenStreetMap storage boundaries are NOT road gaps and must not create disconnected troop dots.
raw_road_segments=road_lines[:]
pending=raw_road_segments[:]
start_index=max(range(len(pending)),key=lambda i:max(pending[i]["coords"][0][1],pending[i]["coords"][-1][1]))
seed=pending.pop(start_index)
chain=seed["coords"][:]
if chain[-1][1]>chain[0][1]:chain.reverse()
ordered_ways=[seed["osm_way_id"]]
merge_max_gap_m=2.0
max_observed_join_gap=0.0
while pending:
 cur=chain[-1]
 proposals=[]
 for i,line in enumerate(pending):
  p=line["coords"]
  proposals.append((geodist(cur,p[0]),i,False))
  proposals.append((geodist(cur,p[-1]),i,True))
 gap,i,reverse=min(proposals)
 if gap>merge_max_gap_m:
  raise RuntimeError("Brennerstraße guide has a real unmapped gap of %.2fm. Do NOT connect by a fake straight shortcut."%gap)
 seg=pending.pop(i)
 coords=seg["coords"][::-1] if reverse else seg["coords"]
 max_observed_join_gap=max(max_observed_join_gap,gap)
 chain.extend(coords[1:])
 ordered_ways.append(seg["osm_way_id"])
line_length=LineString(chain).length
road_lines=[{"name":"Brennerstraße / B182 (modern alignment)",
             "modern_ref":"B182","modern_highway_class":"mixed",
             "source_osm_way_ids":ordered_ways,
             "coords":[rnd(p) for p in chain],
             "length_m":round(line_length,2),
             "historical_alignment_verified":False,
             "max_join_gap_m":round(max_observed_join_gap,4)}]

river_lines=[]
for r in streams:
 for p in parts(r["coords"]):
  if p.length>8:river_lines.append({"name":r["name"],"type":r["kind"],"osm_way_id":r["osm_way_id"],"coords":[rnd(a) for a in p.coords],"length_m":round(p.length,2)})
# Route polyline is from guide, not a fake straight-line shape. Dots every 30-40m and all disabled.
links=[];waypoints=[]
for lineidx,line in enumerate(road_lines):
 geom=LineString(line["coords"])
 n=max(2,math.ceil(geom.length/40)+1)
 prev=None
 for k in range(n):
  d=k/(n-1)*geom.length;p=geom.interpolate(d)
  nid=f"{CELL}:R{lineidx}:N{k}"
  waypoints.append({"id":nid,"coords_xy_m":rnd((p.x,p.y)),"road_source_ways":line["source_osm_way_ids"],"line_id":lineidx,"distance_along_m":round(d,2),"visible_in_game":False,"approved_for_movement":False})
  if prev:links.append({"from":prev,"to":nid,"line_id":lineidx,"active":False,"historical_alignment_verified":False,"troop_suitability":"pending_terrain_check"})
  prev=nid
# Sample retained DEM for context: broad landforms only.
dem=json.loads((ROOT/"terrain-v97/brenner-data.json").read_text())
bounds=dem["boundsLonLat"];NX,NY=dem["heightGrid"];arr=dem["elevationM"]
def elev(x,y):
 lon=ORIGIN[0]+x/MLON;lat=ORIGIN[1]+y/MLAT
 u=max(0,min(NX-1.00001,(lon-bounds[0])/(bounds[2]-bounds[0])*(NX-1)))
 v=max(0,min(NY-1.00001,(bounds[3]-lat)/(bounds[3]-bounds[1])*(NY-1)))
 i=int(u);j=int(v);a=u-i;b=v-j;k=j*NX+i
 return (arr[k]*(1-a)+arr[k+1]*a)*(1-b)+(arr[k+NX]*(1-a)+arr[k+NX+1]*a)*b
# Coarse DEM gradient and mapped water-intersection audit only, not a road certification.
# Use 10m along-geometry sampling to avoid skipping sharp turns in the modern guide.
road_geom=LineString(road_lines[0]["coords"])
observations=[]
for d in range(0,int(road_geom.length)+1,10):
 pp=road_geom.interpolate(d);observations.append((d,elev(pp.x,pp.y)))
last=road_geom.interpolate(road_geom.length)
observations.append((road_geom.length,elev(last.x,last.y)))
grades=[]
for i in range(1,len(observations)):
 dd=observations[i][0]-observations[i-1][0]
 if dd>0:grades.append(abs(observations[i][1]-observations[i-1][1])/dd)
road_terrain_estimate={
 "elevation_north_entry_m":round(elev(*road_lines[0]["coords"][0]),1),
 "elevation_south_exit_m":round(elev(*road_lines[0]["coords"][-1]),1),
 "maximum_coarse_model_grade_pct":round(100*max(grades),1) if grades else None,
 "total_descent_m":round(sum(max(0,a[1]-b[1]) for a,b in zip(observations,observations[1:])),1),
 "dem_adequacy":"CANNOT_CERTIFY_REAL_GRADIENT_OR_HISTORIC_WHEELED_ACCESS"}
water_intersections=[]
for w in river_lines:
 inter=road_geom.intersection(LineString(w["coords"]))
 if not inter.is_empty:
  water_intersections.append({"waterway":w["name"],"geometry_type":inter.geom_type,"crossing_approved":False})

elev_summary={"origin_elevation_m":round(elev(0,0),1),
 "center_north_500_m":round(elev(0,500),1),"center_south_500_m":round(elev(0,-500),1),
 "resolution_warning":"V97 retained grid ~160-230m, insufficient to certify path gradients or bridges"}
# Terrain image from geographically registered V97 relief, NOT new fake trees.
relief=Image.open(ROOT/"terrain-v97/brenner-relief.webp").convert("RGB")
WIDTH,HEIGHT=1200,1200;pad=70;side=1060
# sample V97 relief using its own bounds and correct geographic alignment
base=Image.new("RGB",(WIDTH,HEIGHT))
px=base.load(); data=relief.load();sw,sh=relief.size
for Y in range(HEIGHT):
 yy=(side/2-(Y-pad))*1120/side
 lat=ORIGIN[1]+yy/MLAT
 sy=int(max(0,min(sh-1,(bounds[3]-lat)/(bounds[3]-bounds[1])*(sh-1))))
 for X in range(WIDTH):
  xx=((X-pad)-side/2)*1120/side
  lon=ORIGIN[0]+xx/MLON
  sx=int(max(0,min(sw-1,(lon-bounds[0])/(bounds[2]-bounds[0])*(sw-1))))
  px[X,Y]=data[sx,sy]
# Image used only as a geographic debug; no assertion of visual quality.
base=base.filter(ImageFilter.GaussianBlur(.65))
def screen(point):
 return (pad+side/2+point[0]*side/1120,pad+side/2-point[1]*side/1120)
im=base.copy();draw=ImageDraw.Draw(im,"RGBA")
octpts=[screen(p) for p in POLY]
draw.polygon(octpts,outline=(249,225,169,235),width=3)
for water in river_lines:
 draw.line([screen(p) for p in water["coords"]],fill=(114,203,219,200),width=4,joint="curve")
for road in road_lines:
 draw.line([screen(p) for p in road["coords"]],fill=(44,33,25,210),width=9,joint="curve")
 draw.line([screen(p) for p in road["coords"]],fill=(228,192,123,240),width=4,joint="curve")
for p in waypoints:
 x,y=screen(p["coords_xy_m"]);draw.ellipse((x-4,y-4,x+4,y+4),fill=(248,237,200,225),outline=(28,51,39,255),width=1)
draw.rectangle((0,0,WIDTH,65),fill=(20,41,36,245))
draw.text((25,14),"MATREI / WIPPTAL   |   HISTORIC ROAD CORRIDOR STUDY",fill="#f7eacb")
draw.text((25,37),"MODERN ROAD ALIGNMENT ONLY -- 1800 CENTERLINE & BRIDGES NOT VERIFIED",fill="#f0c58c")
draw.rectangle((0,1130,WIDTH,1200),fill=(20,41,36,245))
draw.text((25,1150),"DEVELOPER CONTROLS: old Brenner trade route historically documented; movement graph INACTIVE",fill="#e0dbc4")
imgpath=OUT/"matrei-modern-road-control.jpg"
im.save(imgpath,quality=87,optimize=True)
# Small JPEG can be inspected through GitHub's UTF-8 connector without retrieving binary files.
buf=io.BytesIO();im.resize((600,600)).save(buf,format="JPEG",quality=74)
(OUT/"matrei-control-preview.jpeg.base64.txt").write_text(base64.b64encode(buf.getvalue()).decode())

control={"schema_version":"1.0","cell_id":CELL,
 "status":"MODERN_MAPPED_ROAD_GEOMETRY_CANDIDATE_HISTORIC_ROUTE_EXISTS_NOT_EXACTLY_LOCATED",
 "origin_lonlat":list(ORIGIN),"projection":"local metric longitude/latitude approximation (x east, y north), not Europe-wide projection",
 "octagon_pitch_m":1000,"polygon_xy_m":[rnd(p) for p in POLY],
 "sources":{"osm_api_url":url,"osm_downloaded_utc":datetime.now(timezone.utc).isoformat(),
  "map_data_attribution":"© OpenStreetMap contributors, ODbL; modern geometries, NOT 1800 road survey",
  "dem_source":"terrain-v97/brenner-data.json, Copernicus GLO-30-derived coarse retained 260x300 grid",
  "relief_source":"terrain-v97/brenner-relief.webp",
  "historic_road_evidence":["https://orawww.uibk.ac.at/apex/uprod/f?p=LLW:3:0::NO::P3_ID:1179",
   "https://austria-forum.org/af/AustriaWiki/Brennerstra%C3%9Fe",
   "https://www.steinach.gv.at/Leben_in_Steinach/Wissenswertes/Geschichte"]},
 "route_alignment_source":"modern OSM named Brennerstraße or B182 or Hauptstraße; period-exact centerline unverified",
 "road_segments":road_lines,"waterway_segments":river_lines,
 "candidate_waypoints":waypoints,"candidate_edges":links,"all_routes_enabled":False,
 "historical_road_existed_during_game":True,"exact_road_location_1800_verified":False,
 "crossings_approved":[],"artwork_state":"GEOGRAPHIC_CONTROL_ONLY_NOT_PREMIUM_TERRAIN_ART",
 "dem_context":elev_summary,"coarse_road_gradient":road_terrain_estimate,"mapped_water_intersections":water_intersections,"road_entry_exit_candidates":[{"edge":"N","xy_m":road_lines[0]["coords"][0],"approved":False},{"edge":"S","xy_m":road_lines[0]["coords"][-1],"approved":False}]}
(OUT/"matrei-road-control.json").write_text(json.dumps(control,indent=2)+"\n")
validation={"road_segments":len(road_lines),"original_osm_ways_joined":len(ordered_ways),"max_segment_join_gap_m":round(max_observed_join_gap,4),"continuous_centerline":len(road_lines)==1 and len(ordered_ways)>=3,"river_segments":len(river_lines),
 "nodes":len(waypoints),"links":len(links),"all_edges_off":all(not e["active"] for e in links),
 "candidate_in_polygon":all(POLYGON.buffer(.001).covers(Point(p["coords_xy_m"])) for p in waypoints),
 "historic_exact_alignment_not_claimed":not control["exact_road_location_1800_verified"],
 "no_approved_crossings":not control["crossings_approved"],
 "max_coarse_road_grade_pct":road_terrain_estimate["maximum_coarse_model_grade_pct"],"mapped_water_crossings":len(water_intersections),"candidate_entry_exit_edges":["N","S"],"dem_origin_m":elev_summary["origin_elevation_m"],
 "historical_market_origin_lonlat":list(ORIGIN)}
if not all((validation[k] for k in ("road_segments","continuous_centerline","nodes","all_edges_off","candidate_in_polygon","historic_exact_alignment_not_claimed","no_approved_crossings"))):raise RuntimeError("Failed route QA: "+str(validation))
(OUT/"matrei-road-qa.json").write_text(json.dumps(validation,indent=2)+"\n")
print(json.dumps(validation,indent=2),flush=True)

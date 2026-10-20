#!/usr/bin/env python3
"""Extract actual mapped streams in a small Brenner Pass valley from OpenStreetMap.
The public OSM map API returns node+way geometry directly, avoiding the failed
Overpass service. No estimated polylines or major-river substitution.
"""
import json
import xml.etree.ElementTree as ET
from pathlib import Path
import requests

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"terrain-v99"
OUT.mkdir(exist_ok=True)
BBOX=(11.48,47.10,11.56,47.17)
URL="https://api.openstreetmap.org/api/0.6/map"
print("Requesting OSM map extract",BBOX,flush=True)
res=requests.get(URL,params={"bbox":",".join(map(str,BBOX))},
  headers={"User-Agent":"CenturyOfEmpires geographic research preview 0.99"},
  timeout=(12,65))
print("OSM HTTP status",res.status_code,"bytes",len(res.content),flush=True)
res.raise_for_status()
if len(res.content)<1000:raise RuntimeError("Unexpectedly small OSM map response")
root=ET.fromstring(res.content)
nodes={}
for n in root.findall("node"):
 nodes[n.attrib["id"]]=[round(float(n.attrib["lon"]),7),round(float(n.attrib["lat"]),7)]
lines=[]
for way in root.findall("way"):
 tags={t.attrib["k"]:t.attrib["v"] for t in way.findall("tag")}
 typ=tags.get("waterway","")
 if typ not in {"stream","river","brook","canal","ditch"}:continue
 coords=[nodes[ref.attrib["ref"]] for ref in way.findall("nd") if ref.attrib["ref"] in nodes]
 if len(coords)<2:continue
 lines.append({"id":way.attrib["id"],"type":typ,"name":tags.get("name",""),
               "coords":coords})
print("OSM mapped waterways",len(lines),"named",sum(bool(x['name']) for x in lines),flush=True)
if len(lines)<3:raise RuntimeError("Too few real watercourses at focus area; do not claim success")
# Prefer a real stream way near the center of the tested mountains, not a made-up line.
focus=[]
for line in lines:
 if line["type"] not in {"stream","brook"}:continue
 for lon,lat in line["coords"]:
  dist=(lon-11.52)**2 + ((lat-47.13)*1.47)**2
  focus.append((dist,[lon,lat]))
if not focus:raise RuntimeError("No genuine local stream in chosen forest study area")
center=min(focus,key=lambda a:a[0])[1]
result={"source":"OpenStreetMap API 0.6 public map extract",
        "license":"© OpenStreetMap contributors, ODbL 1.0",
        "boundsLonLat":list(BBOX),"focusLonLat":center,
        "waterways":lines,"count":len(lines)}
(OUT/"brenner-streams.json").write_text(json.dumps(result,separators=(",",":")))
(OUT/"manifest.json").write_text(json.dumps({
    "streamSource":"OpenStreetMap API (not fallback or speculative geometry)",
    "streamSegments":len(lines),"focusLonLat":center,
    "aerialSource":"basemap.at government orthophoto WMTS, CC BY 4.0",
    "aerialNote":"Live tiles, not copied or stored in the game repository",
    "elevationSource":"Copernicus GLO-30 from V97",
    "historicNote":"Modern geographic sources, not verified 1780 river and forest distribution"
},indent=2)+"\n")
print("V99 local real stream extract validated",center,flush=True)

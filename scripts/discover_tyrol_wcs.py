#!/usr/bin/env python3
"""Diagnose official Tyrol WCS coverage layers; no gameplay or atlas files touched."""
from urllib.parse import urlencode
import requests,xml.etree.ElementTree as ET,json,datetime,sys
from pathlib import Path
out=Path(__file__).resolve().parents[1]/"terrain-puzzle"/"wipptal-matrei"
out.mkdir(exist_ok=True,parents=True)
base="https://gis.tirol.gv.at/arcgis/services/Service_Public/terrain/MapServer/WCSServer"
info={"endpoint":base,"date_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"requests":[]}
for version in ["1.0.0","2.0.1"]:
 try:
  r=requests.get(base,params={"SERVICE":"WCS","REQUEST":"GetCapabilities","VERSION":version},timeout=42,
     headers={"User-Agent":"CenturyOfEmpires/0.1 (historical terrain research)"})
  text=r.text[:2000]
  item={"version":version,"status":r.status_code,"bytes":len(r.content),"sample":text[:200]}
  if r.status_code==200 and r.content.strip().startswith(b"<"):
   root=ET.fromstring(r.content)
   item["root"]=root.tag
   names=[];heads=[]
   for child in root.iter():
    local=child.tag.rsplit("}",1)[-1]
    if local in ("CoverageOfferingBrief","CoverageSummary","CoverageOffering"):
     for sub in child:
      typ=sub.tag.rsplit("}",1)[-1]
      if typ in ("name","CoverageId","Title","Identifier"):
       names.append({"tag":typ,"value":(sub.text or "")[:180]})
    if local in ("CoverageId","name") and child.text and len(heads)<200:
     heads.append(child.text.strip()[:100])
   item["coverages"]=names[:120];item["all_ids"]=heads[:120]
   (out/("tyrol-wcs-capabilities-"+version+".xml")).write_bytes(r.content)
  info["requests"].append(item)
 except Exception as e:info["requests"].append({"version":version,"error":str(e)[:350]})
(out/"tirol-high-res-source-discovery.json").write_text(json.dumps(info,indent=2)+"\n")
print(json.dumps(info,indent=2)[:12000])
if not any("root" in x for x in info["requests"]):raise SystemExit(1)

#!/usr/bin/env python3
from pathlib import Path
from io import BytesIO
from datetime import datetime,timezone
import base64,json,re
import requests
import numpy as np
from PIL import Image
from pyproj import Transformer
out=Path(__file__).resolve().parents[1]/"terrain-puzzle"/"wipptal-matrei";out.mkdir(parents=True,exist_ok=True)
center=(11.453056,47.130278)
x,y=Transformer.from_crs("EPSG:4326","EPSG:31254",always_xy=True).transform(*center)
base="https://gis.tirol.gv.at/arcgis/services/Service_Public/orthofoto/MapServer/WMSServer"
headers={"User-Agent":"CenturyOfEmpires map development (github.com/wayfinderandco0-cell/century-of-empires)"}
info={"date_utc":datetime.now(timezone.utc).isoformat(),"endpoint":base,"requested_layer":"Image_Aktuell_RGB","crs":"EPSG:31254",
      "center_lonlat":list(center),"center_xy":[x,y],"extent_m":600,"era":"modern photography - NOT c.1800",
      "license":"CC BY 4.0, Land Tirol","gameplay_modified":False}
cap=requests.get(base,params={"SERVICE":"WMS","REQUEST":"GetCapabilities","VERSION":"1.3.0"},headers=headers,timeout=30)
info.update({"capabilities_http":cap.status_code,"layer_found":"Image_Aktuell_RGB" in cap.text})
if not info["layer_found"]:
 info["possible_layers"]=re.findall(r"<(?:[^:>]*:)?Name>([^<]+)</",cap.text)[:70]
params={"SERVICE":"WMS","REQUEST":"GetMap","VERSION":"1.3.0","LAYERS":"Image_Aktuell_RGB",
 "STYLES":"","FORMAT":"image/jpeg","CRS":"EPSG:31254",
 "BBOX":f"{x-300},{y-300},{x+300},{y+300}","WIDTH":900,"HEIGHT":900}
r=requests.get(base,params=params,headers=headers,timeout=65)
info.update({"image_http":r.status_code,"content_type":r.headers.get("Content-Type"),"bytes":len(r.content)})
if r.status_code!=200 or not r.content.startswith(b"\xff\xd8"):
 info["response_sample"]=r.text[:450]
 (out/"matrei-orthophoto-probe.json").write_text(json.dumps(info,indent=2)+"\n")
 raise RuntimeError("WMS did not return JPEG")
im=Image.open(BytesIO(r.content)).convert("RGB")
a=np.asarray(im)
info.update({"size":list(im.size),"rgb_std":[round(float(np.std(a[:,:,i])),1) for i in range(3)]})
info["sufficient_visual_variation"]=im.size==(900,900) and min(info["rgb_std"])>=7

# A uniform white JPEG can be HTTP 200 when WMS bbox axis order does not match.
# Probe interoperable alternative CRSs and 1.1.1's deterministic E/N axis convention.
info["alternates"]=[]
if not info["sufficient_visual_variation"]:
 from pyproj import Transformer
 XX,YY=Transformer.from_crs("EPSG:4326","EPSG:3857",always_xy=True).transform(*center)
 candidates=[
  ("wms111_native",{"VERSION":"1.1.1","SRS":"EPSG:31254","BBOX":f"{x-300},{y-300},{x+300},{y+300}"}),
  ("wms130_bbox_swapped",{"VERSION":"1.3.0","CRS":"EPSG:31254","BBOX":f"{y-300},{x-300},{y+300},{x+300}"}),
  ("wms130_webmercator",{"VERSION":"1.3.0","CRS":"EPSG:3857","BBOX":f"{XX-430},{YY-430},{XX+430},{YY+430}"}),
  ("wms111_webmercator",{"VERSION":"1.1.1","SRS":"EPSG:3857","BBOX":f"{XX-430},{YY-430},{XX+430},{YY+430}"})]
 for label,patch in candidates:
  pp={**params,**patch}
  if "SRS" in patch:pp.pop("CRS",None)
  try:
   rr=requests.get(base,params=pp,headers=headers,timeout=40)
   candidate={"method":label,"http_status":rr.status_code,"bytes":len(rr.content)}
   if rr.status_code==200 and rr.content.startswith(b"\xff\xd8"):
    ii=Image.open(BytesIO(rr.content)).convert("RGB")
    aa=np.asarray(ii)
    candidate["rgb_std"]=[round(float(np.std(aa[:,:,k])),2) for k in range(3)]
    if min(candidate["rgb_std"])>=7 and ii.size==(900,900):
     info["sufficient_visual_variation"]=True
     info["successful_method"]=label
     im=ii
     info["rgb_std"]=candidate["rgb_std"]
   else:candidate["reply"]=rr.text[:160]
   info["alternates"].append(candidate)
   if info["sufficient_visual_variation"]:break
  except Exception as ex:info["alternates"].append({"method":label,"error":str(ex)[:250]})

im.save(out/"matrei-official-modern-orthophoto-reference.jpg",quality=85)
preview=im.resize((620,620),Image.Resampling.LANCZOS)
buf=BytesIO();preview.save(buf,format="JPEG",quality=65,optimize=True)
(out/"matrei-modern-orthophoto-reference-preview.base64.txt").write_text(base64.b64encode(buf.getvalue()).decode())
info["validated"]="retrieval_only_no_historical_claim" if info["sufficient_visual_variation"] else "returned_jpeg_but_blank_or_low_variation_NEEDS_RESEARCH"
(out/"matrei-orthophoto-probe.json").write_text(json.dumps(info,indent=2)+"\n")
print(json.dumps(info,indent=2))

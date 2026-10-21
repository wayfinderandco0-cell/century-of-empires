#!/usr/bin/env python3
"""Safely probe small Matrei DEM WCS crops, saving formats/diagnostics, no invented heights."""
import requests,json,io,os
from pyproj import Transformer
from pathlib import Path
from rasterio.io import MemoryFile
ROOT=Path(__file__).resolve().parents[1];out=ROOT/"terrain-puzzle"/"wipptal-matrei";out.mkdir(exist_ok=True,parents=True)
base="https://gis.tirol.gv.at/arcgis/services/Service_Public/terrain/MapServer/WCSServer"
tx=Transformer.from_crs("EPSG:4326","EPSG:31254",always_xy=True)
cx,cy=tx.transform(11.453056,47.130278)
result={"wcs":base,"target_crs":"EPSG:31254","center":(cx,cy),"trials":[]}
for layer in ["Gelaendemodell_50cm_M28","Gelaendemodell_5m_M28"]:
 for fmt in ["GeoTIFF","image/tiff"]:
  params={"SERVICE":"WCS","VERSION":"1.0.0","REQUEST":"GetCoverage","COVERAGE":layer,"BBOX":f"{cx-150},{cy-150},{cx+150},{cy+150}",
      "CRS":"EPSG:31254","RESPONSE_CRS":"EPSG:31254","WIDTH":300,"HEIGHT":300,"FORMAT":fmt}
  test={"layer":layer,"format":fmt}
  try:
   r=requests.get(base,params=params,timeout=42)
   test.update({"http_status":r.status_code,"size_bytes":len(r.content),"content_type":r.headers.get("content-type"),"body_head":r.text[:140] if len(r.content)<3000 else ""})
   if r.status_code==200 and len(r.content)>10000:
    with MemoryFile(r.content) as mem:
     with mem.open() as src:
      v=src.read(1,masked=True)
      test.update({"valid_raster":True,"bounds":list(src.bounds),"crs":str(src.crs),"min":float(v.min()),"max":float(v.max()),"nodata":src.nodata,"shape":list(v.shape),"data_type":str(v.dtype)})
      if not v.mask.all(): (out/"matrei-test-wcs-300m.tif").write_bytes(r.content)
  except Exception as ex:test["error"]=str(ex)[:250]
  result["trials"].append(test)
  if test.get("valid_raster"):break
 if any(t.get("valid_raster") for t in result["trials"]):break
(out/"matrei-highres-wcs-probe.json").write_text(json.dumps(result,indent=2)+"\n")
print(json.dumps(result,indent=2))
if not any(t.get("valid_raster") for t in result["trials"]):raise SystemExit(1)

#!/usr/bin/env python3
"""V231: two independently CC0-licensed original Austrian oblique photo studies.
Not Matrei geography, historical cartways, route registration, or approved art.
No automated crop scoring; fixed candidate regions selected for review.
"""
import argparse, hashlib, io, json, time
from pathlib import Path
import cv2
import numpy as np
import requests
from PIL import Image
from build_v229_austrian_source_art import ROADS, SIZE, FALSE_FLAGS, assert_immutable_roads
from build_v230_grounded_alpine_art import ground_contact, choose_meadow_strip

SOURCES = {
  "west": {
    "title": "Forested mountain valley (Unsplash).jpg",
    "url": "https://upload.wikimedia.org/wikipedia/commons/5/52/Forested_mountain_valley_%28Unsplash%29.jpg",
    "sourceSha1": "4a01fd2356056ceea1bfdf0374751040fdbd0145",
    "dimensions": [4288, 2848], "crop": [1350, 1450, 2886, 2474],
    "author": "Stijn te Strake", "place": "Schoenenbach, Bezau, Austria",
  },
  "south": {
    "title": "Alpine valley (Unsplash).jpg",
    "url": "https://upload.wikimedia.org/wikipedia/commons/e/e9/Alpine_valley_%28Unsplash%29.jpg",
    "sourceSha1": "29667d44329ad6a36ce8f881e16dbcc51f8995db",
    "dimensions": [5472, 3078], "crop": [2400, 1550, 3936, 2574],
    "author": "Paul Gilmore", "place": "Brandenberg Alps, Austria",
  },
}
KIND = "UNAPPROVED_DISTINCT_CC0_OBLIQUE_AUSTRIAN_ART"
LICENSE = "CC0 1.0"
LICENSE_URL = "https://creativecommons.org/publicdomain/zero/1.0/"

def download(info):
  for attempt, delay in enumerate([0, 15, 35, 70]):
    if delay: time.sleep(delay)
    response=requests.get(info["url"],timeout=90,headers={
      "User-Agent":"CenturyOfEmpires/0.2 (CC0 photo provenance; https://github.com/wayfinderandco0-cell/century-of-empires/issues/9)"})
    if response.status_code==429 and attempt<3: continue
    response.raise_for_status()
    raw=response.content
    sha1=hashlib.sha1(raw).hexdigest()
    if sha1!=info["sourceSha1"]: raise ValueError("STOP: source SHA1 changed: "+sha1)
    image=Image.open(io.BytesIO(raw)).convert("RGB")
    if list(image.size)!=info["dimensions"]: raise ValueError("STOP: source image dimensions changed")
    return np.asarray(image),hashlib.sha256(raw).hexdigest()
  raise RuntimeError("Source unavailable; no unverified substitution")

def build(output):
  assert_immutable_roads()
  output.mkdir(parents=True,exist_ok=True)
  records={}
  for cell,info in SOURCES.items():
    original,sha256=download(info)
    crop=info["crop"]
    if crop[2]-crop[0]!=SIZE[0] or crop[3]-crop[1]!=SIZE[1]:
      raise ValueError("Non-native crop: "+cell)
    scene=original[crop[1]:crop[3],crop[0]:crop[2]].copy()
    # Single nonrepeating 1536px native ground strip follows unchanged V123 points.
    # This is illustrative and does NOT prove a real historical cartway or roadbank.
    meadow,strip=choose_meadow_strip(original,crop)
    prepared=ground_contact(scene,meadow,ROADS[cell])
    filename=cell+"-austrian-natural-cover-v231.webp"
    path=output/filename
    Image.fromarray(prepared).save(path,"WEBP",quality=91,method=6)
    raw=path.read_bytes()
    # Report camera/texture mismatch rather than silently claiming success.
    lab=cv2.cvtColor(prepared,cv2.COLOR_RGB2LAB)
    fine=np.abs(lab[:,:,0].astype(np.float32)-cv2.GaussianBlur(lab[:,:,0].astype(np.float32),(0,0),1.4))
    records[cell]=dict(info,file=filename,nativePixels=list(SIZE),
      sourceImagePixels=info["dimensions"],sourceSha256=sha256,
      outputSha256=hashlib.sha256(raw).hexdigest(),outputBytes=len(raw),
      license=LICENSE,licenseUrl=LICENSE_URL,
      sourcePage="https://commons.wikimedia.org/wiki/File:"+info["title"].replace(" ","_"),
      nonrepeatingGroundStrip=strip,
      sourceCropMetrics={"fine":round(float(fine.mean()),4)},
      modifications="Fixed native 1536x1024 photo crop; source-ground strip follows immutable V123 polyline with 14px core and 37px fade; unverified fictional art",
      **FALSE_FLAGS)
  if records["west"]["sourceSha256"]==records["south"]["sourceSha256"]: raise ValueError("Duplicate source")
  manifest=dict(version=231,kind=KIND,
    sourceRegion="Two different Austrian Alpine valleys, NOT Matrei",
    license=LICENSE,notHistorical1780Geography=True,
    cartwaysAndBridgeBanksNotSurveyed=True,
    sourceLandmarkTiepointsVerified=False,selectionIsSemanticVerification=False,
    sources=records,**FALSE_FLAGS)
  (output/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
  print(json.dumps({cell:{"crop":r["crop"],"sha256":r["outputSha256"],
    "fine":r["sourceCropMetrics"]["fine"]} for cell,r in records.items()},indent=2))
  return manifest

if __name__=="__main__":
  parser=argparse.ArgumentParser()
  parser.add_argument("--output",type=Path,default=Path("terrain-v231/assets"))
  build(parser.parse_args().output)

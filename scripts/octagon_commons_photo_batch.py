#!/usr/bin/env python3
"""Add geographically differentiated licensed photographic SOURCE candidates.

Source photographs are native-pixel terrain reference art, not historic surveys,
finished cartways, conquerable towns or playable cells. Do not use a photograph
to assert exact georegistration or 1780-period buildings/roads.
"""
from __future__ import annotations
import hashlib, html, json, re, time, urllib.parse, urllib.request
from pathlib import Path
from PIL import Image, ImageEnhance, ImageDraw

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"terrain-grid/factory-photo"
CACHE=OUT/"source-cache"
W,H=1536,1024
# One distinct source per cell, geographically appropriate REGION only.
# Each approximate center is an independently known modern geographic feature,
# not a photo ground-control point or period-road verification.
SOURCES=[
 dict(id="eu-05-14",title="Alps aerial 1.jpg",author="Kallerna",
      region="Mont Blanc and Aosta Valley, western Alps",
      lon=6.86,lat=45.83,biome="alpine",motif="Western Alps high ridges and valley",
      license="CC BY-SA 4.0"),
 dict(id="eu-07-12",title="Aerial image of the Danube Gorge near Weltenburg.jpg",
      author="Carsten Steger",region="Danube gorge, Bavaria, Germany",
      lon=11.83,lat=48.90,biome="hills-and-mountains",
      motif="Forested Danube limestone gorge",license="CC BY-SA 4.0"),
 dict(id="eu-08-15",title="Dalmatia Vrgoračko Polje and Gradac coastal city IMG 9880.JPG",
      author="Bjoertvedt",region="Dalmatian coastal mountains, Croatia",
      lon=17.43,lat=43.21,biome="coast-or-lowland",
      motif="Adriatic coast, limestone mountains and coastal lowlands",
      license="CC BY-SA 4.0"),
]
USER_AGENT="CenturyOfEmpiresArtResearch/1.0 (GitHub open-source educational game; Wikimedia attribution retained)"
def digest(data):return hashlib.sha256(data).hexdigest()
def request(url):
 req=urllib.request.Request(url,headers={"User-Agent":USER_AGENT,"Accept":"application/json,image/*;q=0.9,*/*;q=0.5"})
 for n in range(3):
  try:
   with urllib.request.urlopen(req,timeout=55) as response:return response.read()
  except Exception:
   if n==2:raise
   time.sleep(3*(n+1))
def commons_source(spec):
 params=urllib.parse.urlencode({"action":"query","format":"json","prop":"imageinfo",
   "titles":"File:"+spec["title"],"iiprop":"url|size|extmetadata","iiurlwidth":3072})
 data=json.loads(request("https://commons.wikimedia.org/w/api.php?"+params))
 pages=list(data["query"]["pages"].values())
 if len(pages)!=1 or "imageinfo" not in pages[0]:raise RuntimeError("Missing Commons source: "+spec["title"])
 info=pages[0]["imageinfo"][0]
 metadata=info.get("extmetadata",{})
 short=html.unescape(re.sub("<[^>]+>","",metadata.get("LicenseShortName",{}).get("value",""))).strip()
 if short!=spec["license"]:raise RuntimeError("License changed or incompatible for "+spec["title"]+": "+short)
 url=info.get("thumburl") or info["url"]
 raw=request(url)
 if len(raw)<200_000:raise RuntimeError("Unexpectedly small Commons photo "+spec["title"])
 return raw,url,info,short
def cell_id(lon,lat):
 c=int((lon+14)*18/63);r=int((75-lat)*24/49)
 return f"eu-{c:02d}-{r:02d}"
def main():
 CACHE.mkdir(parents=True,exist_ok=True)
 manifest_path=OUT/"manifest.json"
 manifest=json.loads(manifest_path.read_text())
 if manifest["schema"]!="coe-photo-art/v1":raise RuntimeError("Unexpected base manifest")
 # Geography planning cells are V94 grid bins, not a photo georeferencing claim.
 expected={x["id"]:x for x in manifest["cells"]}
 for spec in SOURCES:
  if cell_id(spec["lon"],spec["lat"])!=spec["id"]:
   raise RuntimeError("Source region does not match proposed V94 cell "+spec["title"])
  if spec["id"] in expected:raise RuntimeError("Duplicate photo candidate "+spec["id"])
  raw,url,info,license_short=commons_source(spec)
  src=CACHE/(spec["id"]+"-commons.jpg")
  src.write_bytes(raw)
  with Image.open(src) as im:
   if im.width<W or im.height<H:raise RuntimeError("Insufficient native photo resolution")
   im=im.convert("RGB")
   # Native 1:1 crop. Upper sky/modern infrastructure is NOT guaranteed excluded;
   # these candidates remain quarantined until manual visual review.
   left=(im.width-W)//2
   top=max(0,min(im.height-H,round((im.height-H)*.58)))
   crop=(left,top,left+W,top+H)
   art=im.crop(crop)
  art=ImageEnhance.Color(art).enhance(.87)
  art=ImageEnhance.Contrast(art).enhance(1.035)
  art=ImageEnhance.Brightness(art).enhance(.92)
  outfile=OUT/(spec["id"]+".webp")
  art.save(outfile,"WEBP",quality=92,method=6)
  expected[spec["id"]]={
   "id":spec["id"],"grid":[int(spec["id"][3:5]),int(spec["id"][6:8])],
   "origin":[int(spec["id"][3:5])*W,int(spec["id"][6:8])*H],
   "geography":{"biome":spec["biome"],"source":"V94 geographic grid; approximate source region only"},
   "image":"terrain-grid/factory-photo/"+outfile.name,"imageSize":[W,H],
   "originalSource":"terrain-grid/factory-photo/source-cache/"+src.name,
   "sourceCrop":list(crop),"sourceSha256":digest(raw),
   "outputSha256":digest(outfile.read_bytes()),
   "sourcePage":"https://commons.wikimedia.org/wiki/File:"+urllib.parse.quote(spec["title"].replace(" ","_")),
   "downloadUrl":url,"author":spec["author"],"license":license_short,
   "licenseUrl":"https://creativecommons.org/licenses/by-sa/4.0/",
   "motif":spec["motif"],"sourceRegion":spec["region"],
   "approximateRegionCenter":[spec["lon"],spec["lat"]],
   "exactPhotoGeoreferenced":False,"periodSafe":False,
   "modernFeaturesQuarantined":False,"originalTerrainSource":True,
   "sourceBackedPhotographicArtComposed":True,"artMethodApproved":False,
   "physicallyRoadSeamChecked":False,"paintedRoads":[],"gameplayEnabled":False,
   "historicallyVerified":False,"visuallyReviewedOnPhone":False,
   "provinceIds":[],"scenicSettlements":[],"strategicTowns":[]
  }
 manifest["cells"]=list(expected.values())
 manifest["photographicArtComposed"]=len(expected)
 manifest["sourceDiversityRegions"]=sorted({c["sourceRegion"] for c in expected.values()})
 manifest["finishedToday"]=0
 manifest["status"]="source-backed-unapproved-not-georegistered"
 manifest_path.write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+"\n")
 rows=[]
 for c in manifest["cells"]:
  rows.append('<article><img loading="lazy" src="'+Path(c["image"]).name+'" alt="'+html.escape(c["motif"])+'"><h2>'+c["id"]+
   '</h2><p>'+html.escape(c["motif"])+' · '+html.escape(c["sourceRegion"])+
   '</p><p>Photo: '+html.escape(c["author"])+' · '+html.escape(c["license"])+
   '. Not a historical or road-certified playable tile.</p></article>')
 (OUT/"index.html").write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Europe source photography batch</title><style>body{background:#172b24;color:#f7e7cb;font:15px system-ui;margin:12px}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:12px}article{border:1px solid #b49a6c;padding:9px;background:#263c30}img{width:100%;aspect-ratio:3/2;object-fit:contain}p{font-size:12px}</style><h1>Source-backed photographic candidate batch</h1><p>Original native-resolution crops from distinct licensed sources. Regional resemblance only; not georegistered historical terrain. No invented roads, towns or conquest nodes. These are NOT finished octagons.</p><main>'+''.join(rows)+'</main></html>')
 contact=Image.new("RGB",(768*3,560*2),"#1b2b22")
 d=ImageDraw.Draw(contact)
 for i,c in enumerate(manifest["cells"]):
  x=(i%3)*768;y=(i//3)*560
  im=Image.open(ROOT/c["image"]).convert("RGB")
  contact.paste(im.resize((768,512),Image.Resampling.LANCZOS),(x,y))
  d.text((x+8,y+520),c["id"]+" · "+c["sourceRegion"][:60],fill="#f9e8c9")
 contact.save(OUT/"photo-contact.webp","WEBP",quality=86)
 print(json.dumps({"sourceBackedPhotoCandidates":len(expected),"newRegions":len(SOURCES),"finished":0}))
if __name__=="__main__":main()

#!/usr/bin/env python3
"""Source-image seam contact sheet; visual evidence, NOT passability certification."""
import argparse,hashlib,json
from pathlib import Path
from PIL import Image,ImageDraw

root=Path(__file__).resolve().parent.parent
ap=argparse.ArgumentParser()
ap.add_argument("--out",default="art-reviews/atlas-native-game")
args=ap.parse_args()
out=root/args.out
out.mkdir(parents=True,exist_ok=True)
sources={
 "south":"art-reviews/v267-original-source/south-unified-native-border-unapproved.webp",
 "countryside-03":"terrain-grid/v267-countryside-original/forest-meadow-03-master.webp"
}
images={name:Image.open(root/path).convert("RGB") for name,path in sources.items()}
assert all(im.size==(1536,1024) for im in images.values())
# Last 768px of SOUTH and first 768px of C03, preserving original pixels and scale.
sheet=Image.new("RGB",(1536,1024))
sheet.paste(images["south"].crop((768,0,1536,1024)),(0,0))
sheet.paste(images["countryside-03"].crop((0,0,768,1024)),(768,0))
draw=ImageDraw.Draw(sheet)
# Source-aligned, UNVERIFIED scout coordinates; the dotted path is a diagnostic only.
route=[(2806-1536-768,1629-1024),(768,1629-1024),(768+768,1536-1024)]
for a,b in zip(route,route[1:]):
 dx,dy=b[0]-a[0],b[1]-a[1]
 steps=max(1,int((dx*dx+dy*dy)**.5/20))
 for j in range(steps):
  if j%2:continue
  t0=j/steps;t1=min(1,(j+1)/steps)
  draw.line([(a[0]+dx*t0,a[1]+dy*t0),(a[0]+dx*t1,a[1]+dy*t1)],fill=(255,204,38),width=4)
draw.line([(768,0),(768,1024)],fill=(255,72,62),width=3)
for x,y in route:
 draw.ellipse((x-8,y-8,x+8,y+8),fill=(255,208,45),outline=(0,0,0),width=2)
draw.rectangle((8,8,740,80),fill=(15,27,22))
draw.text((20,18),"SOUTH: APPROVED ART, EASTERN ROAD/RIVER APPROACH",fill=(255,238,188))
draw.text((20,45),"SOURCE PIXELS UNCHANGED; YELLOW = UNVERIFIED SCOUT",fill=(255,238,188))
draw.rectangle((780,8,1518,80),fill=(15,27,22))
draw.text((794,18),"C03: ROAD-FREE CANDIDATE; ROCK/FOREST AT SEAM",fill=(255,238,188))
draw.text((794,45),"NO VERIFIED SURFACE MASK OR PHYSICAL PASS",fill=(255,238,188))
output=out/"south-c03-actual-source-seam-BLOCKED.png"
sheet.save(output)
record={
 "kind":"source-pixel visual comparison, not a browser screenshot",
 "sourcePaths":sources,
 "sha256":{k:hashlib.sha256((root/p).read_bytes()).hexdigest() for k,p in sources.items()},
 "worldWaypoints":[[2806,1629],[3072,1629],[3840,1536]],
 "roadConnectionVerified":False,"surfaceMasksVerified":False,"movementEnabled":False,
 "note":"The yellow overlay is an unverified proposed route. This contact sheet does not establish passability."
}
(out/"south-c03-seam-evidence.json").write_text(json.dumps(record,indent=2)+"\n")
print(json.dumps({"image":str(output.relative_to(root)),"movementEnabled":False,"surfaceMasksVerified":False}))

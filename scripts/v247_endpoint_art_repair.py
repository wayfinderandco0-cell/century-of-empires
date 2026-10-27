#!/usr/bin/env python3
"""V247 isolated fictional terrain-art endpoint experiment, NOT approved.

Only retouches manually traced visible road sections OUTSIDE the surveyed
subset; original road pixels inside the subset are preserved. Retouched
pixels are NOT original source photography or evidence of historical roads.
"""
import argparse
import hashlib
import json
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageDraw

SIZE=(1536,1024)

def road_mask(size,points,radius=35):
    if size!=SIZE:
        raise ValueError("source must be 1536x1024")
    if not isinstance(points,list) or len(points)<2:
        raise ValueError("a separately annotated visible road is required")
    arr=np.asarray(points,dtype=float)
    if arr.shape[1:]!=(2,) or not np.isfinite(arr).all() or (arr<0).any() or (arr[:,0]>size[0]).any() or (arr[:,1]>size[1]).any():
        raise ValueError("bad source road annotation")
    if radius<8 or radius>36:
        raise ValueError("unsupported road mask width")
    mask=Image.new("L",size,0)
    d=ImageDraw.Draw(mask)
    d.line([tuple(map(float,p)) for p in points],fill=255,width=2*radius,joint="curve")
    for x,y in points:
        d.ellipse((x-radius,y-radius,x+radius,y+radius),fill=255)
    return np.array(mask)

def prepare(image_path,manifest,output):
    image_path=Path(image_path)
    raw=image_path.read_bytes()
    sha=hashlib.sha256(raw).hexdigest()
    if sha!=manifest.get("originalSha256"):
        raise ValueError("original image SHA256 mismatch")
    if manifest.get("sourceKind")!="fictional-generated-art-study":
        raise ValueError("do not silently treat licensed photography as generated artwork")
    if manifest.get("annotationMethod")!="manual-original-pixel-visible-road-trace":
        raise ValueError("independent original-pixel annotation is required")
    full=manifest.get("fullVisibleRoadPoints")
    first,last=manifest.get("playableStartIndex"),manifest.get("playableEndIndex")
    if not isinstance(first,int) or not isinstance(last,int) or not isinstance(full,list) or not (0<=first<last<len(full)):
        raise ValueError("invalid surveyed road subset")
    source=Image.open(image_path).convert("RGB")
    if source.size!=SIZE:
        raise ValueError("invalid original size")
    erase=np.zeros((SIZE[1],SIZE[0]),dtype=np.uint8)
    if first:
        erase=cv2.bitwise_or(erase,road_mask(SIZE,full[:first+1],radius=35))
    if last<len(full)-1:
        erase=cv2.bitwise_or(erase,road_mask(SIZE,full[last:],radius=35))
    keep=cv2.dilate(road_mask(SIZE,full[first:last+1],radius=8),np.ones((3,3),np.uint8))
    erase[keep!=0]=0
    if not erase.any():
        raise ValueError("no unsupported road section to repair")
    src=np.array(source)
    base=cv2.inpaint(src,erase,5,cv2.INPAINT_TELEA).astype(np.float32)
    yy,xx=np.indices((SIZE[1],SIZE[0]),dtype=np.float32)
    donor_y=np.clip(yy+62.0,0,SIZE[1]-1)
    donor=cv2.remap(src,xx,donor_y,cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT).astype(np.float32)
    high=donor-cv2.GaussianBlur(donor,(0,0),7.0)
    repaired=np.clip(base+0.92*high,0,255).astype(np.uint8)
    repaired[erase==0]=src[erase==0]
    output=Path(output)
    output.mkdir(parents=True,exist_ok=True)
    dest=output/"endpoint-repaired-ART-STUDY.png"
    Image.fromarray(repaired).save(dest)
    Image.fromarray(erase).save(output/"erased-road-mask.png")
    diag=Image.fromarray(repaired).convert("RGBA")
    over=Image.new("RGBA",SIZE,(0,0,0,0))
    d=ImageDraw.Draw(over)
    d.line([tuple(p) for p in full[first:last+1]],fill=(245,35,40,180),width=3)
    for p in (full[first],full[last]):
        x,y=p
        d.ellipse((x-9,y-9,x+9,y+9),outline=(255,245,30,255),width=3)
    Image.alpha_composite(diag,over).convert("RGB").save(output/"survey-endpoint-review.jpg",quality=93)
    difference=np.any(src!=repaired,axis=2)
    report={
      "kind":"ISOLATED_FICTIONAL_EDITED_ART_NOT_SOURCE_PHOTOGRAPHY",
      "originalSha256":sha,"editedSha256":hashlib.sha256(dest.read_bytes()).hexdigest(),
      "sourceAttribution":manifest.get("sourceAttribution"),
      "sourceKind":"fictional-generated-art-study",
      "manuallyTracedVisibleRoad":full,
      "playableStartIndex":first,"playableEndIndex":last,
      "erasedPixels":int(np.count_nonzero(erase)),
      "changedOutsideErase":int(np.count_nonzero(difference & (erase==0))),
      "retouchingIsOriginalSource":False,
      "sourceRegisteredToV123":False,
      "historicalRoadsVerified":False,
      "bridgeBanksVerified":False,
      "sourceLicenseVerified":False,
      "v203VisualPass":False,
      "fourBrowserPass":False,
      "humanVisualApproval":False,
      "productionApproved":False,
      "promotionEligible":False
    }
    (output/"report.json").write_text(json.dumps(report,indent=2)+"\n")
    return report

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--image",type=Path,required=True)
    p.add_argument("--manifest",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    print(json.dumps(prepare(a.image,json.loads(a.manifest.read_text()),a.out),indent=2))

if __name__=="__main__":
    main()

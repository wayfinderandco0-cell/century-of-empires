#!/usr/bin/env python3
"""Visual audit of the first new V267 east-ridge seam; never modifies art.

The canonical Matrei display crop is mirrored from atlas-integrated.js.
This is a DIAGNOSTIC, not evidence of a continuous landform or road.
"""
import json
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / "terrain-grid/v267-original-art-batch-01"
MATREI = ROOT / "terrain-grid/art/matrei-v121-original.webp"
RIDGE = FOLDER / "matrei-east-ridge.webp"
W, H = 1536, 1024
Y0, Y1 = 256, 768
STRIP = 256

def smooth(v):
    v = max(0.0, min(1.0, v))
    return v*v*(3-2*v)

def matrei_source_xy(x, y):
    t = smooth((y-845)/179)
    sy0 = 10+y*(953/H)-26*t
    sl = (385-(sy0-10)*(295/276) if sy0 < 286
          else 90+(sy0-674)*(295/289) if sy0 > 674 else 90)
    tl = 256-y if y < 256 else y-768 if y > 768 else 0
    tr = W-tl
    b = smooth((y-700)/324)
    x_south = math.exp(-0.5*((x-466)/105)**2)
    x_west = math.exp(-0.5*((x-240)/400)**2)
    wy = 26*math.exp(-0.5*((y-505)/110)**2)
    sx = sl+(x-tl)*(W-2*sl)/(tr-tl)-55*b*x_south
    sy = sy0+wy*x_west
    return (max(0,min(W-1,int(round(sx)))),
            max(0,min(H-1,int(round(sy)))))

def main():
    with Image.open(MATREI) as m, Image.open(RIDGE) as r:
        matrei = m.convert("RGB")
        ridge = r.convert("RGB")
    assert matrei.size == ridge.size == (W,H)
    mp, rp = matrei.load(), ridge.load()
    left = Image.new("RGB", (STRIP,Y1-Y0))
    right = ridge.crop((0,Y0,STRIP,Y1))
    lp = left.load()
    differences = []
    for y in range(Y0,Y1):
        for x in range(W-STRIP,W):
            lp[x-(W-STRIP),y-Y0] = mp[matrei_source_xy(x,y)]
        a = lp[STRIP-1,y-Y0]
        b = rp[0,y]
        differences.append(sum(abs(a[c]-b[c]) for c in range(3))/3)
    # Two intact, side-by-side border strips. No warped trees, false roads,
    # seam smoothing, or modification of approved source imagery.
    comparison = Image.new("RGB", (1024,1080), "#182820")
    comparison.paste(left.resize((512,1024),Image.Resampling.NEAREST),(0,48))
    comparison.paste(right.resize((512,1024),Image.Resampling.NEAREST),(512,48))
    draw = ImageDraw.Draw(comparison)
    draw.rectangle((0,0,1024,47),fill="#13231c")
    draw.text((16,15),"MATREI / registered east border",fill="#f6e7be")
    draw.text((530,15),"NEW RIDGE / unapproved west border",fill="#f6e7be")
    draw.line((511,48,511,1072),fill="#ffd277",width=3)
    output = FOLDER/"matrei-east-seam-audit.webp"
    comparison.save(output,"WEBP",quality=87,method=6)
    metrics = {
      "schema":"coe-v267-seam-audit/v1",
      "cells":["matrei","matrei-east-ridge"],
      "border":"matrei.east <-> matrei-east-ridge.west",
      "worldX":3072,
      "worldYRange":[Y0,Y1],
      "registeredMatreiSource":"terrain-grid/art/matrei-v121-original.webp",
      "ridgeSource":"terrain-grid/v267-original-art-batch-01/matrei-east-ridge.webp",
      "meanBorderRgbAbsDifference":round(sum(differences)/len(differences),2),
      "maxBorderRgbAbsDifference":round(max(differences),2),
      "borderSamples":len(differences),
      "geometricContinuityVerified":False,
      "roadConnectionVerified":False,
      "historicalVerification":False,
      "userApproved":False,
      "finished":False,
      "note":"A pixel difference is a visual diagnostic, not a terrain-seam pass; original images unchanged."
    }
    (FOLDER/"matrei-east-seam-audit.json").write_text(json.dumps(metrics,indent=2)+"\n")
    assert len(differences)==512 and output.stat().st_size>20000
    print(json.dumps(metrics))
if __name__ == "__main__":
    main()

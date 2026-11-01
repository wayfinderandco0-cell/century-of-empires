#!/usr/bin/env python3
"""Extract nine separate reference-only octagon assets from a 1536x1024
user-supplied 12-cell screenshot. NEVER promotes these crops as V267 originals.
Usage: python terrain-grid/tools/extract-12-cell-references.py screenshot.jpg out/
Requires Pillow and OpenCV (cv2). Does not touch native art, saves, or routes.
"""
import sys, json, hashlib
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

POLYGONS = {
"NW-01":[[217,62],[355,62],[452,149],[452,269],[357,339],[100,339],[100,150]],
"NORTH-01":[[551,62],[688,62],[785,149],[785,269],[688,339],[521,339],[451,269],[451,149]],
"NE-01":[[884,62],[1021,62],[1117,149],[1117,269],[1021,339],[853,339],[785,269],[785,149]],
"NE-02":[[1217,62],[1355,62],[1454,149],[1454,269],[1355,339],[1185,339],[1117,269],[1117,149]],
"EAST-01":[[883,341],[1028,341],[1131,422],[1131,560],[1028,643],[886,643],[790,560],[790,422]],
"EAST-02":[[1228,344],[1364,344],[1514,421],[1514,558],[1364,643],[1230,643],[1132,558],[1132,421]],
"SW-01":[[128,649],[307,649],[397,731],[397,853],[307,936],[128,936],[23,853],[23,731]],
"SE-01":[[881,644],[1029,644],[1132,728],[1132,852],[1029,936],[881,936],[788,852],[788,728]],
"SE-02":[[1224,644],[1377,644],[1520,728],[1520,852],[1377,936],[1224,936],[1132,852],[1132,728]]
}
LABELS = {
"NW-01":[320,193,94,39],"NORTH-01":[624,193,146,39],
"NE-01":[954,193,98,39],"NE-02":[1293,193,98,39],
"EAST-01":[957,450,117,40],"EAST-02":[1335,450,117,40],
"SW-01":[232,801,98,42],"SE-01":[970,803,98,42],"SE-02":[1308,803,98,42]
}
def build(source_path, out_dir):
    source = Image.open(source_path).convert("RGB")
    if source.size != (1536,1024):
        raise ValueError("Expected exact 1536x1024 source screenshot; no silent rescaling")
    out = Path(out_dir)
    out.mkdir(parents=True,exist_ok=True)
    rgb = np.asarray(source)
    entries = []
    for tile, polygon in POLYGONS.items():
        x0 = min(p[0] for p in polygon)
        y0 = min(p[1] for p in polygon)
        x1 = max(p[0] for p in polygon)
        y1 = max(p[1] for p in polygon)
        x,y,w,h = LABELS[tile]
        mask = np.zeros(rgb.shape[:2],dtype=np.uint8)
        cv2.rectangle(mask,(x-w//2,y-h//2),(x+w//2,y+h//2),255,-1)
        clean = cv2.inpaint(rgb,mask,7,cv2.INPAINT_TELEA)
        crop = Image.fromarray(clean[y0:y1+1,x0:x1+1]).convert("RGBA")
        alpha = Image.new("L",crop.size,0)
        ImageDraw.Draw(alpha).polygon([(x-x0,y-y0) for x,y in polygon],fill=255)
        crop.putalpha(alpha.filter(ImageFilter.MinFilter(3)))
        target = out / (tile+".webp")
        crop.save(target,format="WEBP",quality=84,method=6)
        entries.append({
            "id":tile,"bbox":[x0,y0,crop.width,crop.height],
            "file":target.name,"sha256":hashlib.sha256(target.read_bytes()).hexdigest(),
            "artProvenance":"cropped and label-inpainted user screenshot",
            "originalV267Art":False,"seamVerified":False,"roadVerified":False,
            "mobileWebKitVerified":False,"historicallyVerified":False,
            "nativePlayable":False,"userApproved":False
        })
    assert len(entries)==9
    assert len({e["sha256"] for e in entries})==9
    (out/"manifest.json").write_text(json.dumps({
        "schema":"coe-atlas-screenshot-reference/v2",
        "approvedOriginalsProtected":["WEST","MATREI","SOUTH"],
        "screenshotPixels":[1536,1024],
        "worldCoordinates":"UNASSIGNED; do not infer V123 from screenshot",
        "warning":"These are reference crops, not newly approved original art or playable cells.",
        "cells":entries
    },indent=2)+"\n")
    print("Nine distinct reference images generated; zero new finished playable cells.")
if __name__=="__main__":
    if len(sys.argv)!=3:raise SystemExit("usage: script.py screenshot.jpg out_dir")
    build(sys.argv[1],sys.argv[2])

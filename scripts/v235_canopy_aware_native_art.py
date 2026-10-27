#!/usr/bin/env python3
"""V235: reject bright forest canopy falsely scored as roadbed in V234.

Source-native crop selection only. Historical roads, bridge banks, V209
registration, Matrei preservation and visual approval remain unverified.
"""
import argparse
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
import v232_route_ground_preflight as v232
import v234_native_corridor_crop as v234

FALSE_FLAGS = v232.FALSE_FLAGS

def canopy_aware_ground_mask(image):
    """Conservative OPEN pasture evidence, not certified semantic segmentation.

    V232 accepted HSV H<=95 and S>=28: bright conifer foliage passed as
    traversable grass. Exclude cool/low-saturation canopy, dark forest,
    grey rock and water. This intentionally may reject real brown paths.
    """
    rgb=np.asarray(image.convert("RGB"))
    hsv=cv2.cvtColor(rgb,cv2.COLOR_RGB2HSV)
    h,s,v=cv2.split(hsv)
    open_ground=((h>=18)&(h<=48)&(s>=90)&(v>=85)&(v<=240))
    excluded={
      "darkCanopy":((v<85)|((h>48)&(h<=100))).astype(np.uint8),
      "bareRock":((s<35)&(v>100)).astype(np.uint8),
    }
    return open_ground.astype(np.uint8),excluded

def evaluate(paths, output, manifest):
    if not manifest:
        raise ValueError("Source manifest required for provenance and SHA256")
    # V234's full-native crop ranking and V232's exact 25px V123
    # corridor inspection both must use the SAME corrected mask.
    # Assign in this isolated CLI process; never modify shared source.
    v232.ground_mask=canopy_aware_ground_mask
    v234.ground_mask=canopy_aware_ground_mask
    report=v234.evaluate_sources(paths,output,manifest)
    report["version"]=235
    report["method"]="unmodified native crop with canopy-aware open-ground mask"
    report["v234FalsePassCorrected"]=True
    report["maskLimits"]="Conservative color heuristic; necessary, never sufficient"
    for tile in ("west","south"):
        t=report["tiles"][tile]
        t["status"]=("NECESSARY_LANDCOVER_ONLY"
                     if t["status"]=="GROUND_PREFLIGHT_ONLY" else "REJECTED")
        t.update(FALSE_FLAGS)
    report["bothNecessaryLandcoverGatesPass"]=all(
        t["status"]=="NECESSARY_LANDCOVER_ONLY"
        for t in report["tiles"].values())
    report["bothNecessaryGroundGatesPass"]=report["bothNecessaryLandcoverGatesPass"]
    report.update(FALSE_FLAGS)
    (Path(output)/"v235-report.json").write_text(
        json.dumps(report,indent=2)+"\n")
    return report

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--west",type=Path,required=True)
    p.add_argument("--south",type=Path,required=True)
    p.add_argument("--manifest",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    r=evaluate({"west":a.west,"south":a.south},a.output,
               json.loads(a.manifest.read_text()))
    for tile in ("west","south"):
        t=r["tiles"][tile]
        print(tile,t["status"],t["nativeCrop"],
              t["topCandidates"][0]["ground"])
    print("Both necessary landcover gates:",r["bothNecessaryLandcoverGatesPass"])
    print("Production approved:",r["productionApproved"])

if __name__=="__main__":
    main()

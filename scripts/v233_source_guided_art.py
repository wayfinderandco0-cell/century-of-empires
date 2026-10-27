#!/usr/bin/env python3
"""V233 whole-scene source-guide art study. NOT geography or approved game art.
No painted ground strips, cloned pixels, or changes to the V123 road graph.
"""
import argparse, hashlib, json
from pathlib import Path
import cv2
import numpy as np
from PIL import Image
from v232_route_ground_preflight import source_roads, inspect, SIZE, ATLAS

PINNED_ATLAS_BLOB = "09f04b4062e24fbacbb645307462cdddce2b2aa3"
FALSE_FLAGS = {k: False for k in (
    "sourceRegisteredToV123", "historicalRoadsVerified", "bridgeBanksVerified",
    "periodSafe", "humanVisualApproval", "physicalIPhoneApproved",
    "productionApproved")}

def verified_roads():
    data = ATLAS.read_bytes()
    sha = hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()
    if sha != PINNED_ATLAS_BLOB:
        raise ValueError("STOP: immutable V123 source blob changed")
    return source_roads()

def warp(image, points, guide, radius=175):
    """Continuous full-image inverse mapping; rejects destructive distortion."""
    if image.size != SIZE:
        raise ValueError("Expected original 1536x1024 source; no upsampling")
    pts = np.asarray(points, np.float32)
    guides = np.asarray(guide, np.float32)
    if pts.shape != guides.shape or pts.ndim != 2 or pts.shape[1] != 2:
        raise ValueError("Guide must contain one source point per immutable V123 point")
    if not np.isfinite(guides).all() or (guides < 0).any() or (guides > np.asarray(SIZE)).any():
        raise ValueError("Guide contains invalid source coordinates")
    shifts = guides-pts
    maximum = float(np.linalg.norm(shifts, axis=1).max())
    if maximum > 80:
        raise ValueError(f"REJECTED: guide needs {maximum:.1f}px deformation (>80px)")
    yy, xx = np.indices((SIZE[1], SIZE[0]), dtype=np.float32)
    weights = np.zeros_like(xx)
    dx = np.zeros_like(xx)
    dy = np.zeros_like(xx)
    for (x,y),(sx,sy) in zip(pts,shifts):
        w = np.exp(-((xx-x)**2+(yy-y)**2)/(2*radius*radius)).astype(np.float32)
        weights += w
        dx += w*sx
        dy += w*sy
    influence = 1-np.exp(-weights)
    dx = dx/np.maximum(weights,1e-9)*influence
    dy = dy/np.maximum(weights,1e-9)*influence
    # Identity at all scene edges: no reflected/repeated source strips.
    edge = np.minimum.reduce((xx/80,(SIZE[0]-1-xx)/80,
                              yy/80,(SIZE[1]-1-yy)/80))
    edge = np.clip(edge,0,1)
    mx = xx+dx*edge
    my = yy+dy*edge
    outside = float(((mx<0)|(mx>SIZE[0]-1)|(my<0)|(my>SIZE[1]-1)).mean())
    det = np.gradient(mx,axis=1)*np.gradient(my,axis=0) - \
          np.gradient(mx,axis=0)*np.gradient(my,axis=1)
    folds = float((det[2:-2,2:-2]<=0).mean())
    if outside>0 or folds>0:
        raise ValueError(f"REJECTED: off-canvas={outside:.6f}, foldovers={folds:.6f}")
    rgb = np.asarray(image.convert("RGB"))
    output = cv2.remap(rgb,mx,my,cv2.INTER_LINEAR,
                       borderMode=cv2.BORDER_CONSTANT,borderValue=(255,0,255))
    return Image.fromarray(output), {
        "maximumGuideShiftPx":round(maximum,2),
        "invalidSourceFraction":outside,"foldoverFraction":folds,
        "fullSceneOriginalPixelsOnly":True}

def evaluate(paths, manifest, output):
    roads = verified_roads()
    output.mkdir(parents=True,exist_ok=True)
    report = {"version":233,"bothNecessaryArtGatesPass":False,
              "tiles":{},**FALSE_FLAGS}
    for tile in ("west","south"):
        info = manifest[tile]
        raw = Path(paths[tile]).read_bytes()
        sha = hashlib.sha256(raw).hexdigest()
        if sha != info["sha256"]:
            raise ValueError("STOP: "+tile+" source SHA-256 mismatch")
        try:
            result,metrics = warp(Image.open(paths[tile]),roads[tile],info["guide"])
            ground,_ = inspect(result,roads[tile],tile)
            if not ground["necessaryRoadGroundGate"]:
                raise ValueError("REJECTED: source terrain cannot ground V123 cartway")
            filename = tile+"-v233-whole-scene-study.webp"
            result.save(output/filename,"WEBP",quality=92)
            report["tiles"][tile] = {"status":"ART_STUDY_ONLY",
                "sourceSha256":sha,"file":filename,**metrics,"ground":ground,**FALSE_FLAGS}
        except ValueError as e:
            report["tiles"][tile] = {"status":"REJECTED",
                "sourceSha256":sha,"reason":str(e),**FALSE_FLAGS}
    report["bothNecessaryArtGatesPass"] = all(
        x["status"]=="ART_STUDY_ONLY" for x in report["tiles"].values())
    (output/"v233-report.json").write_text(json.dumps(report,indent=2)+"\n")
    return report

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--west",type=Path,required=True)
    p.add_argument("--south",type=Path,required=True)
    p.add_argument("--manifest",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--enforce",action="store_true")
    a=p.parse_args()
    r=evaluate({"west":a.west,"south":a.south},
               json.loads(a.manifest.read_text()),a.output)
    print(json.dumps(r,indent=2))
    if a.enforce and not r["bothNecessaryArtGatesPass"]:
        raise SystemExit("ART RED: source scenes cannot support V123 roads")
if __name__=="__main__":main()

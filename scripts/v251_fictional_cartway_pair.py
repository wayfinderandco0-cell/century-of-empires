#!/usr/bin/env python3
"""V251: whole-scene fictional road/ground relocation, ART/PRODUCTION RED.

Moves EXISTING source road pixels and their surrounding landscape together.
No cartway is painted. The manually sighted source traces are NOT independently
verified, the images are fictional and cannot establish historic geography.
This is an isolated visual experiment, never a production import.
"""
import argparse
import hashlib
import json
from pathlib import Path

import cv2
import numpy as np
from scipy.spatial import cKDTree

PINNED_V123_BLOB = "09f04b4062e24fbacbb645307462cdddce2b2aa3"
WEST = [[1536,478],[1450,478],[1320,480],[1210,490],[1085,507],
        [980,515],[890,535],[784,551],[680,560],[570,540],[470,520],
        [370,522],[275,550]]
SOUTH = [[466,0],[466,74],[470,160],[488,235],[540,310],[620,350],
         [700,400],[805,442],[930,510],[1050,550],[1140,585],[1270,605]]
# Visual estimates from two original fictional image studies; UNVERIFIED.
SOURCE = {
    "west": [[330,428],[415,428],[515,420],[635,410],[750,401],
             [890,385],[1030,376],[1180,363],[1330,353],[1450,343],[1536,333]],
    "south": [[513,0],[509,72],[508,155],[516,230],[552,300],
              [615,354],[720,406],[825,455],[935,496],[1045,529],[1140,550]],
}
TARGET = {"west": list(reversed(WEST)), "south": SOUTH}


def git_blob_sha(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def require_immutable_atlas(path):
    raw = Path(path).read_bytes()
    if git_blob_sha(raw) != PINNED_V123_BLOB:
        raise ValueError("V123 atlas hash drift: stop")
    import re
    for name, points in (("westRoad", WEST), ("southRoad", SOUTH)):
        match = re.search(r"const\s+" + name + r"\s*=\s*(\[\[[^;]+?\]\])\s*;", raw.decode())
        if not match or json.loads(match.group(1)) != points:
            raise ValueError("V123 coordinates drift: " + name)


def arc_sample(points, n=1024):
    p = np.asarray(points, dtype=np.float64)
    if p.ndim != 2 or p.shape[1] != 2 or len(p) < 2 or not np.isfinite(p).all():
        raise ValueError("invalid road points")
    lengths = np.linalg.norm(np.diff(p, axis=0), axis=1)
    if np.min(lengths) < 1:
        raise ValueError("degenerate road")
    arclen = np.r_[0, np.cumsum(lengths)]
    t = np.linspace(0, arclen[-1], n)
    return np.stack([np.interp(t, arclen, p[:,k]) for k in range(2)], axis=-1), float(arclen[-1])


def warp(image, source, target, sigma=230, max_disp=165, top_fade=False):
    if image.shape[:2] != (1024,1536):
        raise ValueError("native source must be 1536x1024")
    a, la = arc_sample(source)
    b, lb = arc_sample(target)
    displacement = a - b
    maximum = float(np.max(np.linalg.norm(displacement, axis=1)))
    if maximum > max_disp:
        raise ValueError(f"max displacement {maximum:.1f} > {max_disp}")
    h, w = image.shape[:2]
    yy, xx = np.indices((h,w), dtype=np.float32)
    pixels = np.stack([xx.ravel(), yy.ravel()], axis=1)
    dist, idx = cKDTree(b).query(pixels, k=1, workers=-1)
    weights = np.exp(-0.5*(dist/sigma)**2).astype(np.float32)
    dx = cv2.GaussianBlur((displacement[idx,0].astype(np.float32)*weights).reshape(h,w),(0,0),18)
    dy = cv2.GaussianBlur((displacement[idx,1].astype(np.float32)*weights).reshape(h,w),(0,0),18)
    if top_fade:
        fade = np.clip(yy/160.0,0.0,1.0)
        dx *= fade
        dy *= fade
    mapx, mapy = xx+dx, yy+dy
    observed = (mapx>=0)&(mapx<=w-1)&(mapy>=0)&(mapy<=h-1)
    out = cv2.remap(image,mapx,mapy,interpolation=cv2.INTER_CUBIC,borderMode=cv2.BORDER_REFLECT_101)
    step = 12
    gx = np.gradient(mapx[::step,::step])
    gy = np.gradient(mapy[::step,::step])
    jac = (gx[1]*gy[0]-gx[0]*gy[1])/(step*step)
    coverage = float(np.mean(observed))
    stretch = abs(lb/la-1)
    return out, {
        "sourceRoadLengthPx": round(la,1),
        "targetRoadLengthPx": round(lb,1),
        "maxSourceToTargetDisplacementPx": round(maximum,2),
        "minSampledJacobian": round(float(jac.min()),3),
        "foldedSampleFraction": round(float(np.mean(jac<=0)),6),
        "observedPixelCoverage": round(coverage,6),
        "arcLengthStretchFraction": round(stretch,6),
        "v245StrictGeometryPass": bool(maximum<=155 and float(jac.min())>=0.24
                                        and coverage>=0.997 and stretch<=0.22),
        "originalPixelAnnotationIndependentlyVerified": False,
        "sourceRegisteredToV123": False,
        "bridgeBanksVerified": False,
        "humanArtApproved": False,
        "productionApproved": False,
    }


def overlay(image, points):
    out = image.copy()
    p = np.asarray(points, dtype=np.int32)
    cv2.polylines(out,[p],False,(30,40,245),3,cv2.LINE_AA)
    for xy in (p[0],p[-1]):
        cv2.circle(out,tuple(xy),9,(20,230,245),2,cv2.LINE_AA)
    return out


def run(sources, output, atlas):
    require_immutable_atlas(atlas)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    report = {
        "version":251,"kind":"FICTIONAL_ORIGINAL_ART_STUDY_UNAPPROVED",
        "immutableV123Blob":PINNED_V123_BLOB,
        "sourceAttribution":"Original fictional AI-generated studies, not geographic evidence",
        "historicalRoadsVerified":False,"sourceRegisteredToV123":False,
        "humanArtApproved":False,"productionApproved":False,"tiles":{},
    }
    for tile in ("west","south"):
        raw = Path(sources[tile]).read_bytes()
        im = cv2.imread(str(sources[tile]),cv2.IMREAD_COLOR)
        if im is None:
            raise ValueError("unreadable image: "+tile)
        candidate, qa = warp(im,SOURCE[tile],TARGET[tile],top_fade=(tile=="west"))
        cv2.imwrite(str(output/f"{tile}-v251-UNAPPROVED.jpg"),candidate,
                    [cv2.IMWRITE_JPEG_QUALITY,93])
        cv2.imwrite(str(output/f"{tile}-route-overlay-UNAPPROVED.jpg"),
                    overlay(candidate,TARGET[tile]),[cv2.IMWRITE_JPEG_QUALITY,92])
        qa["sourceSha256"] = hashlib.sha256(raw).hexdigest()
        qa["sourceRoadTrace"] = SOURCE[tile]
        qa["status"] = ("GEOMETRY_FAIL_AND_UNAPPROVED" if not qa["v245StrictGeometryPass"]
                        else "NECESSARY_GEOMETRY_ONLY_UNAPPROVED")
        report["tiles"][tile] = qa
    (output/"report.json").write_text(json.dumps(report,indent=2)+"\n")
    return report


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--west",required=True)
    ap.add_argument("--south",required=True)
    ap.add_argument("--out",required=True)
    ap.add_argument("--atlas",default="terrain-grid/v123-atlas.js")
    args = ap.parse_args()
    print(json.dumps(run({"west":args.west,"south":args.south},args.out,args.atlas),indent=2))

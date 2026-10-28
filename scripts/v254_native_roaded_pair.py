#!/usr/bin/env python3
"""V254 isolated original fictional WEST/SOUTH physical-cartway raster candidate.

Never changes V123 roads, Matrei, sprites, saves or production. The source road
traces below are visually estimated, NOT independent geographic registration.
Original images are supplied separately, never mistaken for historical evidence.
"""
import argparse
import hashlib
import json
from pathlib import Path

import cv2
import numpy as np
from v251_fictional_cartway_pair import require_immutable_atlas, warp

PINNED = {
    "west": "7326e88c778ed4a0018c241156e701690e95deb1feeb8fa13a298c0f0c74505e",
    "south": "034246c5d9471cd6d87673daa48fb1a014dab38d414626677f6148ce8c7d08f3",
}
# Native source-image pixel observations, NOT independently reviewed/verified.
SOURCE = {
    "west": [[275,427],[370,420],[470,422],[570,419],[680,413],[784,402],
             [890,392],[980,385],[1085,375],[1210,370],[1320,360],[1450,350],[1536,341]],
    "south": [[447,0],[451,74],[471,160],[512,235],[570,310],[639,365],
              [710,425],[770,480],[825,518],[910,558],[1010,588],[1110,611],[1244,625]],
}
# Exact immutable V123 centerlines. WEST is reversed to match SOURCE direction.
TARGET = {
    "west": [[275,550],[370,522],[470,520],[570,540],[680,560],[784,551],
             [890,535],[980,515],[1085,507],[1210,490],[1320,480],[1450,478],[1536,478]],
    "south": [[466,0],[466,74],[470,160],[488,235],[540,310],[620,350],
              [700,400],[805,442],[930,510],[1050,550],[1140,585],[1270,605]],
}
def load_original(path, tile):
    raw = Path(path).read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    if sha != PINNED[tile]:
        raise ValueError(tile + ": original image SHA256 mismatch")
    image = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if image is None or image.shape[:2] != (1024,1536):
        raise ValueError(tile + ": expected original native 1536x1024 image")
    return image, sha

def render(west, south, output, atlas):
    require_immutable_atlas(atlas)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    report = {"version":254, "status":"ISOLATED_FICTIONAL_ART_NOT_APPROVED",
              "sourceRights":"Original AI-generated fictional project studies; no third-party photograph",
              "sourceToGameNaturalTiepointsVerified":False,
              "historical1780RoadsVerified":False, "bridgeBanksVerified":False,
              "strictV203Passed":False, "fourBrowserNewArtPassed":False,
              "humanVisualApproval":False, "productionApproved":False, "tiles":{}}
    for tile, path in (("west",west),("south",south)):
        image, sha = load_original(path,tile)
        candidate, metrics = warp(image,SOURCE[tile],TARGET[tile],
                                  sigma=160 if tile=="west" else 210,
                                  max_disp=155,top_fade=False)
        candidate_file = output / (tile+"-native-cartway-UNAPPROVED.webp")
        cv2.imwrite(str(candidate_file),candidate,[cv2.IMWRITE_WEBP_QUALITY,88])
        overlay=candidate.copy()
        cv2.polylines(overlay,[np.asarray(TARGET[tile],np.int32)],False,
                      (25,25,250),3,cv2.LINE_AA)
        cv2.imwrite(str(output/(tile+"-route-overlay-UNAPPROVED.jpg")),overlay,
                    [cv2.IMWRITE_JPEG_QUALITY,92])
        report["tiles"][tile] = {
            "originalSha256":sha, "sourceTrace":SOURCE[tile],
            "sourceTraceIndependentlyVerified":False,
            "roadEndpointBeyondGraph":"NOT_SEEN_IN_MANUAL_REVIEW_NOT_INDEPENDENTLY_VERIFIED",
            "rasterOutput":candidate_file.name, **metrics}
    (output/"report.json").write_text(json.dumps(report,indent=2)+"\n")
    return report

if __name__ == "__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--west",required=True)
    p.add_argument("--south",required=True)
    p.add_argument("--out",required=True)
    p.add_argument("--atlas",default="terrain-grid/v123-atlas.js")
    a=p.parse_args()
    print(json.dumps(render(a.west,a.south,a.out,a.atlas),indent=2))

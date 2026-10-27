#!/usr/bin/env python3
"""V229 isolated source-attributed Austrian art experiment; NOT historical cartography.
Generates two complete independent native-size natural-cover photographs with
conservative 28px V123-aligned clearance. NOT a verified cartway, bridge or terrain.
The images are intentionally subject to unchanged V203 and human review gates.
"""
import argparse, hashlib, io, json
from pathlib import Path
import cv2
import numpy as np
import requests
from PIL import Image

SIZE = (1536, 1024)
SOURCES = {
    "west": {
        "title": "Guggenberg von Norden a.JPG",
        "url": "https://upload.wikimedia.org/wikipedia/commons/f/f5/Guggenberg_von_Norden_a.JPG",
        "sourceSha256": "273218ffd17e79fc8fb2c1e6db609b53045be955ac7284d60945a588ff383e55",
        "crop": [3600, 1950, 5136, 2974],
        "author": "Michael Kranewitter",
    },
    "south": {
        "title": "Bichl von Nordwesten.jpg",
        "url": "https://upload.wikimedia.org/wikipedia/commons/c/c9/Bichl_von_Nordwesten.jpg",
        "sourceSha256": "afb9f2c80f8e436ad20a3bc085e4cb9badfaee5075ea80c6e39b14746e67fc7d",
        "crop": [400, 2400, 1936, 3424],
        "author": "Michael Kranewitter",
    },
}
# Original V123, not new or edited navigation geometry.
ROADS = {
    "west": [[1536,478],[1450,478],[1320,480],[1210,490],[1085,507],[980,515],
             [890,535],[784,551],[680,560],[570,540],[470,520],[370,522],[275,550]],
    "south": [[466,0],[466,74],[470,160],[488,235],[540,310],[620,350],
              [700,400],[805,442],[930,510],[1050,550],[1140,585],[1270,605]],
}
LOCKED_FNV = {"west": "a716b11c", "south": "c0491522"}
FALSE_FLAGS = dict(sourceRegisteredToV123=False, historicalRoadsVerified=False,
                   bridgeBanksVerified=False, onwardRoadVerified=False,
                   roadClearanceVerified=False, periodSafe=False,
                   gameArtApproved=False, humanVisualApproval=False,
                   physicalIPhoneApproved=False, productionApproved=False)

def fnv_points(points):
    h = 2166136261
    for char in json.dumps(points, separators=(",", ":")):
        h = ((h ^ ord(char)) * 16777619) & 0xffffffff
    return f"{h:x}"

def assert_immutable_roads():
    for cell, points in ROADS.items():
        assert fnv_points(points) == LOCKED_FNV[cell], f"V123 road drift: {cell}"

def make_cell(cell, info, output):
    response = requests.get(info["url"], timeout=90,
                            headers={"User-Agent": "CenturyOfEmpiresSourceAudit/0.1"})
    response.raise_for_status()
    raw = response.content
    sha = hashlib.sha256(raw).hexdigest()
    if sha != info["sourceSha256"]:
        raise ValueError(f"STOP: upstream source bytes changed for {cell}: {sha}")
    original = Image.open(io.BytesIO(raw)).convert("RGB")
    crop = original.crop(tuple(info["crop"]))
    if crop.size != SIZE:
        raise ValueError(f"STOP: {cell} crop not native 1536x1024")
    rgb = np.array(crop)
    # CLAHE operates on source luminance; no random texture, synthetic trees,
    # Matrei source-pixel reuse, houses, new roads or new river crossings.
    lab = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB)
    l, a, b = cv2.split(lab)
    l = cv2.createCLAHE(clipLimit=1.6, tileGridSize=(8, 8)).apply(l)
    rgb = cv2.cvtColor(cv2.merge((l, a, b)), cv2.COLOR_LAB2RGB)
    mask = np.zeros((SIZE[1], SIZE[0]), dtype=np.uint8)
    points = np.array(ROADS[cell], dtype=np.int32).reshape((-1, 1, 2))
    cv2.polylines(mask, [points], False, 255, 28, lineType=cv2.LINE_AA)
    # Illustrative removal of nearby source texture UNDER the unchanged road
    # renderer; cannot be called surveyed road clearance or a verified bank.
    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    prepared = cv2.cvtColor(cv2.inpaint(bgr, mask, 7, cv2.INPAINT_TELEA),
                            cv2.COLOR_BGR2RGB)
    name = f"{cell}-austrian-natural-cover-v229.webp"
    target = output / name
    Image.fromarray(prepared).save(target, "WEBP", quality=86, method=6)
    data = target.read_bytes()
    return dict(info, file=name, nativePixels=list(SIZE),
                sourceImagePixels=list(original.size), outputSha256=hashlib.sha256(data).hexdigest(),
                outputBytes=len(data), license="CC BY-SA 4.0",
                licenseUrl="https://creativecommons.org/licenses/by-sa/4.0/",
                sourcePage=f"https://commons.wikimedia.org/wiki/File:{info['title'].replace(' ', '_')}",
                modifications="Native-pixel crop, local luminance contrast, 28px graph-aligned illustrative inpainting",
                **FALSE_FLAGS)

def build(output):
    assert_immutable_roads()
    output.mkdir(parents=True, exist_ok=True)
    sources = {cell: make_cell(cell, info, output) for cell, info in SOURCES.items()}
    assert sources["west"]["sourceSha256"] != sources["south"]["sourceSha256"]
    manifest = dict(version=229, kind="UNAPPROVED_AUSTRIAN_SOURCE_ART_STUDY",
                    sourceRegion="Matrei in Osttirol, Austria",
                    license="CC BY-SA 4.0", notHistorical1780Geography=True,
                    cartwaysAndBridgeBanksNotSurveyed=True, sources=sources, **FALSE_FLAGS)
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({"assets": {c: {"sha256": s["outputSha256"],
                                     "bytes": s["outputBytes"]} for c, s in sources.items()},
                      "approval": False}, indent=2))
    return manifest

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("terrain-v229/assets"))
    args = parser.parse_args()
    build(args.output)

#!/usr/bin/env python3
"""V232: inspect UNALTERED CC0 source crops before V231 road-strip inpainting.

The V231 generated images already contain an artificial meadow strip under
the cartway. Inspecting only those outputs could falsely certify a rock face
as drivable. Preserve the exact native source pixels and their attribution.
"""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image
from build_v231_cc0_oblique_art import SOURCES, download, LICENSE, LICENSE_URL

def extract(output):
    output.mkdir(parents=True, exist_ok=True)
    records = {}
    for tile, source in SOURCES.items():
        original, source_sha256 = download(source)
        x0, y0, x1, y1 = source["crop"]
        if x1-x0 != 1536 or y1-y0 != 1024:
            raise ValueError("STOP: source crop is not native 1536x1024")
        crop = original[y0:y1, x0:x1].copy()
        path = output/f"{tile}-unaltered-native-source-v232.png"
        Image.fromarray(crop).save(path)
        records[tile] = {
            "sourceTitle": source["title"],
            "author": source["author"],
            "sourcePage": "https://commons.wikimedia.org/wiki/File:" + source["title"].replace(" ", "_"),
            "sourceSha1": source["sourceSha1"],
            "sourceSha256": source_sha256,
            "nativeCrop": source["crop"],
            "nativeCropSha256": hashlib.sha256(crop.tobytes()).hexdigest(),
            "file": path.name,
            "license": LICENSE,
            "licenseUrl": LICENSE_URL,
            "sourceRegisteredToV123": False,
            "historicalRoadsVerified": False,
            "productionApproved": False,
        }
    manifest = {
        "version": 232,
        "stage": "PRE-ROAD-STRIP NATIVE SOURCE AUDIT",
        "unmodifiedSourcePixels": True,
        "historicalGeographyVerified": False,
        "productionApproved": False,
        "sources": records,
    }
    (output/"native-source-manifest.json").write_text(json.dumps(manifest, indent=2)+"\n")
    return manifest

if __name__ == "__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--output",type=Path,default=Path("terrain-v232/native-crops"))
    args=p.parse_args()
    print(json.dumps(extract(args.output),indent=2))

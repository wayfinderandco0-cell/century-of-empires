#!/usr/bin/env python3
"""Package genuinely authored countryside PNGs into native-size V267 raster cells.
No procedural terrain, resizing, cloned trees, synthetic roads or fake historical labels.
Requires an actual independently generated or hand-authored 1536x1024 source image.
"""
import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image

def package(source: Path, output: Path, quality: int = 75):
    if not source.is_file():
        raise FileNotFoundError(f"Original source image missing: {source}")
    with Image.open(source) as original:
        if original.size != (1536, 1024):
            raise ValueError(f"Refusing to rescale/warp source: {original.size} != (1536,1024)")
        if original.mode not in ("RGB", "RGBA"):
            original = original.convert("RGB")
        corners = [original.getpixel((x, y))[:3] for x,y in ((0,0),(1535,0),(0,1023),(1535,1023))]
        if any(max(c) > 35 for c in corners):
            raise ValueError("Expected dark nonplayable octagon corners; inspect the art framing")
        output.parent.mkdir(parents=True,exist_ok=True)
        original.save(output,format="WEBP",quality=quality,method=6)
    with Image.open(output) as check:
        if check.size != (1536,1024):
            raise AssertionError("Packaged art dimensions changed")
    return {"source":str(source),"asset":str(output),"bytes":output.stat().st_size,
            "sha256":hashlib.sha256(output.read_bytes()).hexdigest(),
            "quality":quality,"originalPixelsRetained":True,
            "roadOrRiverGeometryCertified":False,"artApproval":"pending"}

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("source",type=Path)
    p.add_argument("output",type=Path)
    p.add_argument("--quality",type=int,default=75)
    a=p.parse_args()
    print(json.dumps(package(a.source,a.output,a.quality),indent=2))

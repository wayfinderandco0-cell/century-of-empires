#!/usr/bin/env python3
"""Export small base64-encoded visual QA images for human review via GitHub text API.
No original or gameplay source files are changed. This is NOT automated approval.
"""
from pathlib import Path
from PIL import Image
import base64
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"terrain-grid/v267-southeast-road-02"
inputs=[
    ("southeast-02-seam-review.webp","southeast-02-seam-review-small.webp",900,540),
    ("native-webkit-390x844-southeast-road-v2-candidate.png","southeast-02-native-iphone-small.webp",390,844),
    ("southeast-02-local-ruts.webp","southeast-02-art-small.webp",1000,667)
]
for source,name,w,h in inputs:
    with Image.open(OUT/source) as im:
        image=im.convert("RGB").resize((w,h),Image.Resampling.LANCZOS)
        target=OUT/name
        image.save(target,"WEBP",quality=45,method=6)
        encoded=base64.b64encode(target.read_bytes()).decode("ascii")
        (OUT/(name+".base64.txt")).write_text(encoded)
        print(name,"bytes",target.stat().st_size,"base64 chars",len(encoded))

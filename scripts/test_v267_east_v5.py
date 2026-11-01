#!/usr/bin/env python3
"""Conservative V267 EAST-01 V5 output checks; never certifies visual road seams."""
import hashlib,json
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/"terrain-grid/v267-original-art-batch-01"
j=json.loads((p/"matrei-east-v5-road-evidence.json").read_text())
src=ROOT/j["sourceMatrei"]
assert hashlib.sha256(src.read_bytes()).hexdigest()==j["matreiSourceSha256"]
assert j["sourceOriginalsUnchanged"] and j["roadPortContract"]["endpointGapPx"]==0
for key in ("physicalRoadSeamVerified","riverSeamVerified","roadAppearanceVisuallyApproved",
            "historicallyVerified","nativePlayable","userApproved","finished"):
    assert j[key] is False,key
with Image.open(p/j["candidate"]) as im:assert im.size==(1536,1024)
with Image.open(p/j["matreiDisplayOverlay"]) as im:
    assert im.mode=="RGBA" and im.size==(1536,1024)
    a=im.getchannel("A")
    assert a.getpixel((1000,749))==0
    assert a.getpixel((1450,750))>0
with Image.open(p/j["contact"]) as im:assert im.size==(3072,1024)
assert hashlib.sha256((p/j["candidate"]).read_bytes()).hexdigest()==j["candidateSha256"]
print("PASS: V5 artwork exists, overlay isolated, source unchanged, route still disabled")

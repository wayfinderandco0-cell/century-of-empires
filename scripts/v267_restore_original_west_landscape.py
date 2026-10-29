#!/usr/bin/env python3
"""Replace the visibly pasted WEST cirque with one coherent native Alpine photograph.

This is an isolated V267 art-only candidate. It intentionally preserves the
original V121 Matrei bytes, V123 route arrays, V94 campaign, sprites and saves.
The original WEST photograph contains its own real-looking alpine tarn, rocky
cirque and forest. No Matrei pixels, mirrored terrain or digital roads are added.
"""
from __future__ import annotations

import base64
import hashlib
import io
import re
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "v267-three-octagon-original-art-prototype.html"
SOURCE = ROOT / "art-reviews/v267-original-source/west-native-original.jpg"
OUTPUT = ROOT / "art-reviews/v267-original-source/west-native-restored-unapproved.jpg"
REVIEW = ROOT / "art-reviews/v267-west-source-restoration-review.md"
W, H = 1536, 1024

# Existing V267 source-road / immutable V123 display coordinates. This is
# artwork registration only; no new node, graph edge or path is created.
ROUTE = np.array([
    [275,548,550], [370,520,522], [470,552,520], [570,635,540],
    [680,589,560], [784,575,551], [890,621,535], [980,648,515],
    [1085,630,507], [1210,586,490], [1320,559,480],
    [1450,558,478], [1536,576,478]
], dtype=np.float32)


def smooth(t):
    t = np.clip(t, 0, 1)
    return t*t*(3-2*t)


def reconstruct_native():
    """Use only the original WEST source, preserving its coherent landscape."""
    with Image.open(SOURCE) as im:
        native = np.asarray(im.convert("RGB").resize((W,H),Image.Resampling.LANCZOS))
    xx = np.arange(W,dtype=np.float32)
    yy = np.arange(H,dtype=np.float32)
    delta = np.interp(xx, ROUTE[:,0], ROUTE[:,1]-ROUTE[:,2])
    # Same pre-existing WEST art-to-route registration as the accepted
    # V267 source registration. Crucially, remove the pasted cirque ellipse.
    falloff = smooth(yy/110)*smooth((H-1-yy)/285)
    map_x = np.broadcast_to(xx[None,:],(H,W)).copy()
    map_y = np.broadcast_to(yy[:,None]+falloff[:,None]*delta[None,:],(H,W))
    result = cv2.remap(native,map_x,np.clip(map_y,0,H-1.001).astype(np.float32),
                       cv2.INTER_CUBIC,borderMode=cv2.BORDER_REPLICATE)
    return Image.fromarray(result)


def main():
    original = HTML.read_text(encoding="utf-8")
    pattern = r'(?<!\\w)ART_WEST="data:image/[^;]+;base64,[^"]+"'
    matches = list(re.finditer(pattern,original))
    if len(matches)!=1:
        raise RuntimeError("Expected exactly one embedded WEST art source")
    image = reconstruct_native()
    buffer = io.BytesIO()
    image.save(buffer,"JPEG",quality=93,subsampling=0,optimize=True)
    data = buffer.getvalue()
    replacement = 'ART_WEST="data:image/jpeg;base64,'+base64.b64encode(data).decode("ascii")+'"'
    m = matches[0]
    updated = original[:m.start()]+replacement+original[m.end():]
    # Enforce an art-only change. V123 road arrays and all other HTML bytes
    # must remain identical.
    assert updated[:m.start()] == original[:m.start()]
    assert updated[m.start()+len(replacement):] == original[m.end():]
    for marker in ("const southRoad=", "const westRoad=", "ART_MATREI_CANONICAL="):
        assert marker in original and marker in updated,marker
    digest=hashlib.sha256(data).hexdigest()
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    OUTPUT.write_bytes(data)
    HTML.write_text(updated,encoding="utf-8")
    REVIEW.write_text(
        "# WEST coherent original-source reconstruction — UNAPPROVED\n\n"
        "This removes the visible composited ellipse/patch around the added "
        "WEST cirque and restores one continuous original Alpine photograph "
        "with its own small natural mountain lake, rocky terrain and forest. "
        "The pre-existing V267 art-to-V123 cartway registration is retained. "
        "No new road, settlement, Matrei copy, mirrored tree or synthetic "
        "forest was added. No change outside ART_WEST in the HTML.\n\n"
        "This is fictional game-art prototype, not verified historical "
        "topography. The WEST–MATREI and Matrei–SOUTH terrain seams remain "
        "subject to real iPhone Safari visual approval. Production RED.\n\n"
        f"Source: {SOURCE.relative_to(ROOT)}\n"
        f"Output: {OUTPUT.relative_to(ROOT)}\n"
        f"Output dimensions: {W}x{H}\n"
        f"Output SHA256: {digest}\n",
        encoding="utf-8")
    print("Restored coherent WEST native artwork",len(data),"bytes",digest)


if __name__=="__main__":
    main()

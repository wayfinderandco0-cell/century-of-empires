#!/usr/bin/env python3
"""Local SOUTH road-bearing seam registration; isolated V267 review only.

Move the existing photographed meadow/cartway, not a synthetic road stripe.
The V121 image, V123 graph, WEST source, V94, sprites and saves are immutable.
Fictional Alpine prototype artwork, not verified historical geography.
"""
from __future__ import annotations
import base64, hashlib, io, re
from pathlib import Path
import cv2
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
HTML=ROOT/"v267-three-octagon-original-art-prototype.html"
ART=ROOT/"art-reviews/v267-original-source/south-cartway-edge-contact-unapproved.jpg"
NOTE=ROOT/"art-reviews/v267-south-cartway-edge-contact-review.md"
MARKER="SOUTH_CARTWAY_EDGE_CONTACT_20261029"
W,H=1536,1024

def smooth(a):
    a=np.clip(a,0,1)
    return a*a*(3-2*a)

def register(image):
    """Correct the northern photographed road's ~35px westward drift.

    A source-coordinate translation is bounded to the upper 340px meadow.
    x>=900 and y>=340 stay EXACTLY native; no global SOUTH forest warp.
    """
    y,x=np.mgrid[0:H,0:W].astype(np.float32)
    shift=35.0*smooth((340.0-y)/340.0)*smooth((900.0-x)/220.0)
    moved=cv2.remap(image,np.clip(x-shift,0,W-1).astype(np.float32),y,
                    cv2.INTER_LINEAR,borderMode=cv2.BORDER_REPLICATE)
    moved[y>=340]=image[y>=340]
    moved[:,900:]=image[:,900:]
    return moved

def main():
    html=HTML.read_text(encoding="utf-8")
    if MARKER in html:
        print("Already registered: no double resampling")
        return
    pat=re.compile(r'ART_SOUTH="data:image/[^;]+;base64,([^"]+)"')
    hits=list(pat.finditer(html))
    if len(hits)!=1:
        raise RuntimeError("Expected one embedded SOUTH art source")
    before=Image.open(io.BytesIO(base64.b64decode(hits[0].group(1)))).convert("RGB")
    if before.size!=(W,H):
        raise RuntimeError("Unexpected SOUTH source dimensions")
    result=register(np.asarray(before))
    buff=io.BytesIO()
    Image.fromarray(result).save(buff,"JPEG",quality=94,subsampling=0,optimize=True)
    data=buff.getvalue()
    replacement='ART_SOUTH="data:image/jpeg;base64,'+base64.b64encode(data).decode("ascii")+'"'
    m=hits[0]
    changed=html[:m.start()]+replacement+html[m.end():]
    marker="const southRoad="
    if changed.count(marker)!=1 or html.count(marker)!=1:
        raise RuntimeError("V123 road declaration absent or duplicated")
    changed=changed.replace(marker,"/* "+MARKER+" */ "+marker,1)
    # Every other byte of the HTML must remain unchanged.
    original_rest=pat.sub('ART_SOUTH="IMAGE"',html,count=1)
    new_rest=pat.sub('ART_SOUTH="IMAGE"',changed,count=1).replace(
        "/* "+MARKER+" */ ","",1)
    if original_rest!=new_rest:
        raise AssertionError("Unexpected renderer, graph or engine change")
    assert "ART_MATREI_CANONICAL=" in changed and "const westRoad=" in changed
    ART.parent.mkdir(parents=True,exist_ok=True)
    ART.write_bytes(data)
    HTML.write_text(changed,encoding="utf-8")
    NOTE.write_text(
        "# SOUTH photographic cartway edge registration — UNAPPROVED\n\n"
        "Original fictional Alpine game art; no claim of historical topography. "
        "The existing SOUTH photograph's upper meadow and dirt road were "
        "registered 35 source pixels east at the MATREI boundary, fading "
        "continuously to zero by y340 and x900. The cartway is photographed "
        "terrain, not a digital overlay. Forest and river east of x900, "
        "the entire lower y>=340 landscape, WEST, the original V121 image, "
        "the immutable 100-node V123 graph, V94, sprites and saves remain "
        "untouched. No production merge.\n\n"
        "Remaining visual blocker: the Matrei/SOUTH landform and forest "
        "transition is still conspicuous; WEST/MATREI also requires approval. "
        "Real physical iPhone Safari acceptance outstanding. Production RED.\n\n"
        "SOUTH SHA256: "+hashlib.sha256(data).hexdigest()+"\n",
        encoding="utf-8")
    print("Registered real SOUTH cartway locally",len(data),
          hashlib.sha256(data).hexdigest())

if __name__=="__main__":
    main()

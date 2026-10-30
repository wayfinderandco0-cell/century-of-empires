#!/usr/bin/env python3
"""SOUTH river alignment: rigid native photographic terrain transfer, isolated V267 only.

This is an unapproved fictional Alpine-art candidate, not verified topography.
Never edits V121 source, V123 graph, V94, campaign, sprites or saves.
"""
from __future__ import annotations
import base64, hashlib, io, re
from pathlib import Path
import cv2
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "v267-three-octagon-original-art-prototype.html"
OUT = ROOT / "art-reviews/v267-original-source/south-river-east-contact-unapproved.webp"
REPORT = ROOT / "art-reviews/v267-south-river-east-contact-review.md"
W, H = 1536, 1024
MARKER = "SOUTH_RIVER_EAST_RIGID_CANDIDATE_20261029"

def smooth(a):
    a = np.clip(a, 0, 1)
    return a*a*(3-2*a)

def embedded(html, name):
    m = re.search(r'(?<!\w)' + name + r'="data:image/[^;]+;base64,([^"]+)"', html)
    if not m:
        raise RuntimeError("Missing source art " + name)
    im = Image.open(io.BytesIO(base64.b64decode(m.group(1)))).convert("RGB")
    if im.size != (W,H):
        raise RuntimeError("Unexpected source dimensions for " + name + ": " + str(im.size))
    return np.asarray(im)

def water_center(rgb, y0, y1):
    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
    band = hsv[y0:y1].astype(np.float32).mean(axis=0)
    mask = ((band[:,0] > 80) & (band[:,0] < 125) &
            (band[:,1] > 30) & (band[:,2] > 65))
    xx = np.where(mask[450:1350])[0]
    return float(450 + xx.mean()) if len(xx) else None

def main():
    html = HTML.read_text(encoding="utf-8")
    if MARKER in html:
        print("Candidate already integrated, no repeat resampling")
        return
    original_matrei = re.search(r'ART_MATREI_CANONICAL="([^"]+)"', html)
    if not original_matrei:
        raise RuntimeError("Missing protected Matrei source")
    protected_matrei = hashlib.sha256(original_matrei.group(1).encode()).hexdigest()
    west_road = re.search(r'const westRoad=([^;]+);', html)
    south_road = re.search(r'const southRoad=([^;]+);', html)
    if not west_road or not south_road:
        raise RuntimeError("Protected V123 roads not found")
    assert "[1536,478]" in west_road.group(1)
    assert "[466,0]" in south_road.group(1)
    south = embedded(html, "ART_SOUTH")
    matrei_source = embedded(html, "ART_MATREI_CANONICAL")
    # The existing Matrei preview mapping is a render-only source registration.
    # Compare river color at the actual bottom crossing, not arbitrary photograph centers.
    # Its measured crossing is near x949; existing SOUTH upper river is near x839.
    # The old x+116 sampling moved the SOUTH gorge WEST; this candidate moves it EAST.
    matrei_crossing = 949.0
    south_crossing = water_center(south,0,20)
    if south_crossing is None or not (750 < south_crossing < 950):
        raise RuntimeError("Unexpected SOUTH river location; refuse blind registration")
    dx = int(round(matrei_crossing - south_crossing))
    if not (65 <= dx <= 150):
        raise RuntimeError("Unsafe shift " + str(dx))
    yy, xx = np.mgrid[0:H,0:W].astype(np.float32)
    # One-to-one source pixel translation; NO global warp, NO repeated forest
    # scaling, NO digital road stripe. Native x466 cartway is untouched.
    rigid = cv2.remap(south, np.clip(xx-dx,0,W-1), yy,
                      cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    # Curved, irregular patch boundary avoids a straight cut through the forest.
    # Keep the bridge and road below y~300 completely in their native positions.
    left = 665 + .30*np.minimum(yy,350)
    lower = 265 + 25*np.sin(xx/91) + 13*np.sin(xx/29)
    mask = smooth((xx-left)/35)*smooth((lower-yy)/26)
    candidate = np.uint8(np.clip(
        rigid*mask[:,:,None]+south*(1-mask[:,:,None]),0,255))
    # Verify protected pixels remain literally identical near the V123 entrance.
    assert np.array_equal(candidate[:220,420:530], south[:220,420:530])
    assert np.array_equal(candidate[400:],south[400:])
    OUT.parent.mkdir(parents=True,exist_ok=True)
    Image.fromarray(candidate).save(OUT, "WEBP", quality=83, method=6)
    # Only add an opt-in mode. The default embedded SOUTH, all V121 art, all
    # V123 arrays and the existing game renderer remain unchanged.
    old = 'const SOUTH_APRON_PREVIEW=SOUTH_ART_MODE==="apron";'
    new = ('const SOUTH_RIVER_EAST_PREVIEW=SOUTH_ART_MODE==="river"; '
           '/* '+MARKER+' */\n'+old)
    if html.count(old)!=1:
        raise RuntimeError("Unexpected preview mode declaration")
    html=html.replace(old,new,1)
    old='const southArtSource=SOUTH_APRON_PREVIEW'
    new=('const southArtSource=SOUTH_RIVER_EAST_PREVIEW\n'
         '  ? "art-reviews/v267-original-source/south-river-east-contact-unapproved.webp"\n'
         '  : SOUTH_APRON_PREVIEW')
    if html.count(old)!=1:
        raise RuntimeError("Unexpected source selection")
    html=html.replace(old,new,1)
    assert hashlib.sha256(re.search(r'ART_MATREI_CANONICAL="([^"]+)"',html).group(1).encode()).hexdigest()==protected_matrei
    assert west_road.group(0) in html and south_road.group(0) in html
    HTML.write_text(html,encoding="utf-8")
    REPORT.write_text(
        "# SOUTH river eastward native-source registration — UNAPPROVED\n\n"
        "Fictional prototype Alpine game art, not verified historical terrain.\n\n"
        "A physical mismatch was identified: Matrei's southern river exits near x949, "
        "but the embedded SOUTH river enters near x"+str(round(south_crossing))+
        ". The previous source mapping sampled x+116, moving that river further "
        "west. This candidate instead transfers upper-right native photographic "
        "material "+str(dx)+"px EAST as a rigid 1:1 source patch, with a curved "
        "transition confined above y~300 and east of the x466 cartway. No tree "
        "scaling, bridge movement, new roads or V123 graph changes.\n\n"
        "Review only with ?southArt=river. Default preview unchanged. The "
        "Matrei/SOUTH visual forest and river material seam still requires physical "
        "iPhone inspection and may require new authored terrain. Do not approve "
        "based on water centroid or browser pass alone. Production RED.\n\n"
        "WebP SHA256: "+hashlib.sha256(OUT.read_bytes()).hexdigest()+"\n",
        encoding="utf-8")
    print("Generated",OUT,"bytes",OUT.stat().st_size,
          "river x",round(south_crossing),"east shift",dx)

if __name__=="__main__":
    main()

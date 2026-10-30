#!/usr/bin/env python3
"""Rebuild the existing V267 SOUTH river/forest contact from native original art.

Fictional Alpine game-art prototype, not verified historical geography.
The previous 260px SOUTH forest was a cloned stand with a visible rectangular
edge. This replacement restores the original unwarped rock/meadow/conifers,
then performs multiscale photographic boundary registration against Matrei's
existing rendered edge. No new route, invented road stripe, tree warp or tile.
Only the opt-in ?southArt=river asset is rebuilt; production stays RED.
"""
from __future__ import annotations
import hashlib,re
from pathlib import Path
import cv2
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
HTML=ROOT/'v267-three-octagon-original-art-prototype.html'
SOURCE=ROOT/'art-reviews/v267-original-source/south-river-east-contact-unapproved.webp'
OUTPUT=ROOT/'art-reviews/v267-original-source/south-forest-river-continuity-unapproved.webp'
REPORT=ROOT/'art-reviews/v267-forest-river-continuity-review.md'
W,H=1536,1024

def smooth(v):
    v=np.clip(v,0,1)
    return v*v*(3-2*v)

def build(native,matrei):
    """Restore original 1:1 SOUTH terrain; register border at multiple scales.

    A narrow high-frequency correction matches individual photographic edge
    pixels, while longer wavelength differences decay through the first 270px.
    SOUTH's own tree/rock/water gradients remain intact; no pixel is moved.
    """
    assert native.shape==matrei.shape==(H,W,3)
    delta=matrei[1022].astype(np.float32)-native[0].astype(np.float32)
    low=cv2.GaussianBlur(delta[None,:,:],(0,0),37)[0]
    mid=cv2.GaussianBlur(delta[None,:,:],(0,0),7)[0]-low
    high=delta-low-mid
    xx=np.arange(W,dtype=np.float32)
    # Matrei's bottom octagon edge is only x256..1280; do not copy its
    # exterior black/gold frame into SOUTH or darken terrain outside it.
    across=smooth((xx-256)/30)*smooth((1280-xx)/30)
    result=native.copy()
    for y in range(270):
        slow=(1-y/270)**2
        medium=(1-y/92)**2 if y<92 else 0
        fine=(1-y/18)**2 if y<18 else 0
        correction=(low*slow+mid*medium+high*fine)*across[:,None]
        result[y]=np.uint8(np.clip(native[y].astype(np.float32)+correction,0,255))
    assert np.array_equal(result[270:],native[270:])
    assert np.array_equal(result[:270,:256],native[:270,:256])
    assert np.array_equal(result[:270,1280:],native[:270,1280:])
    # The V123 road at x466 and native stone bridge below y270 retain their
    # actual source positions and unscaled geometry.
    return result

def main():
    html=HTML.read_text(encoding='utf-8')
    original_matrei=re.search(r'ART_MATREI_CANONICAL="([^"]+)"',html)
    west=re.search(r'const westRoad=([^;]+);',html)
    south=re.search(r'const southRoad=([^;]+);',html)
    assert original_matrei and west and south
    assert '[1536,478]' in west.group(1) and '[466,0]' in south.group(1)
    assert 'art-reviews/v267-original-source/south-forest-river-continuity-unapproved.webp' in html
    matrei_hash=hashlib.sha256(original_matrei.group(1).encode()).hexdigest()
    from rebuild_v267_south_natural_apron import decode,matrei_ground
    matrei=matrei_ground(decode(html,'ART_MATREI_CANONICAL')[0])
    native=np.asarray(Image.open(SOURCE).convert('RGB'))
    result=build(native,matrei)
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    Image.fromarray(result).save(OUTPUT,'WEBP',quality=92,method=6)
    assert hashlib.sha256(HTML.read_bytes()).hexdigest()==hashlib.sha256(html.encode()).hexdigest()
    assert hashlib.sha256(re.search(r'ART_MATREI_CANONICAL="([^"]+)"',HTML.read_text()).group(1).encode()).hexdigest()==matrei_hash
    REPORT.write_text(
        '# V267 native SOUTH riverbank and forest contact — UNAPPROVED\n\n'
        'Fictional original Alpine game art, not historically verified terrain.\n\n'
        'The previous cloned rectangular forest stand is removed. The full '
        '1536×1024 native SOUTH photographic terrain is restored from the '
        'earlier durable river-east source, preserving the original meadow, '
        'individual conifers, cliff faces, turquoise gorge and stone bridge. '
        'A 270px northern material-contact region uses a three-scale '
        'photographic boundary reconstruction against the actual rendered '
        'Matrei bottom edge: 18px fine, 92px medium and 270px broad. '
        'No pixels are translated, resized or mirrored; no synthetic road '
        'or route graph edges are introduced. The x466 original cartway '
        'geometry, bridge below y270 and all lower SOUTH art are untouched. '
        'The protected V121 source, 100-node V123 graph, V94 campaign, '
        'sprites, saves and production are unchanged.\n\n'
        'This remains an OPT-IN ?southArt=river candidate. Actual browser '
        'phone-size views and physical iPhone review are needed. The cliff '
        'and river morphology still differ across the boundary, and pixel '
        'contact alone does not constitute visual approval. Production RED.\n\n'
        'Input SHA256: '+hashlib.sha256(SOURCE.read_bytes()).hexdigest()+'\n'
        'Output SHA256: '+hashlib.sha256(OUTPUT.read_bytes()).hexdigest()+'\n',
        encoding='utf-8')
    print('Rebuilt native SOUTH riverbank and forest contact:',OUTPUT,
          OUTPUT.stat().st_size,'bytes')

if __name__=='__main__': main()

#!/usr/bin/env python3
"""Isolated SOUTH source-native river-throat reconstruction for Matrei contact.

The northern Matrei display edge carries river water near x943; the current
SOUTH photograph has its water near x1088. This reconstruction registers the
upper *rock and water* corridor, not the SOUTH tile, its road, trees or bridge.
Fictional 1780-1880-style Alpine game art, not verified historical topography.
"""
from __future__ import annotations
import hashlib, json, re
from pathlib import Path
import cv2
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'art-reviews/v267-original-source/south-forest-river-continuity-unapproved.webp'
OUTPUT=ROOT/'art-reviews/v267-original-source/south-gorge-river-registered-unapproved.webp'
HTML=ROOT/'v267-three-octagon-original-art-prototype.html'
REPORT=ROOT/'art-reviews/v267-gorge-river-registration-review.md'
W,H=1536,1024
MARKER='SOUTH_GORGE_RIVER_SOURCE_REGISTERED_20261030'

def smooth(t):
    t=np.clip(t,0.,1.)
    return t*t*(3-2*t)

def water_material_mask(photo):
    """Segment photographed turquoise river and adjacent natural banks."""
    hsv=cv2.cvtColor(photo,cv2.COLOR_RGB2HSV)
    water=((hsv[:,:,0]>=77)&(hsv[:,:,0]<=128)&
           (hsv[:,:,1]>=34)&(hsv[:,:,2]>=50)).astype(np.uint8)*255
    water=cv2.morphologyEx(water,cv2.MORPH_CLOSE,
                           cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(15,15)))
    # Natural rock edges immediately beside water belong to the same gorge;
    # do not clone the surrounding meadow or entire conifer stands.
    water=cv2.dilate(water,
                     cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(63,63)))
    return cv2.GaussianBlur(water.astype(np.float32)/255,(0,0),12)


def rebuild(source):
    assert source.shape==(H,W,3)
    # Previous rigid whole-cliff replacement made a second horizontal
    # limestone ledge. Keep every ORIGINAL cliff and tree outside the
    # photographed riverbanks; only transfer a different natural river reach.
    donor=source.copy()
    donor[:330,:1466]=source[190:520,70:1536]
    yy,xx=np.mgrid[:H,:W].astype(np.float32)
    material=np.maximum(water_material_mask(donor),
                        water_material_mask(source))
    # Only the upper river throat is reconstructed. The 466px cartway,
    # bridge, original lower river and all surrounding native trees stay.
    corridor=smooth((xx-755)/55)*smooth((1365-xx)/55)
    depth=smooth((355-yy)/105)
    alpha=np.clip(material*corridor*depth*.98,0,.98)
    alpha[355:]=0
    alpha[:,:690]=0
    alpha[:,1420:]=0
    result=np.uint8(np.clip(
        source.astype(np.float32)*(1-alpha[:,:,None])+
        donor.astype(np.float32)*alpha[:,:,None],0,255))
    assert np.array_equal(result[355:],source[355:])
    assert np.array_equal(result[:,:690],source[:,:690])
    assert np.array_equal(result[:,1420:],source[:,1420:])
    changed=np.abs(result.astype(np.int16)-source.astype(np.int16))
    pixels=int(np.count_nonzero(np.max(changed,axis=2)>8))
    assert pixels>30000, f'Upper water/bank reconstruction too small: {pixels}'
    return result,pixels

def stage(html):
    if MARKER in html:
        return html
    assert html.count('const southRoad=')==1 and html.count('const westRoad=')==1
    assert '[1536,478]' in html and '[466,0]' in html
    assert 'ART_MATREI_CANONICAL=' in html
    old='const SOUTH_RIVER_EAST_PREVIEW=SOUTH_ART_MODE==="river";'
    new=('const SOUTH_GORGE_RIVER_PREVIEW=SOUTH_ART_MODE==="gorge"; '
         '/* '+MARKER+' */\n'+old)
    assert html.count(old)==1
    html=html.replace(old,new,1)
    old='const southArtSource=SOUTH_RIVER_EAST_PREVIEW'
    new=('const southArtSource=SOUTH_GORGE_RIVER_PREVIEW\n'
         '  ? "art-reviews/v267-original-source/south-gorge-river-registered-unapproved.webp"\n'
         '  : SOUTH_RIVER_EAST_PREVIEW')
    assert html.count(old)==1
    html=html.replace(old,new,1)
    # This remains the exact existing V123 playable preview, no new
    # renderer, graph, sprites or game engine. Only opt-in source selection.
    return html

def main():
    original_html=HTML.read_text(encoding='utf-8')
    with Image.open(SOURCE) as im:
        if im.size!=(W,H): raise ValueError('Unexpected SOUTH dimensions')
        source=np.asarray(im.convert('RGB'))
    result,pixels=rebuild(source)
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    Image.fromarray(result).save(OUTPUT,'WEBP',quality=94,method=6)
    new_html=stage(original_html)
    if new_html!=original_html:HTML.write_text(new_html,encoding='utf-8')
    REPORT.write_text(
        '# Isolated SOUTH upper river-gorge registration — UNAPPROVED\n\n'
        'A substantive source-art candidate, not a verified historic Alpine map.\n'
        'Matrei visible river mouth ~x943; previous SOUTH upper mouth ~x1088.\n'
        'The upper native limestone and water corridor is locally registered '
        'toward the fixed Matrei mouth. Native tree/grass pixels are protected; '
        'the cartway and stone bridge stay at their existing V123 positions. '
        'No global SOUTH warp, mirrored tile, digital road stripe, invented '
        'settlement, V121/V123/V94/sprite/save or production change.\n\n'
        f'Changed visible source pixels (>8 channel difference): {pixels}.\n'
        'Review ?southArt=gorge against ?southArt=river at the same '
        'iPhone camera. Rock edges and forest transitions may still be '
        'visually imperfect. Passing movement tests does not approve art.\n\n'
        f'SOURCE SHA256: {hashlib.sha256(SOURCE.read_bytes()).hexdigest()}\n'
        f'OUTPUT SHA256: {hashlib.sha256(OUTPUT.read_bytes()).hexdigest()}\n'
        'Production RED; requires physical iPhone visual approval.\n',
        encoding='utf-8')
    print(json.dumps({'art':str(OUTPUT.relative_to(ROOT)),
        'bytes':OUTPUT.stat().st_size,'changed_pixels':pixels,
        'html_staged':new_html!=original_html,'status':'UNAPPROVED'}))
if __name__=='__main__':main()

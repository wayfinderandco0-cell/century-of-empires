#!/usr/bin/env python3
"""Rebuild the SOUTH forest/river border as native photographic terrain, V267 only.

This is fictional Alpine game art, NOT verified historical topography.
Never modifies Matrei V121, V123 routes, V94, sprites, saves, or production.
Replaces the previous SOUTH river opt-in candidate (same ?southArt=river mode);
does not create a new game mode or branch.
"""
from __future__ import annotations
import hashlib, json, re
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
OLD='art-reviews/v267-original-source/south-river-east-contact-unapproved.webp'
NEW='art-reviews/v267-original-source/south-forest-river-continuity-unapproved.webp'

def smooth(a):
    a=np.clip(a,0,1)
    return a*a*(3-2*a)

def build(native):
    yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
    # Real, unscaled conifers sampled from a DISTINCT native SOUTH forest stand.
    # SOUTH's bare meadow previously severed the Matrei conifer canopy at the
    # x≈550..800 border. No mirrored trees, synthesized green fill, or x-warp.
    donor=cv2.remap(native,xx+675,yy+35,cv2.INTER_LINEAR,
                    borderMode=cv2.BORDER_REPLICATE)
    # Natural uneven forest line; only a 6-7px feather at the vegetation edge.
    left=528+0.20*yy+12*np.sin(yy/37)+6*np.sin(yy/11)
    right=830-0.15*yy+16*np.sin(yy/48)+5*np.sin(yy/14)
    bottom=260+18*np.sin(xx/71)+9*np.sin(xx/19)
    mask=smooth((xx-left)/6)*smooth((right-xx)/6)*smooth((bottom-yy)/7)
    # Cartway x466, river x>900, and native bridge remain EXACT source pixels.
    mask[:,860:]=0
    candidate=np.uint8(np.clip(
        native*(1-mask[:,:,None])+donor*mask[:,:,None],0,255))
    assert np.array_equal(candidate[:,900:],native[:,900:])
    assert np.array_equal(candidate[370:],native[370:])
    assert np.array_equal(candidate[:220,400:490],native[:220,400:490])
    assert np.mean(np.abs(candidate[:250,570:760].astype(np.int16)-
                          native[:250,570:760].astype(np.int16)))>15
    return candidate

def main():
    html=HTML.read_text(encoding='utf-8')
    matrei=re.search(r'ART_MATREI_CANONICAL="([^"]+)"',html)
    west=re.search(r'const westRoad=([^;]+);',html)
    south=re.search(r'const southRoad=([^;]+);',html)
    assert matrei and west and south
    assert '[1536,478]' in west.group(1) and '[466,0]' in south.group(1)
    protected=hashlib.sha256(matrei.group(1).encode()).hexdigest()
    assert html.count(OLD)+html.count(NEW)==1
    native=np.asarray(Image.open(SOURCE).convert('RGB'))
    assert native.shape==(H,W,3)
    art=build(native)
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    Image.fromarray(art).save(OUTPUT,'WEBP',quality=92,method=6)
    if OLD in html:
        html=html.replace(OLD,NEW,1)
        HTML.write_text(html,encoding='utf-8')
    after=HTML.read_text(encoding='utf-8')
    assert hashlib.sha256(re.search(r'ART_MATREI_CANONICAL="([^"]+)"',
                                   after).group(1).encode()).hexdigest()==protected
    assert west.group(0) in after and south.group(0) in after
    REPORT.write_text(
        '# V267 SOUTH native forest/river contact — UNAPPROVED\n\n'
        'Fictional Alpine artwork; not a claim about 1780–1880 topography.\n\n'
        'Rebuilt approximately 260×260 pixels of the northern SOUTH forest '
        'with a 1:1 native photographic conifer stand. The Matrei boundary '
        'previously dropped directly into bare SOUTH meadow. The new forest '
        'line is irregular and ends naturally in the meadow; no global terrain '
        'warp or digital road stripe was added. The actual cartway at x466, '
        'river and stone bridge at x>900, and terrain below y370 are unchanged '
        'from the previous river-east candidate. The older source remains '
        'durably stored. This reuses the SAME opt-in ?southArt=river candidate, '
        'not a new mode.\n\n'
        'Remaining visual risk: the Matrei/SOUTH cliff and water material '
        'transition may still be visible; physical iPhone review required. '
        'Passing browser route tests alone does not approve the art.\n\n'
        'Source SHA256: '+hashlib.sha256(SOURCE.read_bytes()).hexdigest()+'\n'
        'Candidate SHA256: '+hashlib.sha256(OUTPUT.read_bytes()).hexdigest()+'\n'
        'Protected: V121 Matrei, V123 graph, V94 campaign, sprites, saves, main. '
        'Production RED.\n',encoding='utf-8')
    print('SUBSTANTIAL native forest artwork built:',OUTPUT,
          OUTPUT.stat().st_size,'bytes')

if __name__=='__main__': main()

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

def find_bottom_seam(original, donor):
    """Choose a native-pixel join, rather than compressing river and cliffs.

    The donor is a rigid translation of a DIFFERENT photographed section of
    the same SOUTH source. A shallow 2-D minimum-error cut runs through its
    lower bank, with only a few pixels of feathering.
    """
    lo, hi, left, right = 222, 312, 720, 1370
    a = cv2.cvtColor(original[lo:hi+1, left:right], cv2.COLOR_RGB2LAB)
    b = cv2.cvtColor(donor[lo:hi+1, left:right], cv2.COLOR_RGB2LAB)
    mismatch = np.mean(np.abs(a.astype(np.float32)-b.astype(np.float32)), axis=2)
    ga = cv2.cvtColor(original[lo:hi+1,left:right],cv2.COLOR_RGB2GRAY)
    gb = cv2.cvtColor(donor[lo:hi+1,left:right],cv2.COLOR_RGB2GRAY)
    # Avoid cutting through sharp rock faces and trees where possible.
    edge = (cv2.Laplacian(ga,cv2.CV_32F).astype(np.float32)**2 +
            cv2.Laplacian(gb,cv2.CV_32F).astype(np.float32)**2)**0.5
    energy = cv2.GaussianBlur(mismatch,(5,5),0) + 0.028*edge
    ys = np.arange(lo,hi+1,dtype=np.float32)
    energy += 0.020*(ys[:,None]-266.0)**2
    n,m = energy.shape
    dp = np.empty((n,m),np.float64)
    parents = np.zeros((n,m),np.int8)
    dp[:,0] = energy[:,0]
    for x in range(1,m):
        options = np.stack((
            np.r_[dp[0,x-1]+1000,dp[:-1,x-1]+1.8],
            dp[:,x-1],
            np.r_[dp[1:,x-1]+1.8,dp[-1,x-1]+1000]),axis=1)
        choice = np.argmin(options,axis=1)
        dp[:,x] = energy[:,x]+options[np.arange(n),choice]
        parents[:,x] = choice.astype(np.int8)-1
    seam = np.zeros(m,np.float32)
    row = int(np.argmin(dp[:,-1]))
    for x in range(m-1,-1,-1):
        seam[x] = lo+row
        if x: row = int(np.clip(row+parents[row,x],0,n-1))
    # The seam is a path through original photographic material, not
    # an additional road, river line, or generated landscape texture.
    return cv2.GaussianBlur(seam.reshape(1,-1),(0,0),3.0).ravel()


def rebuild(source):
    assert source.shape==(H,W,3)
    # The existing SOUTH upper waterfall begins abruptly at the shared
    # Matrei boundary. Move a continuous, already photographed turquoise
    # river reach and its natural limestone banks UP 220px and LEFT 70px.
    # Every copied rock/tree/water pixel retains its original scale.
    # The V123 road x466 and stone bridge below y~560 remain untouched.
    donor=source.copy()
    donor[:320,:1466]=source[220:540,70:1536]
    seam=find_bottom_seam(source,donor)
    yy,xx=np.mgrid[:H,:W].astype(np.float32)
    # Only the existing river gorge and its banks are recomposed.
    # These deliberately irregular shoulders stay well east of the road.
    left=775 + .29*yy + 13*np.sin(yy/31)
    right=1235 + .12*yy + 17*np.sin(yy/44)
    left_alpha=smooth((xx-left)/21)
    right_alpha=smooth((right-xx)/21)
    seam_x=np.arange(720,1370,dtype=np.float32)
    bottom=np.interp(xx[0],seam_x,seam,left=266,right=266)[None,:]
    # A narrow source-aware bottom join prevents a second waterfall or
    # horizontal ghosted river. Do not stretch SOUTH forest or cliff pixels.
    bottom_alpha=smooth((bottom-yy+5)/10)
    alpha=left_alpha*right_alpha*bottom_alpha
    alpha[340:]=0
    alpha[:,:690]=0
    alpha[:,1420:]=0
    result=np.uint8(np.clip(
        source.astype(np.float32)*(1-alpha[:,:,None])+
        donor.astype(np.float32)*alpha[:,:,None],0,255))
    assert np.array_equal(result[340:],source[340:])
    assert np.array_equal(result[:,:690],source[:,:690])
    assert np.array_equal(result[:,1420:],source[:,1420:])
    changed=np.abs(result.astype(np.int16)-source.astype(np.int16))
    pixels=int(np.count_nonzero(np.max(changed,axis=2)>8))
    assert pixels>60000, f'Upper gorge reconstruction too small: {pixels}'
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

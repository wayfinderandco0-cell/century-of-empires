#!/usr/bin/env python3
"""Reconstruct SOUTH's river/forest join from two ORIGINAL unwarped photo artworks.

Use a structure-aware photographic seam, not a recolor, forest clone, digital
road overlay, or global terrain warp. The original bridge/contact image
supplies intact meadow, road and trees to the west; the river-east artwork
supplies the physically aligned gorge to the east. Preserve native pixels
away from the seam. Fictional Alpine prototype, not historical topography.
"""
from __future__ import annotations
import hashlib, re
from pathlib import Path
import cv2
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / 'v267-three-octagon-original-art-prototype.html'
WEST_SOURCE = ROOT / 'art-reviews/v267-original-source/south-bridge-contact-unapproved.webp'
RIVER_SOURCE = ROOT / 'art-reviews/v267-original-source/south-river-east-contact-unapproved.webp'
OUTPUT = ROOT / 'art-reviews/v267-original-source/south-forest-river-continuity-unapproved.webp'
REPORT = ROOT / 'art-reviews/v267-forest-river-continuity-review.md'
W, H = 1536, 1024

def smooth(t):
    t = np.clip(t, 0.0, 1.0)
    return t*t*(3.0-2.0*t)

def river_mask(rgb):
    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
    # Turquoise water, excluding green forest and tan road pigment.
    return ((hsv[:, :, 0] >= 79) & (hsv[:, :, 0] <= 126) &
            (hsv[:, :, 1] >= 38) & (hsv[:, :, 2] >= 54))

def find_photo_seam(west, east):
    """Find a low-disruption seam through real meadow, away from both rivers.

    A vertical dynamic-programming seam crosses the north-west meadow and
    becomes the east-registered native riverbank by the south edge of the
    replacement area. It never enters the road at x466 or the bridge.
    """
    h = 405
    lo, hi = 535, 815
    lab_a = cv2.cvtColor(west[:h], cv2.COLOR_RGB2LAB).astype(np.float32)
    lab_b = cv2.cvtColor(east[:h], cv2.COLOR_RGB2LAB).astype(np.float32)
    # A photometric mismatch alone favors smooth empty grass; edge energy
    # penalizes cutting a visible tree trunk, rock face or riverbank.
    color = np.mean(np.abs(lab_a-lab_b), axis=2)
    gray_a = cv2.cvtColor(west[:h], cv2.COLOR_RGB2GRAY)
    gray_b = cv2.cvtColor(east[:h], cv2.COLOR_RGB2GRAY)
    ga = cv2.magnitude(cv2.Sobel(gray_a, cv2.CV_32F, 1, 0),
                       cv2.Sobel(gray_a, cv2.CV_32F, 0, 1))
    gb = cv2.magnitude(cv2.Sobel(gray_b, cv2.CV_32F, 1, 0),
                       cv2.Sobel(gray_b, cv2.CV_32F, 0, 1))
    water = river_mask(west[:h]) | river_mask(east[:h])
    energy = cv2.GaussianBlur(color, (5, 5), 0) + 0.045*(ga+gb) + water*250.0
    xs = np.arange(lo, hi+1)
    dp = np.full((h, len(xs)), np.inf, dtype=np.float64)
    parent = np.zeros((h, len(xs)), dtype=np.int16)
    for y in range(h):
        # Follow the landward bank eastwards as the original river curves.
        center = 594 + 0.30*y
        valid = np.abs(xs-center) <= 55
        row = energy[y, lo:hi+1].astype(np.float64)
        row[~valid] += 2500
        if y == 0:
            dp[y] = row + 0.12*(xs-center)**2
            continue
        for step in (-3, -2, -1, 0, 1, 2, 3):
            previous = np.arange(len(xs))-step
            valid_previous = (previous >= 0) & (previous < len(xs))
            inds = np.where(valid_previous)[0]
            value = dp[y-1, previous[inds]] + 1.6*abs(step)
            replace = value < dp[y, inds]
            dp[y, inds[replace]] = value[replace]
            parent[y, inds[replace]] = previous[inds[replace]]
        dp[y] += row
    result = np.zeros(h, dtype=np.float32)
    pos = int(np.argmin(dp[-1]))
    for y in range(h-1, -1, -1):
        result[y] = xs[pos]
        pos = int(parent[y, pos])
    assert 530 <= result.min() and result.max() <= 815
    return result

def build(west, east):
    assert west.shape == east.shape == (H, W, 3)
    seam = find_photo_seam(west, east)
    out = east.copy()
    # Left native meadow and undistorted trees; right registered gorge.
    # A narrow 8px blend follows the photographed graph-cut seam; never
    # stretch or move a tree, road or bridge pixel.
    xx = np.arange(W, dtype=np.float32)[None, :]
    yy = np.arange(405, dtype=np.float32)[:, None]
    left = 1.0-smooth((xx-seam[:, None]+4.0)/8.0)
    # End the west-source replacement through an irregular alpine meadow
    # transition rather than a horizontal strip or rectangular patch.
    bottom = 310 + 22*np.sin(xx/47) + 13*np.sin(xx/97)
    fade = smooth((bottom-yy)/48.0)
    mask = left*fade
    out[:405] = np.uint8(np.clip(
        west[:405].astype(np.float32)*mask[:, :, None] +
        east[:405].astype(np.float32)*(1-mask[:, :, None]), 0, 255))
    assert np.array_equal(out[405:], east[405:])
    assert np.array_equal(out[:170, :490], west[:170, :490])
    assert np.array_equal(out[:250, 930:], east[:250, 930:])
    return out, seam


def reconstruct_riverbank_contact(south, html):
    """Continue the *unseen* native Matrei photograph into SOUTH at the seam.

    V121's painted renderer crops the Matrei source before its bottom 80 px.
    This reconstructs the next ~48 pixels of that SAME original photograph
    using the exact V121 crop coordinates, then finds an irregular, low-impact
    photographic cut back to the intact SOUTH meadow, cartway and river.
    Unlike the former high-frequency-only transfer, this transfers coherent
    native rocks, water, tree crowns and meadow structure at their natural
    scale. No tree is stretched, reflected, painted or cloned. No V121 pixel
    or V123 node changes. The result is fictional prototype landscape art.
    """
    import base64
    from io import BytesIO
    m = re.search(r'ART_MATREI_CANONICAL="([^"]+)"', html)
    if not m or 'base64,' not in m.group(1):
        raise ValueError('Canonical V121 Matrei art not found')
    raw = base64.b64decode(m.group(1).split('base64,', 1)[1])
    with Image.open(BytesIO(raw)) as photo:
        matrei = np.asarray(photo.convert('RGB'))
    if matrei.shape != (H, W, 3):
        raise ValueError(f'Unexpected Matrei art dimensions: {matrei.shape}')

    # Match the existing Matrei renderer's photographic source registration,
    # *extrapolating* only into source rows not yet displayed by V121.
    # The gold frame occupies the source's last ~35 rows: never sample it.
    height = 160
    yy, xx = np.mgrid[:height, :W].astype(np.float32)
    display_y = 1024.0 + yy
    easing = smooth((display_y-845.0)/179.0)
    source_y = 10.0 + display_y*(953.0/H) - 26.0*easing
    source_left = np.where(
        source_y < 286, 385-(source_y-10)*(295/276),
        np.where(source_y > 674, 90+(source_y-674)*(295/289), 90))
    left = np.where(display_y < 256, 256-display_y,
                    np.where(display_y > 768, display_y-768, 0))
    right = W-left
    bow = smooth((display_y-700)/324)
    source_x = np.clip(
        source_left + (xx-left)*(W-2*source_left)/(right-left)
        - 55*bow*np.exp(-.5*((xx-466)/105)**2), 0, W-1.001)
    source_y += (26*np.exp(-.5*((xx-240)/400)**2)
                 *np.exp(-.5*((display_y-505)/110)**2))
    # No reflecting / stretching / inventing pixels beyond the original art.
    valid_y = source_y < 986
    native_extension = cv2.remap(
        matrei, source_x.astype(np.float32),
        np.clip(source_y, 0, 985).astype(np.float32),
        cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)

    # Find a low-visibility non-horizontal photographic join. The road has a
    # shorter continuation so its actual SOUTH cartway remains undisturbed;
    # the river and limestone bank receive a deeper native-photo apron.
    band_lo, band_hi = 12, 46
    lab_a = cv2.cvtColor(native_extension[:height], cv2.COLOR_RGB2LAB)
    lab_b = cv2.cvtColor(south[:height], cv2.COLOR_RGB2LAB)
    mismatch = np.mean(np.abs(lab_a.astype(np.float32)
                              - lab_b.astype(np.float32)), axis=2)
    ga = cv2.cvtColor(native_extension[:height], cv2.COLOR_RGB2GRAY)
    gb = cv2.cvtColor(south[:height], cv2.COLOR_RGB2GRAY)
    grad_a = cv2.magnitude(cv2.Sobel(ga,cv2.CV_32F,1,0),
                           cv2.Sobel(ga,cv2.CV_32F,0,1))
    grad_b = cv2.magnitude(cv2.Sobel(gb,cv2.CV_32F,1,0),
                           cv2.Sobel(gb,cv2.CV_32F,0,1))
    energy = cv2.GaussianBlur(mismatch, (5,5), 0) + .035*(grad_a+grad_b)
    river_a = river_mask(native_extension[:height])
    river_b = river_mask(south[:height])
    energy += np.logical_xor(river_a,river_b)*45.0
    candidates = np.arange(band_lo,band_hi+1)
    xmin,xmax = 240,1320
    dp = np.full((len(candidates),xmax-xmin),np.inf,dtype=np.float64)
    parent = np.zeros_like(dp,dtype=np.int16)
    for ix,x in enumerate(range(xmin,xmax)):
        desired = 17 if 415<=x<=525 else (38 if 780<=x<=1190 else 30)
        penalty = .10*(candidates-desired)**2
        penalty = penalty + np.where(valid_y[candidates,x],0,10000)
        cost = energy[candidates,x]+penalty
        if ix == 0:
            dp[:,ix] = cost
            continue
        for step in (-2,-1,0,1,2):
            prev = np.arange(len(candidates))-step
            ok = (prev>=0)&(prev<len(candidates))
            inds = np.where(ok)[0]
            v = dp[prev[inds],ix-1]+2.0*abs(step)
            better = v<dp[inds,ix]
            dp[inds[better],ix] = v[better]
            parent[inds[better],ix] = prev[inds[better]]
        dp[:,ix] += cost
    seam = np.zeros(W,dtype=np.float32)
    pos = int(np.argmin(dp[:,-1]))
    for ix in range(xmax-xmin-1,-1,-1):
        seam[xmin+ix] = candidates[pos]
        pos = int(parent[pos,ix])
    seam[:xmin] = seam[xmin]
    seam[xmax:] = seam[xmax-1]
    seam = cv2.GaussianBlur(seam[None,:],(0,0),6)[0]
    # The natural-source edge is opaque at y=0 and cuts back to native SOUTH
    # through a narrow, irregular meadow / bank join. No digital road stripe.
    feather = 6.0
    photo_alpha = smooth((seam[None,:]-yy+feather/2)/feather)
    photo_alpha *= smooth((xx-235)/72)*smooth((1315-xx)/72)
    photo_alpha *= valid_y.astype(np.float32)
    # Multiband blend: retain full native rock/water/tree detail above the cut
    # while matching broad photographic lighting across the join.
    source = south[:height].copy()
    source[:height] = np.where(valid_y[:,:,None],native_extension,source)
    A = source.astype(np.float32)
    B = south[:height].astype(np.float32)
    mask = photo_alpha.astype(np.float32)
    levels = 4
    gauss_a=[A];gauss_b=[B];gauss_m=[mask]
    for _ in range(levels):
        gauss_a.append(cv2.pyrDown(gauss_a[-1]))
        gauss_b.append(cv2.pyrDown(gauss_b[-1]))
        gauss_m.append(cv2.pyrDown(gauss_m[-1]))
    result = (gauss_a[-1]*gauss_m[-1][:,:,None] +
              gauss_b[-1]*(1-gauss_m[-1][:,:,None]))
    for level in range(levels-1,-1,-1):
        size=(gauss_a[level].shape[1],gauss_a[level].shape[0])
        la=gauss_a[level]-cv2.pyrUp(gauss_a[level+1],dstsize=size)
        lb=gauss_b[level]-cv2.pyrUp(gauss_b[level+1],dstsize=size)
        m=gauss_m[level][:,:,None]
        result=cv2.pyrUp(result,dstsize=size)+la*m+lb*(1-m)
    out=south.copy()
    out[:height]=np.uint8(np.clip(result,0,255))
    # Pyramid filters extend slightly outside the mask. Restore the fully
    # clipped exterior, which is not part of either playable octagon.
    out[:height,:215]=south[:height,:215]
    out[:height,1340:]=south[:height,1340:]
    assert np.array_equal(out[height:],south[height:])
    assert np.array_equal(out[:, :215],south[:, :215])
    assert np.array_equal(out[:, 1340:],south[:, 1340:])
    return out,int(np.count_nonzero(photo_alpha>.08))

def main():
    html = HTML.read_text(encoding='utf-8')
    matrei = re.search(r'ART_MATREI_CANONICAL="([^"]+)"', html)
    west_road = re.search(r'const westRoad=([^;]+);', html)
    south_road = re.search(r'const southRoad=([^;]+);', html)
    assert matrei and west_road and south_road
    assert '[1536,478]' in west_road.group(1)
    assert '[466,0]' in south_road.group(1)
    assert 'south-forest-river-continuity-unapproved.webp' in html
    with Image.open(WEST_SOURCE) as f:
        west = np.asarray(f.convert('RGB'))
    with Image.open(RIVER_SOURCE) as f:
        river = np.asarray(f.convert('RGB'))
    result, seam = build(west, river)
    result, contact_pixels = reconstruct_riverbank_contact(result, html)
    assert contact_pixels > 5000, f'Riverbank contact too small: {contact_pixels}'
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(result).save(OUTPUT, 'WEBP', quality=91, method=6)
    # No HTML, V121, graph, game engine, campaign, sprite or save edits.
    assert html == HTML.read_text(encoding='utf-8')
    changed = np.mean(np.abs(result[:340].astype(np.int16)-river[:340].astype(np.int16)))
    assert changed > 1.0, 'No substantive photographic source replacement'
    REPORT.write_text(
        '# SOUTH original-photo meadow and riverbank reconstruction — UNAPPROVED\n\n'
        'Fictional Alpine atlas art, not historically verified topography.\n\n'
        'Restored the natural, undistorted upper-west SOUTH meadow, road and '
        'conifers from the original 1536x1024 stone-bridge artwork while '
        'retaining the separately registered eastern gorge/river and its '
        'original stone bridge. A photographic low-energy graph-cut seam '
        'runs through meadow pixels rather than trees or water. The '
        'replacement ends on an irregular ground boundary. A second '
        'source-native contact reconstructs the river mouth using only '
        'native, previously cropped Matrei landscape pixels across the shared bank, while '
        'retaining SOUTH-native river shapes, forests, roads and cliffs. '
        'No gold frame, invented settlements, mirrored trees or synthetic road are copied. Neither '
        'source photograph is globally warped, scaled, mirrored or '
        'painted with a synthetic cartway. The V123 x466 cartway and '
        'the original bridge stay in place.\n\n'
        f'Seam x range: {int(seam.min())}..{int(seam.max())}; '
        f'native seam-continuation pixels: {contact_pixels}; '
        f'northern-region mean RGB change: {changed:.2f}.\n\n'
        'Still an OPT-IN ?southArt=river review candidate. The Matrei/SOUTH '
        'rock and river morphology requires eyes-on iPhone inspection; '
        'numerical alignment does not establish artistic acceptance. '
        'V121 source, V123 100-node graph, V94, sprites, saves and '
        'production unchanged. Production RED.\n\n'
        'WEST source SHA256: '+hashlib.sha256(WEST_SOURCE.read_bytes()).hexdigest()+'\n'
        'RIVER source SHA256: '+hashlib.sha256(RIVER_SOURCE.read_bytes()).hexdigest()+'\n'
        'Output SHA256: '+hashlib.sha256(OUTPUT.read_bytes()).hexdigest()+'\n',
        encoding='utf-8')
    print('Original photographic SOUTH riverbank contact rebuilt:', OUTPUT,
          OUTPUT.stat().st_size, 'bytes; seam', seam.min(), seam.max(),
          'mean RGB change', round(float(changed),2),
          'native contact pixels', contact_pixels)

if __name__ == '__main__':
    main()

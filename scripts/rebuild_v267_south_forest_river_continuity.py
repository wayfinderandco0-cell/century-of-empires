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
    """Extend native Matrei WATER/ROCK MATERIAL into the SOUTH river mouth.

    Copy only water and exposed stone, NEVER whole Matrei scenery, tree
    crowns, roads, or framed borders. An irregular source-aware mask makes
    the riverbank transition a physical terrain feature, not a digital stripe.
    The native SOUTH river, bridge, cartway, and forests remain fixed.
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

    # Sample a native 180px lower-Matrei riverbank strip. The V121 frame
    # itself occupies the extreme bottom: never sample its final 35 rows.
    top, height = H-215, 180
    bank = matrei[top:top+height].copy()
    hsv = cv2.cvtColor(bank, cv2.COLOR_RGB2HSV)
    water = ((hsv[:,:,0]>=79) & (hsv[:,:,0]<=126) &
             (hsv[:,:,1]>=36) & (hsv[:,:,2]>=54))
    stone = ((hsv[:,:,1]<75) & (hsv[:,:,2]>72) &
             (hsv[:,:,2]<227))
    # Forest, tan roads, buildings and gold frame must not be transplanted.
    forest = ((hsv[:,:,0]>=28) & (hsv[:,:,0]<=85) &
              (hsv[:,:,1]>=37))
    gold = ((hsv[:,:,0]>=10) & (hsv[:,:,0]<=37) &
            (hsv[:,:,1]>=75))
    material = (water | stone) & ~forest & ~gold
    material = np.uint8(material)*255
    material = cv2.morphologyEx(material, cv2.MORPH_CLOSE,
                                np.ones((9,9),np.uint8))
    # The river exits Matrei around x949, not the x466 SOUTH cartway.
    # Preserve all original pixels outside the riverbank contact zone.
    yy,xx = np.mgrid[:height,:W].astype(np.float32)
    landward = np.clip((xx-710)/75,0,1)*np.clip((1290-xx)/75,0,1)
    # Feather out gradually into SOUTH's existing river, not a horizontal
    # cut at the foot of the contact. No resampling of trees or cliffs.
    depth = np.clip((height-yy)/height,0,1)**1.6
    mat = cv2.GaussianBlur(material.astype(np.float32)/255,
                          (0,0),8)
    alpha = np.clip(mat*landward*depth*.86,0,.86)
    # Multiscale photographic material transfer keeps native bank shadows
    # while maintaining the SOUTH river's underlying structure.
    result = south.copy()
    original = south[:height].astype(np.float32)
    source = bank.astype(np.float32)
    # Transfer source texture/structure without an overall color-grade.
    # Low-frequency color stays SOUTH-native; only actual water/rock detail
    # from the adjoining Matrei material crosses the frame.
    src_low = cv2.GaussianBlur(source,(0,0),16)
    dst_low = cv2.GaussianBlur(original,(0,0),16)
    material_detail = source-src_low
    transferred = np.clip(dst_low + material_detail*.78 +
                          (original-dst_low)*.35,0,255)
    result[:height] = np.uint8(np.clip(
        original*(1-alpha[:,:,None]) +
        transferred*alpha[:,:,None],0,255))
    # No trees or road outside the east bank, and no broad SOUTH warp.
    assert np.array_equal(result[:, :710],south[:, :710])
    assert np.array_equal(result[height:],south[height:])
    return result, int(np.count_nonzero(alpha>.08))

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
        'stone and water detail from the immutable Matrei photo, while '
        'retaining SOUTH-native river shapes, forests, roads and cliffs. '
        'No Matrei trees, settlements, road or gold frame are copied. Neither '
        'source photograph is globally warped, scaled, mirrored or '
        'painted with a synthetic cartway. The V123 x466 cartway and '
        'the original bridge stay in place.\n\n'
        f'Seam x range: {int(seam.min())}..{int(seam.max())}; '
        f'native riverbank material pixels: {contact_pixels}; '
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

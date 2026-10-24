#!/usr/bin/env python3
"""Diagnostic Matrei photo-island texture boundary on V161 iPhone screenshots.

Read-only, source-pinned. This measures local high-frequency texture on both
sides of the ORIGINAL V121 photo polygon, not overall West/South quality.
It cannot approve art, georegistration, historical roads or bridge banks.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
from PIL import Image

POLYGON = ((386, 6), (1150, 6), (1444, 283), (1444, 675),
           (1150, 968), (386, 968), (91, 675), (91, 283))
ORIGIN = (1536, 0)
FOCUS = (2350, 530)
VIEWPORTS = {'portrait': (390, 844), 'landscape': (844, 390)}
ENGINES = ('chromium', 'webkit')
OFFSET_WORLD = 82
RADIUS_SCREEN_PX = 9
V161_HTML_BLOB = 'c33ab29b41f4b2a2864ddad368807bdf1938f467'

def verify_preview(root):
    """Reject changed V161 camera, photo mask, or renderer assumptions."""
    raw = (root / 'v161-native-material-study.html').read_bytes()
    git_blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
    if git_blob != V161_HTML_BLOB:
        raise ValueError('V161 source changed; re-register Matrei seam sampling')
    src = raw.decode('utf8')
    for marker in (
        'const poly=[[386,6],[1150,6],[1444,283],[1444,675],[1150,968],[386,968],[91,675],[91,283]]',
        'matrei:[2350,530]',
        'cam=centers[name].slice();zoom=2.4;redraw()',
        'base=Math.min(width/3200,height/2450)',
        'if(centerPhoto)cx.drawImage(centerPhoto,1536,0,W,H)'
    ):
        if marker not in src:
            raise ValueError('V161 Matrei geometry/camera contract changed: ' + marker)
    return git_blob

def local_texture(im, x, y, radius=RADIUS_SCREEN_PX):
    """One-pixel luminance gradient, identical screen-space windows."""
    x, y = int(round(x)), int(round(y))
    if x-radius < 0 or y-radius < 0 or x+radius+1 >= im.width or y+radius+1 >= im.height:
        return None
    p = im.load()
    def lum(a, b):
        r, g, blue = p[a, b][:3]
        return .2126*r + .7152*g + .0722*blue
    total = 0.0
    count = 0
    for yy in range(y-radius, y+radius, 2):
        for xx in range(x-radius, x+radius, 2):
            v = lum(xx, yy)
            total += abs(v-lum(xx+1, yy)) + abs(v-lum(xx, yy+1))
            count += 2
    return total/count

def sample_image(im, orientation, *, crop_hud=True):
    w, h = VIEWPORTS[orientation]
    # V161 focusTile('matrei'): cam=[2350,530], zoom=2.4.
    scale = min(w/3200, h/2450)*2.4
    dprx, dpry = im.width/w, im.height/h
    if abs(dprx-dpry) > .001 or abs(dprx-2) > .001:
        raise ValueError('Unexpected phone screenshot pixel ratio')
    def project(point):
        return ((w/2+(point[0]-FOCUS[0])*scale)*dprx,
                (h/2+(point[1]-FOCUS[1])*scale)*dpry)
    samples = []
    for edge in range(len(POLYGON)):
        ax, ay = POLYGON[edge]
        bx, by = POLYGON[(edge+1) % len(POLYGON)]
        dx, dy = bx-ax, by-ay
        length = math.hypot(dx, dy)
        inward = (-dy/length, dx/length)
        for fraction in (.25, .5, .75):
            cx = ORIGIN[0]+ax+fraction*dx
            cy = ORIGIN[1]+ay+fraction*dy
            inside = project((cx+OFFSET_WORLD*inward[0], cy+OFFSET_WORLD*inward[1]))
            outside = project((cx-OFFSET_WORLD*inward[0], cy-OFFSET_WORLD*inward[1]))
            if crop_hud:
                # Exclude header and footer overlays, which bias photo metrics.
                safe = (65*dprx, (h-125)*dpry) if orientation == 'portrait' else (45*dprx, (h-85)*dpry)
                if not all(safe[0] < pt[1] < safe[1] for pt in (inside, outside)):
                    continue
            a = local_texture(im, *inside)
            b = local_texture(im, *outside)
            if a is None or b is None:
                continue
            samples.append({'edge': edge, 'fraction': fraction,
                            'insideGradient': round(a, 4),
                            'outsideGradient': round(b, 4),
                            'outsideToInside': round(b/max(.001, a), 4)})
    return samples

def audit(folder):
    results = {}
    for engine in ENGINES:
        for orientation in VIEWPORTS:
            key = f'{engine}-{orientation}'
            path = folder / f'{key}-matrei-terrain.png'
            if not path.is_file():
                raise FileNotFoundError('Missing real Matrei phone screenshot: ' + str(path))
            with Image.open(path) as im:
                samples = sample_image(im.convert('RGB'), orientation)
            if len(samples) < 2:
                raise ValueError('Insufficient unobscured Matrei polygon samples: ' + key)
            inside = sum(s['insideGradient'] for s in samples)/len(samples)
            outside = sum(s['outsideGradient'] for s in samples)/len(samples)
            results[key] = {'samples': samples, 'sampleCount': len(samples),
                            'meanInsideGradient': round(inside, 4),
                            'meanOutsideGradient': round(outside, 4),
                            'meanOutsideToInside': round(outside/max(.001, inside), 4)}
    return {'version': 162,
            'source': 'V161 four-browser Matrei-focused phone screenshots',
            'photoPolygon': 'unchanged V121/V161 eight-edge local coordinates',
            'measure': 'local texture contrast across photo mask; diagnostic, NOT art approval',
            'configurations': results, 'productionApproved': False,
            'photoSeamApproved': False, 'gameToGeographyRegistered': False,
            'bridgeBanksVerified': False, 'historicalRoadsVerified': False,
            'next': 'Author reviewed high-resolution neighboring GAME-frame art; compare actual phone images.'}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--screenshots', type=Path, required=True)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    verify_preview(Path(__file__).resolve().parents[1])
    report = audit(args.screenshots)
    target = args.output or args.screenshots / 'v162-photo-boundary-report.json'
    target.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: {'sampleCount': v['sampleCount'],
                          'meanOutsideToInside': v['meanOutsideToInside']}
                      for k, v in report['configurations'].items()}, indent=2))

if __name__ == '__main__':
    main()

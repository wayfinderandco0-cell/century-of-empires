#!/usr/bin/env python3
"""Fail-closed V171 image-detail gate for V170 three-octagon phone captures.

Use V140's unchanged floors; passing a numeric test is not art approval.
"""
import argparse
import json
from pathlib import Path
from PIL import Image

ENGINES = ('chromium', 'webkit')
ORIENTATIONS = ('portrait', 'landscape')
REGIONS = ('matrei', 'west', 'south')
MIN_RELATIVE_GRADIENT = .35
MIN_RELATIVE_STRONG_EDGES = .25
STRONG_EDGE_LUMA = 12.

def detail_score(image):
    im = image.convert('RGB')
    width, height = im.size
    x0, x1 = int(width * .22), int(width * .80)
    y0, y1 = int(height * .22), int(height * .78)
    if x1-x0 < 8 or y1-y0 < 8:
        raise ValueError('Screenshot too small for visual detail audit')
    pixels = im.load()
    def luma(x, y):
        r, g, b = pixels[x, y]
        return .2126*r + .7152*g + .0722*b
    count = 0
    total = 0.
    strong = 0
    for y in range(y0, y1-1, 2):
        for x in range(x0, x1-1, 2):
            c = luma(x, y)
            for d in (abs(c-luma(x+1,y)), abs(c-luma(x,y+1))):
                total += d
                strong += d >= STRONG_EDGE_LUMA
                count += 1
    return {'mean_luma_gradient': round(total/count, 4),
            'strong_edge_fraction': round(strong/count, 5),
            'samples': count}

def assess(scores):
    reference = scores['matrei']
    checks = {}
    for region in ('west', 'south'):
        candidate = scores[region]
        g = candidate['mean_luma_gradient']/max(.001, reference['mean_luma_gradient'])
        e = candidate['strong_edge_fraction']/max(.00001, reference['strong_edge_fraction'])
        checks[region] = {'relative_gradient': round(g, 4),
                          'relative_strong_edges': round(e, 4),
                          'passes_minimum_detail': g >= MIN_RELATIVE_GRADIENT and e >= MIN_RELATIVE_STRONG_EDGES}
    return checks

def audit(folder):
    results, missing = {}, []
    for engine in ENGINES:
        for orientation in ORIENTATIONS:
            prefix = f'{engine}-{orientation}'
            scores = {}
            for region in REGIONS:
                name = 'opening' if region == 'matrei' else f'{region}-terrain'
                path = folder / f'{prefix}-{name}.png'
                if not path.is_file():
                    missing.append(str(path))
                    continue
                with Image.open(path) as im:
                    scores[region] = detail_score(im)
            if len(scores) == 3:
                checks = assess(scores)
                results[prefix] = {'scores': scores, 'neighbors': checks,
                                   'detail_gate_pass': all(x['passes_minimum_detail'] for x in checks.values())}
    return {'passed': not missing and len(results)==4 and all(x['detail_gate_pass'] for x in results.values()),
            'screenshots_missing': missing,
            'relative_gradient_floor': MIN_RELATIVE_GRADIENT,
            'relative_strong_edges_floor': MIN_RELATIVE_STRONG_EDGES,
            'results': results,
            'productionApproved': False, 'physicalIPhoneApproved': False,
            'v123RoadsGeoregistered': False,
            'note': 'Synthetic noise can pass this necessary image gate; no numerical score certifies geography, art or history.'}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--screenshots', type=Path, required=True)
    parser.add_argument('--enforce', action='store_true')
    args = parser.parse_args()
    result = audit(args.screenshots)
    args.screenshots.mkdir(parents=True, exist_ok=True)
    (args.screenshots/'v171-detail-audit.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))
    if args.enforce and not result['passed']:
        raise SystemExit('V171 art gate REJECTED: V170 neighbor terrain is not at Matrei image-detail parity')

if __name__ == '__main__':
    main()

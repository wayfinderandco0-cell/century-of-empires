#!/usr/bin/env python3
"""V127: measure original painted road pixels without movement overlays.

Low contrast is a manual-review cue, not proof of a broken road. High contrast
does NOT certify alignment, bridge safety, historical roads, or production use.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
from statistics import median
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent


def valid_point(p):
    return (isinstance(p, (list, tuple)) and len(p) == 2
            and all(isinstance(v, (int, float)) and not isinstance(v, bool)
                    and math.isfinite(v) for v in p))


def sample_polyline(points, spacing=12.0):
    if not isinstance(points, list) or len(points) < 2 or not all(map(valid_point, points)):
        raise ValueError('Polyline needs at least two finite [x,y] points')
    if not math.isfinite(spacing) or spacing <= 0:
        raise ValueError('Bad sampling spacing')
    distance = 0.0
    for a, b in zip(points, points[1:]):
        dx, dy = b[0]-a[0], b[1]-a[1]
        length = math.hypot(dx, dy)
        if length < 1e-9:
            raise ValueError('Duplicate route control point')
        count = max(1, math.ceil(length / spacing))
        for i in range(count):
            t = (i + 0.5) / count
            yield {'point': (a[0]+t*dx, a[1]+t*dy),
                   'tangent': (dx/length, dy/length),
                   'arc': distance+t*length}
        distance += length


def median_rgb(image, x, y, nx, ny, offsets):
    w, h = image.size
    pixels = []
    for d in offsets:
        xx, yy = round(x+nx*d), round(y+ny*d)
        if not (0 <= xx < w and 0 <= yy < h):
            return None
        pixels.append(image.getpixel((xx, yy))[:3])
    return tuple(median(v[k] for v in pixels) for k in range(3))


def color_distance(a, b):
    return math.sqrt(sum((x-y)**2 for x, y in zip(a, b)))


def evaluate_sample(image, sample, side_offset=20):
    x, y = sample['point']
    tx, ty = sample['tangent']
    nx, ny = -ty, tx
    center = median_rgb(image, x, y, nx, ny, (-2, 0, 2))
    left = median_rgb(image, x, y, nx, ny, (-side_offset-2, -side_offset, -side_offset+2))
    right = median_rgb(image, x, y, nx, ny, (side_offset-2, side_offset, side_offset+2))
    if center is None or left is None or right is None:
        return None
    dl, dr = color_distance(center, left), color_distance(center, right)
    return {'point': [round(x, 2), round(y, 2)],
            'arc': round(sample['arc'], 2),
            'leftRgbDelta': round(dl, 2), 'rightRgbDelta': round(dr, 2),
            'minRgbDelta': round(min(dl, dr), 2)}


def weak_spans(samples, threshold=16.0, min_span_px=30.0):
    spans, group = [], []
    def flush():
        if group and group[-1]['arc']-group[0]['arc'] >= min_span_px:
            spans.append({'start': group[0]['point'], 'end': group[-1]['point'],
                          'startArcPx': group[0]['arc'], 'endArcPx': group[-1]['arc'],
                          'samples': len(group),
                          'medianMinRgbDelta': round(median(s['minRgbDelta'] for s in group), 2)})
        group.clear()
    for s in samples:
        if s['minRgbDelta'] < threshold:
            group.append(s)
        else:
            flush()
    flush()
    return spans


def audit(image, manifest, spacing=12.0, side_offset=20, threshold=16.0):
    if image.size != (manifest['dimensions']['width'], manifest['dimensions']['height']):
        raise ValueError('Painting dimensions differ from pinned V121 manifest')
    results = {}
    roads = manifest['movement']['roads']
    for name, points in roads.items():
        candidates = list(sample_polyline(points, spacing))
        observations = [evaluate_sample(image, p, side_offset) for p in candidates]
        valid = [v for v in observations if v is not None]
        results[name] = {
            'candidateControlPoints': len(points),
            'sampled': len(valid), 'outOfImageSamples': len(observations)-len(valid),
            'medianMinRgbDelta': round(median(v['minRgbDelta'] for v in valid), 2) if valid else None,
            'weakContrastSamples': sum(v['minRgbDelta'] < threshold for v in valid),
            'weakContrastSpans': weak_spans(valid, threshold),
        }
    bridge = manifest['movement']['primaryStoneBridgeEnds']
    route = roads['bridge']
    start, end = route.index(bridge[0]), route.index(bridge[1])
    if not 0 < start < end < len(route)-1:
        raise ValueError('Bridge control points do not have both approaches')
    return {
        'version': 127, 'sourceArt': manifest['art']['path'],
        'roadGeometry': 'candidate coordinates only; not independently approved',
        'measurement': {'spacingPx': spacing, 'sideOffsetPx': side_offset,
                        'weakContrastThresholdRgb': threshold,
                        'method': 'median RGB of source-image centerline vs both perpendicular sides'},
        'bridge': {'ends': bridge, 'candidateBridgeSegments': end-start,
                   'approachesPresentInGraph': True, 'riverCrossingVerified': False},
        'roads': results,
        'historicalAccuracyVerified': False, 'pixelAlignmentVerified': False,
        'neighborContinuationVerified': False, 'productionEnabled': False,
        'interpretation': 'Weak contrast needs manual visual review; strong contrast is not road proof.'
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path, default=ROOT/'terrain-grid/octagon-1-v121.manifest.json')
    parser.add_argument('--image', type=Path)
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text())
    image_path = args.image or ROOT/manifest['art']['path']
    with Image.open(image_path) as raw:
        result = audit(raw.convert('RGB'), manifest)
    output = json.dumps(result, indent=2)+'\n'
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(output)
    print(output)


if __name__ == '__main__':
    main()

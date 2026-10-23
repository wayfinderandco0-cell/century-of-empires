#!/usr/bin/env python3
"""V128: rank source-art cross-sections for human review; never certify roads."""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
from PIL import Image
import audit_v127_road_pixels as previous

ROOT = Path(__file__).resolve().parent.parent
OFFSETS = (-24, -16, -8, 0, 8, 16, 24)


def cross_section(image, sample):
    x, y = sample['point']
    tx, ty = sample['tangent']
    nx, ny = -ty, tx
    colors = [previous.median_rgb(image, x, y, nx, ny, (d-1, d, d+1)) for d in OFFSETS]
    if any(c is None for c in colors):
        return None
    center = colors[OFFSETS.index(0)]
    return [{'offsetPx': d, 'rgb': [round(v, 2) for v in c],
             'rgbDeltaFromCenter': round(previous.color_distance(c, center), 2)}
            for d, c in zip(OFFSETS, colors)]


def rank_route(image, name, points, bridge_ends, spacing=12.0, limit=8):
    if not isinstance(limit, int) or isinstance(limit, bool) or limit < 1:
        raise ValueError('limit must be a positive integer')
    samples = list(previous.sample_polyline(points, spacing))
    length = sum(math.dist(a, b) for a, b in zip(points, points[1:]))
    ranked = []
    for sample in samples:
        observed = previous.evaluate_sample(image, sample)
        if observed is None:
            continue
        x, y = sample['point']
        reasons = []
        if observed['minRgbDelta'] < 16:
            reasons.append('weak_center_vs_flank_contrast')
        if name == 'bridge' and min(math.dist((x, y), p) for p in bridge_ends) <= 72:
            reasons.append('bridge_approach_review')
        if name == 'west' and sample['arc'] <= 96:
            reasons.append('unverified_west_termination')
        if name == 'south' and length - sample['arc'] <= 96:
            reasons.append('unverified_south_termination')
        if not reasons:
            continue
        profile = cross_section(image, sample)
        if profile is None:
            continue
        score = (100 if 'weak_center_vs_flank_contrast' in reasons else 0) + (80 if len(reasons) > 1 or reasons[0] != 'weak_center_vs_flank_contrast' else 0)
        ranked.append({'road': name, 'point': observed['point'], 'arcPx': observed['arc'],
                       'minRgbDelta': observed['minRgbDelta'], 'priorityScore': score,
                       'reviewReasons': reasons, 'crossSection': profile})
    # Prefer highest-priority positions; avoid redundant adjacent 12px samples.
    ranked.sort(key=lambda p: (-p['priorityScore'], p['minRgbDelta'], p['arcPx']))
    selected = []
    for candidate in ranked:
        if all(abs(candidate['arcPx'] - p['arcPx']) >= 24 for p in selected):
            selected.append(candidate)
        if len(selected) >= limit:
            break
    return sorted(selected, key=lambda p: p['arcPx'])


def audit(image, manifest):
    baseline = previous.audit(image, manifest)
    bridge_ends = manifest['movement']['primaryStoneBridgeEnds']
    reviews = {name: rank_route(image, name, points, bridge_ends)
               for name, points in manifest['movement']['roads'].items()}
    return {'version': 128, 'sourceArt': baseline['sourceArt'],
            'baselineV127': baseline, 'reviewProfiles': reviews,
            'crossSectionOffsetsPx': list(OFFSETS),
            'reviewPointCount': sum(len(v) for v in reviews.values()),
            'selection': 'contrast below 16 RGB, bridge approaches within 72px, west/south terminal within 96px; max 8 separated review points per route',
            'roadSurfaceClassified': False, 'historicalAccuracyVerified': False,
            'pixelAlignmentVerified': False, 'bridgeCrossingVerified': False,
            'neighborContinuationVerified': False, 'productionEnabled': False,
            'interpretation': 'Cross-sections are review coordinates only, not road/bridge approval.'}


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
    output = json.dumps(result, indent=2) + '\n'
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(output)
    print(output)


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""V244 isolated whole-landscape physical-cartway registration experiment.

Move EXISTING road pixels and the neighboring landscape together; do not
paint a new stripe over unrelated terrain. Source road must be independently
traced on source imagery. Immutable V123 is loaded and Git-blob-pinned.
No historical road, geographic tiepoint, license, bank or visual approval.
"""
import argparse
import hashlib
import json
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageDraw

SIZE = (1536, 1024)
MAX_DISPLACEMENT = 165.0
MAX_LOCAL_SLOPE = .70
MIN_COVERAGE = .998

def validate_route(route, label):
    if len(route) < 3 or any(len(p) != 2 for p in route):
        raise ValueError(label + ': at least three 2D points required')
    p = np.asarray(route, dtype=float)
    if (not np.isfinite(p).all() or np.any(p[:, 0] < 0) or
            np.any(p[:, 0] > 1536) or np.any(p[:, 1] < 0) or
            np.any(p[:, 1] > 1024)):
        raise ValueError(label + ': invalid coordinates')
    if not np.all(np.diff(p[:, 0]) > 0):
        raise ValueError(label + ': x coordinates must be strictly increasing')
    return p

def register(source, source_trace, target_trace, sigma=145,
             max_displacement=MAX_DISPLACEMENT):
    """Return whole-scene remap and fail-closed necessary-only measurements.

    This monotone-x transform is appropriate for WEST only when it meets
    deformation limits. SOUTH's vertical northern approach cannot be mapped
    by this method; it must reject rather than silently invent a continuation.
    """
    if source.size != SIZE:
        raise ValueError('native image must be 1536x1024')
    src = validate_route(source_trace, 'independent source-road annotation')
    dst = validate_route(target_trace, 'immutable V123 road')
    if src[0, 0] > dst[0, 0] or src[-1, 0] < dst[-1, 0]:
        raise ValueError('source road does not cover immutable route x span')
    x = np.arange(SIZE[0], dtype=np.float32)
    src_y = np.interp(x, src[:, 0], src[:, 1]).astype(np.float32)
    dst_y = np.interp(x, dst[:, 0], dst[:, 1]).astype(np.float32)
    delta = dst_y - src_y
    lo, hi = int(np.ceil(dst[0, 0])), int(np.floor(dst[-1, 0]))
    magnitude = float(np.max(np.abs(delta[lo:hi+1])))
    if magnitude > max_displacement:
        raise ValueError(f'REJECT: road displacement {magnitude:.1f}px exceeds {max_displacement}px')
    y = np.arange(SIZE[1], dtype=np.float32)[:, None]
    field = delta[None, :] * np.exp(-.5 * ((y - dst_y[None, :]) / sigma)**2)
    map_y = (y - field).astype(np.float32)
    map_x = np.broadcast_to(x[None, :], map_y.shape).copy()
    min_grad = float(np.min(np.diff(map_y, axis=0)))
    if min_grad < 1 - MAX_LOCAL_SLOPE:
        raise ValueError(f'REJECT: landscape fold/stretch gradient {min_grad:.3f}')
    valid = (map_y >= 0) & (map_y <= SIZE[1] - 1)
    coverage = float(np.mean(valid))
    # No reflection, repeating, tiling, patch cloning or invented geography.
    if coverage < MIN_COVERAGE:
        raise ValueError(f'REJECT: unobserved image coverage {coverage:.4f}')
    rgb = np.asarray(source.convert('RGB'))
    warped = cv2.remap(rgb, map_x, map_y, cv2.INTER_CUBIC,
                       borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0))
    overhang = float(max(0, dst[0, 0] - src[0, 0],
                         src[-1, 0] - dst[-1, 0]))
    return Image.fromarray(warped), {
        'extraRoadBeyondSurveyPx': round(overhang, 2),
        'visualRoadSurveyLimitPass': bool(overhang <= 50),
        'maxDisplacementPx': round(magnitude, 2),
        'minimumMonotonicGradient': round(min_grad, 4),
        'observedPixelCoverage': round(coverage, 5),
        'sourceLicenseVerified': False,
        'visibleRoadAnnotationIndependentlyReviewed': False,
        'geographicRegistrationVerified': False,
        'historicalRoadsVerified': False,
        'bridgeBanksVerified': False,
        'humanVisualApproval': False,
        'productionApproved': False,
    }

def review(image, target, source=None):
    out = image.convert('RGBA')
    overlay = Image.new('RGBA', SIZE, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    d.line([tuple(p) for p in target], fill=(245, 52, 52, 195),
           width=4, joint='curve')
    if source:
        d.line([tuple(p) for p in source], fill=(60, 220, 245, 190),
               width=3, joint='curve')
    return Image.alpha_composite(out, overlay).convert('RGB')

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--manifest', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--atlas', type=Path, default=Path('terrain-grid/v123-atlas.js'))
    p.add_argument('--tile', choices=['west', 'south'], required=True)
    a = p.parse_args()
    m = json.loads(a.manifest.read_text())
    raw = a.source.read_bytes()
    if hashlib.sha256(raw).hexdigest() != m['sourceSha256']:
        raise ValueError('source sha256 mismatch')
    if m.get('annotationMethod') != 'independent-human-visible-road-trace':
        raise ValueError('source road must be traced independently')
    from v243_road_conditioning import load_routes
    _, routes = load_routes(a.atlas)  # pins original immutable V123 Git blob
    immutable = list(reversed(routes[a.tile])) if a.tile == 'west' else routes[a.tile]
    image = Image.open(a.source).convert('RGB')
    output, report = register(image, m['visibleRoadPoints'], immutable)
    a.out.mkdir(parents=True, exist_ok=True)
    output.save(a.out / 'candidate-unapproved.png')
    review(output, immutable).save(a.out / 'candidate-road-review.jpg', quality=90)
    report.update({
        'sourceSha256': m['sourceSha256'],
        'annotationMethod': m['annotationMethod'],
        'kind': 'UNAPPROVED_FICTIONAL_SOURCE_WARP_STUDY',
        'promotionEligible': False,
    })
    (a.out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))

if __name__ == '__main__':
    main()

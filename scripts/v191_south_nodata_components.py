#!/usr/bin/env python3
"""V191: isolate ambiguous modern-provider white gaps, without painting game art.

A connected near-white region is NOT proof of missing coverage: Alpine snow,
cloud, and bright rock can also be connected to the mosaic edge. This audit
only separates candidate pixels by topological evidence for manual review.
"""
import argparse
from collections import deque
import hashlib
import json
from pathlib import Path

from PIL import Image
import v185_south_tyrol_probe as v185
import v186_south_border_candidates as v186

REPORT = 'white-component-review-NOT-GAME.json'
MASK = 'white-component-review-NOT-GAME.png'
COLORS = {'south-edge': (234, 80, 46, 255),
          'other-edge': (238, 185, 45, 255),
          'interior': (155, 79, 203, 255)}
FALSE_FLAGS = ('geographicSourceCoverageApproved', 'snowExcluded',
               'historicalRoadsVerified', 'bridgeBanksVerified',
               'v123RoadsGeoregistered', 'periodArtComplete',
               'gameArtCoverageApproved', 'physicalIPhoneApproved',
               'productionApproved')


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def classify(original, candidate):
    """Return independent source-review regions and an uncomposited RGBA mask.

    Candidate pixels must be opaque only over original near-white pixels;
    every other pixel must be transparent. Connectivity is 4-neighbor.
    """
    require(original.mode == 'RGB' and candidate.mode == 'RGBA',
            'RGB original and RGBA candidate required')
    require(original.size == candidate.size, 'source grid mismatch')
    width, height = original.size
    require(width >= 3 and height >= 3, 'source grid too small')
    source = original.load(); overlay = candidate.load()
    active = bytearray(width * height)
    white = 0
    for y in range(height):
        for x in range(width):
            i = y * width + x
            observed_white = v185.nearwhite(source[x, y])
            white += int(observed_white)
            pixel = overlay[x, y]
            require(pixel[3] in (0, 255), 'fractional overlay alpha not allowed')
            if pixel[3]:
                require(observed_white, 'candidate overwrites observed source')
                require(not v185.nearwhite(pixel), 'candidate contains white/no-data')
                active[i] = 1
    visited = bytearray(width * height)
    colored = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    out = colored.load()
    groups = {'south-edge': {'components': 0, 'pixels': 0},
              'other-edge': {'components': 0, 'pixels': 0},
              'interior': {'components': 0, 'pixels': 0}}
    components = []
    for start in range(width * height):
        if not active[start] or visited[start]:
            continue
        visited[start] = 1
        queue = deque([start]); pixels = []
        x0 = width; x1 = -1; y0 = height; y1 = -1
        south = other = False
        while queue:
            i = queue.popleft()
            x, y = i % width, i // width
            pixels.append(i)
            x0, x1 = min(x0, x), max(x1, x)
            y0, y1 = min(y0, y), max(y1, y)
            south |= y == height - 1
            other |= x == 0 or x == width - 1 or y == 0
            for neighbor in (i-1 if x else -1,
                             i+1 if x+1 < width else -1,
                             i-width if y else -1,
                             i+width if y+1 < height else -1):
                if neighbor >= 0 and active[neighbor] and not visited[neighbor]:
                    visited[neighbor] = 1
                    queue.append(neighbor)
        category = 'south-edge' if south else 'other-edge' if other else 'interior'
        groups[category]['components'] += 1
        groups[category]['pixels'] += len(pixels)
        for i in pixels:
            out[i % width, i // width] = COLORS[category]
        components.append({'category': category, 'pixels': len(pixels),
                           'boundsXYInclusive': [x0, y0, x1, y1],
                           'touchesSouthEdge': south, 'touchesOtherEdge': other})
    total = sum(g['pixels'] for g in groups.values())
    require(total == sum(active), 'candidate component count mismatch')
    return {
        'nativePixels': [width, height],
        'originalNearWhitePixels': white,
        'candidatePixels': total,
        'unresolvedOriginalNearWhitePixels': white - total,
        'classification': groups,
        'largestComponents': sorted(components,
                                    key=lambda c: (-c['pixels'], c['boundsXYInclusive']))[:15],
        'componentCount': len(components),
        'mask': colored,
    }


def audit(parent_folder, candidate_folder):
    parent_folder = Path(parent_folder); candidate_folder = Path(candidate_folder)
    require(v186.verify(parent_folder, candidate_folder),
            'upstream source provenance/overlay verification failed')
    parent = json.loads((parent_folder / 'manifest.json').read_text())
    upstream = json.loads((candidate_folder / 'manifest.json').read_text())
    with Image.open(parent_folder / parent['mosaicFile']) as im:
        source = im.convert('RGB').crop((0, 2560, 1280, 3072))
    with Image.open(candidate_folder / upstream['candidateOverlayFile']) as im:
        candidate = im.convert('RGBA')
    classified = classify(source, candidate)
    require(classified['candidatePixels'] == upstream['candidateAudit']['candidatePixels'],
            'source candidate total changed')
    mask = classified.pop('mask')
    report = {
        'version': 191,
        'purpose': 'Modern source white-region connectivity for REVIEW only; never GAME terrain',
        'parentManifestSha256': digest((parent_folder / 'manifest.json').read_bytes()),
        'candidateManifestSha256': digest((candidate_folder / 'manifest.json').read_bytes()),
        'originalMosaicSha256': parent['mosaicSha256'],
        'candidateOverlaySha256': upstream['candidateOverlaySha256'],
        'nativeCRS': 'EPSG:3857',
        'fourNeighborConnectivity': True,
        'southEdgeConnectedIsNotBorderOrNoDataProof': True,
        'edgeConnectedSnowOrCloudStillPossible': True,
        'modernInfrastructureStillPresent': True,
        'noSourceOrGamePixelComposited': True,
        'maskColors': {k: list(v) for k, v in COLORS.items()},
        **classified,
        **{key: False for key in FALSE_FLAGS},
    }
    return report, mask


def produce(parent_folder, candidate_folder, out_folder):
    report, mask = audit(parent_folder, candidate_folder)
    out_folder = Path(out_folder); out_folder.mkdir(parents=True, exist_ok=True)
    mask.save(out_folder / MASK)
    report['classificationMaskSha256'] = digest((out_folder / MASK).read_bytes())
    (out_folder / REPORT).write_text(json.dumps(report, indent=2) + '\n')
    verify(parent_folder, candidate_folder, out_folder)
    return report


def verify(parent_folder, candidate_folder, out_folder):
    out_folder = Path(out_folder)
    saved = json.loads((out_folder / REPORT).read_text())
    expected, mask = audit(parent_folder, candidate_folder)
    require(saved.get('classificationMaskSha256') == digest((out_folder / MASK).read_bytes()),
            'classification mask SHA mismatch')
    with Image.open(out_folder / MASK) as im:
        require(im.mode == 'RGBA' and im.size == mask.size and
                im.tobytes() == mask.tobytes(), 'classification mask forged')
    expected['classificationMaskSha256'] = saved['classificationMaskSha256']
    require(saved == expected, 'classification report changed or false approval')
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--parent', default='qa/v184-matrei-brenner-overview')
    parser.add_argument('--candidates', default='qa/v186-south-border-candidates')
    parser.add_argument('--output', default='qa/v191-white-component-review')
    parser.add_argument('--verify', action='store_true')
    args = parser.parse_args()
    if args.verify:
        verify(args.parent, args.candidates, args.output)
    else:
        report = produce(args.parent, args.candidates, args.output)
        print(json.dumps({'candidatePixels': report['candidatePixels'],
                          'classification': report['classification']}, indent=2))
    print('V191 modern SOURCE connectivity only; no GAME or historic road/bridge approval')


if __name__ == '__main__':
    main()

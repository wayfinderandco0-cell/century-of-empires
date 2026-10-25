#!/usr/bin/env python3
"""V187: measure REAL modern-source boundary mismatches; never stitch GAME art.

Audits the V186 transparent South Tyrol candidate against unchanged V184
Austrian pixels. A numerical seam score is a warning, not historical approval.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path

from PIL import Image
import v184_matrei_brenner_overview as v184
import v185_south_tyrol_probe as v185
import v186_south_border_candidates as v186

REPORT = 'source-seam-audit-NOT-GAME.json'
FALSE_APPROVALS = (
    'crossBorderSeamsApproved', 'historicalRoadsVerified',
    'bridgeBanksVerified', 'v121ToGeographyRegistered',
    'v123RoadsGeoregistered', 'gameArtCoverageApproved',
    'periodArtComplete', 'physicalIPhoneApproved', 'productionApproved',
)


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def delta(a, b):
    return sum(abs(int(a[k]) - int(b[k])) for k in range(3)) / 3


def distribution(values):
    if not values:
        return {'count': 0, 'meanRGB': None, 'medianRGB': None,
                'p90RGB': None, 'maxRGB': None}
    values.sort()
    return {
        'count': len(values),
        'meanRGB': round(sum(values) / len(values), 3),
        'medianRGB': round(values[(len(values) - 1) // 2], 3),
        'p90RGB': round(values[((len(values) - 1) * 9) // 10], 3),
        'maxRGB': round(values[-1], 3),
    }


def audit(parent_folder, candidate_folder):
    parent_folder, candidate_folder = Path(parent_folder), Path(candidate_folder)
    require(v186.verify(parent_folder, candidate_folder),
            'V186 source/mask integrity verification failed')
    pm = json.loads((parent_folder / 'manifest.json').read_text())
    cm = json.loads((candidate_folder / 'manifest.json').read_text())
    require(all(cm.get(flag) is False for flag in FALSE_APPROVALS),
            'upstream approval claim must remain false')
    with Image.open(parent_folder / pm['mosaicFile']) as im:
        original = im.convert('RGB').crop((0, 2560, 1280, 3072))
    with Image.open(candidate_folder / cm['candidateOverlayFile']) as im:
        overlay = im.convert('RGBA')
    require(original.size == overlay.size == (1280, 512),
            'native grid dimensions changed')
    src, mask = original.load(), overlay.load()
    tiles = {}
    for item in v186.plan()['sourceTileCandidates']:
        with Image.open(candidate_folder / ('italian-' + item['name'] + '.jpeg')) as im:
            tiles[(item['row'] - 10, item['col'])] = im.convert('RGB').load()
            # PixelAccess from a closed PIL image is not portable: copy RGB bytes.
        with Image.open(candidate_folder / ('italian-' + item['name'] + '.jpeg')) as im:
            tiles[(item['row'] - 10, item['col'])] = im.convert('RGB').tobytes()

    def italian(x, y):
        data = tiles[(y // 256, x // 256)]
        offset = ((y % 256) * 256 + x % 256) * 3
        return data[offset:offset + 3]

    boundary = []
    overlap = []
    per_tile = {t['name']: {'candidatePixels': 0, 'observedOverlapPixels': 0,
                            'candidateToObservedNeighborPairs': 0}
                for t in v186.plan()['sourceTileCandidates']}
    for y in range(512):
        for x in range(1280):
            name = 'r%02dc%02d' % (10 + y // 256, x // 256)
            observed = src[x, y]
            alternative = italian(x, y)
            candidate = mask[x, y][3] == 255
            if candidate:
                per_tile[name]['candidatePixels'] += 1
                for nx, ny in ((x - 1, y), (x + 1, y),
                               (x, y - 1), (x, y + 1)):
                    if 0 <= nx < 1280 and 0 <= ny < 512:
                        neighbor = src[nx, ny]
                        if mask[nx, ny][3] == 0 and not v185.nearwhite(neighbor):
                            boundary.append(delta(alternative, neighbor))
                            per_tile[name]['candidateToObservedNeighborPairs'] += 1
            elif not v185.nearwhite(observed) and not v185.nearwhite(alternative):
                overlap.append(delta(alternative, observed))
                per_tile[name]['observedOverlapPixels'] += 1

    require(sum(x['candidatePixels'] for x in per_tile.values()) ==
            cm['candidateAudit']['candidatePixels'],
            'candidate mask total differs from verified V186 source')
    edges = distribution(boundary)
    agreements = distribution(overlap)
    return {
        'version': 187,
        'purpose': 'Modern source-only seam diagnostics, not stitched or historical GAME terrain',
        'parentManifestSha256': sha(parent_folder / 'manifest.json'),
        'candidateManifestSha256': sha(candidate_folder / 'manifest.json'),
        'candidateOverlaySha256': cm['candidateOverlaySha256'],
        'nativeCRS': 'EPSG:3857',
        'nativeGridPixels': [1280, 512],
        'sourceYearsNotHistoricalProof': True,
        'originalAustrianPixelsUntouched': True,
        'boundaryDefinition': '4-neighbor candidate-to-observed Austrian edge; each pair counted',
        'overlapDefinition': 'same pixel observed nonwhite in both modern providers',
        'boundaryRGBDifference': edges,
        'overlapRGBDifference': agreements,
        'perTile': per_tile,
        'boundaryRequiresVisualReview': True,
        'providerBorderIsNotVerifiedHistoricalRoadOrRiver': True,
        'modernInfrastructureStillPresent': True,
        'sourceMosaicNotComposited': True,
        **{flag: False for flag in FALSE_APPROVALS},
    }


def produce(parent_folder, candidate_folder, output_folder):
    report = audit(parent_folder, candidate_folder)
    output_folder = Path(output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)
    (output_folder / REPORT).write_text(json.dumps(report, indent=2) + '\n')
    verify(parent_folder, candidate_folder, output_folder)
    return report


def verify(parent_folder, candidate_folder, output_folder):
    actual = json.loads((Path(output_folder) / REPORT).read_text())
    require(actual == audit(parent_folder, candidate_folder),
            'seam diagnostics tampered or source changed')
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--parent', default='qa/v184-matrei-brenner-overview')
    parser.add_argument('--candidates', default='qa/v186-south-border-candidates')
    parser.add_argument('--output', default='qa/v187-crossborder-seam-audit')
    parser.add_argument('--verify', action='store_true')
    args = parser.parse_args()
    if args.verify:
        verify(args.parent, args.candidates, args.output)
    else:
        result = produce(args.parent, args.candidates, args.output)
        print('Candidate-to-observed boundary pairs:',
              result['boundaryRGBDifference']['count'])
        print('Observed two-provider overlap:',
              result['overlapRGBDifference'])
    print('V187 SOURCE seam audit only: 3 GAME octagons and historic bridge NOT approved')


if __name__ == '__main__':
    main()

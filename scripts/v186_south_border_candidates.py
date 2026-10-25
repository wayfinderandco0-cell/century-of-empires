#!/usr/bin/env python3
"""V186: audit bottom TWO rows of V184 against licensed South Tyrol imagery.

Transparent candidate overlay ONLY where Austrian source appears near-white.
Never composite into historical game art, infer roads, or certify snow/no-data.
"""
import argparse
import hashlib
import io
import json
import time
from pathlib import Path
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from PIL import Image
import v184_matrei_brenner_overview as v184
import v185_south_tyrol_probe as v185

ROWS = (10, 11)
FALSE_FLAGS = v185.FALSE_FLAGS + (
    'candidateOverlayApproved', 'modernGeographicCoverageApproved',
    'historicTerrainReconstructed', 'crossBorderSeamsApproved',
)
OUTPUT_IMAGE = 'southern-candidate-overlay-TRANSPARENT-NOT-GAME.png'


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def plan():
    parent = v184.plan()
    v184.validate(parent)
    require(parent['gridTiles'] == [5, 12] and parent['tileOriginXYZ'] == [8712, 5752, 14],
            'V184 geography changed: review all source sampling')
    tiles = []
    for s in parent['samples']:
        if s['row'] not in ROWS:
            continue
        x, y, z = s['tileXYZ']
        bounds = v185.projected_bounds(x, y, z)
        params = [('SERVICE', 'WMS'), ('VERSION', '1.3.0'), ('REQUEST', 'GetMap'),
                  ('LAYERS', v185.LAYER), ('STYLES', ''), ('FORMAT', 'image/jpeg'),
                  ('CRS', 'EPSG:3857'), ('WIDTH', '256'), ('HEIGHT', '256'),
                  ('BBOX', ','.join(map(str, bounds)))]
        tiles.append({'name': s['name'], 'row': s['row'], 'col': s['col'],
                      'tileXYZ': [x, y, z], 'boundsEPSG3857': bounds,
                      'wmsUrl': v185.SERVICE + '?' + urlencode(params)})
    require(len(tiles) == 10 and
            next(t for t in tiles if t['name'] == v185.TARGET)['wmsUrl'] ==
            v185.plan()['wmsRequestUrl'], 'V185 geographic crosscheck failed')
    return {
        'version': 186,
        'purpose': 'Modern source-only cross-border candidate mask; NOT GAME ART',
        'parentVersion': 184, 'parentGridTiles': [5, 12],
        'sampleRows': list(ROWS), 'sampleCount': 10,
        'candidateDimensions': [1280, 512], 'candidateOffsetInParentPixels': [0, 2560],
        'provider': v185.plan()['provider'], 'sourceMetadata': v185.METADATA,
        'license': v185.LICENSE, 'requiredAttribution': v185.plan()['requiredAttribution'],
        'wmsLayer': v185.LAYER, 'wmsCRS': 'EPSG:3857',
        'whiteDetectionIsUnverifiedNoDataHeuristic': True,
        'neverOverwriteObservedAustrianSourcePixels': True,
        'unreviewedSnowOrCloudMayBeMisclassified': True,
        'noSeamBlendingOrHistoricalRoadInference': True,
        'sourceTileCandidates': tiles,
        **{flag: False for flag in FALSE_FLAGS},
    }


def validate(m):
    expected = plan()
    require(set(m) - set(expected) <= {'samples', 'candidateOverlayFile',
            'candidateOverlaySha256', 'candidateAudit'}, 'unexpected fields/approval')
    for key, value in expected.items():
        require(m.get(key) == value, 'source provenance/geometry/approval changed: ' + key)
    return True


def load_original(parent, name):
    manifest = json.loads((Path(parent) / 'manifest.json').read_text())
    sample = next(s for s in manifest['samples'] if s['name'] == name)
    path = Path(parent) / sample['imageFile']
    data = path.read_bytes()
    require(digest(data) == sample['sha256'] and len(data) == sample['byteCount'],
            'V184 native source identity changed: ' + name)
    with Image.open(io.BytesIO(data)) as im:
        return im.convert('RGB'), digest(data)


def compute(parent, alternatives):
    require(v184.verify(parent), 'V184 parent failed exact source verification')
    overlay = Image.new('RGBA', (1280, 512), (0, 0, 0, 0))
    reports = []
    for t in plan()['sourceTileCandidates']:
        name = t['name']
        require(name in alternatives, 'missing South Tyrol source: ' + name)
        data = alternatives[name]
        alt = v185.inspect_jpeg(data)
        original, original_hash = load_original(parent, name)
        src, replacement = original.load(), alt.load()
        white = candidates = alt_visible = 0
        for y in range(256):
            for x in range(256):
                a, b = src[x, y], replacement[x, y]
                orig_white = v185.nearwhite(a)
                alt_visible_here = not v185.nearwhite(b)
                white += int(orig_white)
                alt_visible += int(alt_visible_here)
                if orig_white and alt_visible_here:
                    candidates += 1
                    overlay.putpixel((t['col'] * 256 + x,
                                      (t['row'] - ROWS[0]) * 256 + y), (*b, 255))
        reports.append({
            'name': name, 'originalSha256': original_hash,
            'alternativeFile': 'italian-' + name + '.jpeg',
            'alternativeSha256': digest(data), 'alternativeBytes': len(data),
            'originalNearWhitePixels': white,
            'alternativeNonWhitePixels': alt_visible,
            'candidatePixels': candidates,
        })
    return overlay, reports


def produce(parent, out, alternatives):
    parent, out = Path(parent), Path(out)
    require(set(alternatives) == {s['name'] for s in plan()['sourceTileCandidates']},
            'missing or extra source tiles')
    overlay, reports = compute(parent, alternatives)
    require(sum(s['candidatePixels'] for s in reports) > 10000,
            'no meaningful candidate imagery; do not assert source recovery')
    out.mkdir(parents=True, exist_ok=True)
    for item in reports:
        (out / item['alternativeFile']).write_bytes(alternatives[item['name']])
    overlay.save(out / OUTPUT_IMAGE, optimize=True)
    m = plan()
    m.update(samples=reports, candidateOverlayFile=OUTPUT_IMAGE,
             candidateOverlaySha256=digest((out / OUTPUT_IMAGE).read_bytes()),
             candidateAudit={
                 'candidatePixels': sum(s['candidatePixels'] for s in reports),
                 'originalNearWhitePixels': sum(s['originalNearWhitePixels'] for s in reports),
                 'candidateOnlyNotStitched': True,
                 'geographicSourceCoverageApproved': False,
                 'historicalGameArtApproved': False,
             })
    (out / 'manifest.json').write_text(json.dumps(m, indent=2) + '\n')
    verify(parent, out)
    return m


def verify(parent, out):
    out = Path(out)
    m = json.loads((out / 'manifest.json').read_text())
    validate(m)
    reports = m.get('samples')
    require(isinstance(reports, list) and len(reports) == 10, 'missing source reports')
    require([r.get('name') for r in reports] ==
            [s['name'] for s in plan()['sourceTileCandidates']], 'wrong source order')
    alternatives = {}
    for r in reports:
        name = r['name']
        require(r.get('alternativeFile') == 'italian-' + name + '.jpeg',
                'unexpected alternative path')
        data = (out / r['alternativeFile']).read_bytes()
        require(digest(data) == r.get('alternativeSha256') and
                len(data) == r.get('alternativeBytes'), 'alternative source tampered')
        alternatives[name] = data
    expected_image, expected_reports = compute(parent, alternatives)
    require(reports == expected_reports, 'coverage metrics/source hashes changed')
    require(m.get('candidateOverlayFile') == OUTPUT_IMAGE, 'overlay path changed')
    saved_bytes = (out / OUTPUT_IMAGE).read_bytes()
    require(digest(saved_bytes) == m.get('candidateOverlaySha256'),
            'overlay SHA mismatch')
    with Image.open(io.BytesIO(saved_bytes)) as image:
        require(image.mode == 'RGBA' and image.size == expected_image.size and
                image.tobytes() == expected_image.tobytes(),
                'overlay changed: would overwrite observed source pixels')
    require(m.get('candidateAudit') == {
        'candidatePixels': sum(s['candidatePixels'] for s in reports),
        'originalNearWhitePixels': sum(s['originalNearWhitePixels'] for s in reports),
        'candidateOnlyNotStitched': True,
        'geographicSourceCoverageApproved': False,
        'historicalGameArtApproved': False,
    }, 'forged candidate audit')
    return True


def download_all():
    data = {}
    for tile in plan()['sourceTileCandidates']:
        for attempt in range(3):
            try:
                req = Request(tile['wmsUrl'],
                              headers={'User-Agent': 'CenturyOfEmpires-SourceAudit/1.0'})
                with urlopen(req, timeout=25) as response:
                    require('image' in response.headers.get('Content-Type', '').lower(),
                            'WMS non-image response: ' + tile['name'])
                    body = response.read(1024 * 1024 + 1)
                v185.inspect_jpeg(body)
                data[tile['name']] = body
                break
            except (URLError, TimeoutError):
                if attempt == 2:
                    raise
                time.sleep(1.5 * (attempt + 1))
    return data


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--parent', default='qa/v184-matrei-brenner-overview')
    p.add_argument('--output', default='qa/v186-south-border-candidates')
    p.add_argument('--fetch', action='store_true')
    p.add_argument('--verify', action='store_true')
    a = p.parse_args()
    if a.verify:
        verify(a.parent, a.output)
    elif a.fetch:
        m = produce(a.parent, a.output, download_all())
        print('Candidate modern-source pixels:', m['candidateAudit']['candidatePixels'])
    else:
        print(json.dumps(plan(), indent=2))
    print('V186 SOURCE CANDIDATES only; historic roads, GAME art and release NOT approved')


if __name__ == '__main__':
    main()

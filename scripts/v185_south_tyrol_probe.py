#!/usr/bin/env python3
"""V185: probe independently licensed South Tyrol orthophoto over a V184 white gap.

Modern SOURCE only. Never substitute into V121 art, approve historical roads,
remove Austrian imagery, or declare a game tile complete.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from PIL import Image
import v184_matrei_brenner_overview as v184

TARGET = 'r11c03'
SERVICE = 'https://geoservices.buergernetz.bz.it/mapproxy/p_bz-Orthoimagery/wms'
LAYER = 'Aerial-2023-RGB'
METADATA = 'https://data.civis.bz.it/de/dataset/ortofoto-2023'
LICENSE = 'CC BY 4.0 (dataset description; portal heading also says CCZero)'
FALSE_FLAGS = ('v121ToGeographyRegistered', 'v123RoadsGeoregistered',
               'historicalRoadsVerified', 'bridgeBanksVerified',
               'historic1780Certified', 'periodArtComplete',
               'gameArtCoverageApproved', 'physicalIPhoneApproved',
               'productionApproved')


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def projected_bounds(x, y, z):
    radius = 20037508.342789244
    span = 2 * radius / (1 << z)
    return [round(-radius + x * span, 6),
            round(radius - (y + 1) * span, 6),
            round(-radius + (x + 1) * span, 6),
            round(radius - y * span, 6)]


def plan():
    parent = v184.plan()
    v184.validate(parent)
    sample = next(s for s in parent['samples'] if s['name'] == TARGET)
    x, y, z = sample['tileXYZ']
    require([x, y, z] == [8715, 5763, 14], 'unexpected source tile')
    require(parent['gridTiles'] == [5, 12] and parent['tileOriginXYZ'] == [8712, 5752, 14],
            'V184 geographic source changed; revalidate probe')
    bbox = projected_bounds(x, y, z)
    params = [('SERVICE', 'WMS'), ('VERSION', '1.3.0'), ('REQUEST', 'GetMap'),
              ('LAYERS', LAYER), ('STYLES', ''), ('FORMAT', 'image/jpeg'),
              ('CRS', 'EPSG:3857'), ('WIDTH', '256'), ('HEIGHT', '256'),
              ('BBOX', ','.join(str(n) for n in bbox))]
    return {'version': 185,
            'purpose': 'Cross-border modern orthophoto coverage PROBE only; not game art',
            'v184ParentVersion': 184, 'v184TileName': TARGET,
            'v184TileXYZ': [x, y, z], 'v184TileBoundsLonLat': sample['boundsLonLat'],
            'wmsBoundsEPSG3857': bbox, 'wmsCRS': 'EPSG:3857',
            'wmsVersion': '1.3.0', 'wmsLayer': LAYER,
            'wmsService': SERVICE, 'wmsRequestUrl': SERVICE + '?' + urlencode(params),
            'provider': 'Autonomous Province of Bolzano - South Tyrol',
            'sourceMetadata': METADATA, 'sourceYear': 2023,
            'license': LICENSE,
            'requiredAttribution': 'Autonome Provinz Bozen / Provincia Autonoma di Bolzano; basemap.at for original Austrian source',
            'sourceTileWhiteMayIndicateOutsideAustria': True,
            'alternativeCoverageApproved': False,
            'alternativeUsableForPeriodArt': False,
            'doesNotCertifyModernOrHistoricalRoads': True,
            **{k: False for k in FALSE_FLAGS}}


def validate(m):
    expected = plan()
    require(set(m) - set(expected) <= {'alternativeFile', 'alternativeSha256',
            'alternativeByteCount', 'coverageAudit', 'originalSourceSha256'},
            'unexpected metadata or fake approval')
    for k, value in expected.items():
        require(m.get(k) == value, 'changed WMS geometry/provider/approval: ' + k)
    return True


def nearwhite(p):
    return min(p[:3]) >= 248 and max(p[:3]) - min(p[:3]) <= 7


def audit(original, alternative):
    require(original.size == alternative.size == (256, 256), 'wrong source tile dimensions')
    original = original.convert('RGB'); alternative = alternative.convert('RGB')
    src = original.load(); alt = alternative.load()
    white = 0; candidate = 0; alt_detail = 0
    for y in range(256):
        for x in range(256):
            a, b = src[x, y], alt[x, y]
            if nearwhite(a):
                white += 1
                if not nearwhite(b):
                    candidate += 1
            if not nearwhite(b):
                alt_detail += 1
    return {'v184OriginalNearWhitePixels': white,
            'southTyrolNonWhitePixels': alt_detail,
            'candidateSupplementalPixels': candidate,
            'totalPixels': 65536,
            'requiresIndependentImageReview': True,
            'candidateOnlyNotStitched': True,
            'geographicSourceCoverageApproved': False,
            'historicTerrainApproved': False,
            'gameArtCoverageApproved': False}


def inspect_jpeg(data):
    require(data.startswith(b'\xff\xd8') and len(data) < 1024 * 1024,
            'WMS did not return native-sized JPEG bytes')
    with Image.open(io.BytesIO(data)) as im:
        require(im.format == 'JPEG' and im.size == (256, 256),
                'WMS exception/invalid dimensions')
        im.verify()
    return Image.open(io.BytesIO(data)).convert('RGB')


def produce(parent_folder, out_folder, alternative_bytes):
    parent_folder = Path(parent_folder); out_folder = Path(out_folder)
    require(v184.verify(parent_folder), 'V184 parent source failed integrity check')
    manifest = json.loads((parent_folder / 'manifest.json').read_text())
    source = next(s for s in manifest['samples'] if s['name'] == TARGET)
    source_bytes = (parent_folder / source['imageFile']).read_bytes()
    require(sha(source_bytes) == source['sha256'], 'original V184 source tile altered')
    with Image.open(io.BytesIO(source_bytes)) as original:
        original_rgb = original.convert('RGB')
    alternative = inspect_jpeg(alternative_bytes)
    coverage = audit(original_rgb, alternative)
    require(coverage['v184OriginalNearWhitePixels'] > 30000,
            'V184 missing-area observation changed; review source again')
    require(coverage['candidateSupplementalPixels'] > 10000,
            'alternative WMS did not supply meaningful candidate coverage')
    m = plan()
    out_folder.mkdir(parents=True, exist_ok=True)
    name = 'south-tyrol-2023-r11c03-candidate.jpeg'
    (out_folder / name).write_bytes(alternative_bytes)
    m.update(alternativeFile=name, alternativeSha256=sha(alternative_bytes),
             alternativeByteCount=len(alternative_bytes),
             originalSourceSha256=sha(source_bytes), coverageAudit=coverage)
    (out_folder / 'manifest.json').write_text(json.dumps(m, indent=2) + '\n')
    verify(parent_folder, out_folder)
    return m


def verify(parent_folder, out_folder):
    out_folder = Path(out_folder)
    m = json.loads((out_folder / 'manifest.json').read_text())
    validate(m)
    require(m.get('alternativeFile') == 'south-tyrol-2023-r11c03-candidate.jpeg',
            'invalid alternative source path')
    data = (out_folder / m['alternativeFile']).read_bytes()
    require(sha(data) == m.get('alternativeSha256') and
            len(data) == m.get('alternativeByteCount'), 'alternative source modified')
    require(v184.verify(parent_folder), 'V184 parent failed verification')
    parent = json.loads((Path(parent_folder) / 'manifest.json').read_text())
    source = next(s for s in parent['samples'] if s['name'] == TARGET)
    original_bytes = (Path(parent_folder) / source['imageFile']).read_bytes()
    require(sha(original_bytes) == m.get('originalSourceSha256'),
            'original parent identity changed')
    original = Image.open(io.BytesIO(original_bytes))
    require(m.get('coverageAudit') == audit(original, inspect_jpeg(data)),
            'candidate coverage audit modified')
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--parent', default='qa/v184-matrei-brenner-overview')
    parser.add_argument('--output', default='qa/v185-south-tyrol-probe')
    parser.add_argument('--fetch', action='store_true')
    parser.add_argument('--verify', action='store_true')
    args = parser.parse_args()
    if args.verify:
        verify(args.parent, args.output)
    elif args.fetch:
        m = plan()
        req = Request(m['wmsRequestUrl'], headers={'User-Agent': 'CenturyOfEmpires-SourceAudit/1.0'})
        with urlopen(req, timeout=30) as response:
            require('image' in response.headers.get('Content-Type', '').lower(),
                    'WMS returned non-image response')
            data = response.read(1024 * 1024 + 1)
        produce(args.parent, args.output, data)
    else:
        print(json.dumps(plan(), indent=2))
    print('V185 South Tyrol candidate SOURCE only; no road, bridge, GAME or period approval')


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""V180: acquire native Matrei-area orthophotos, not Navis/game octagons.

The 18 modern source tiles cover one L-shaped neighborhood of the independently
identified Matrei am Brenner reference point. They are NOT the intended three
GAME cells and do not validate V121 painted art, V123 roads, or a historic bridge.
"""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image
from v146_orthophoto_sample import BASE, SOURCE, LICENSE, fetch_images, lonlat_to_xyz, xyz_bounds

ANCHOR = (11.45306, 47.13083)
ZOOM = 17
PIXEL = 256
WIDTH, HEIGHT = 1536, 1024
ATTRIBUTION = 'Datenquelle: basemap.at'
REJECTED = {
    'sourceSectorsAreGameOctagons': False,
    'v121ToGeographyRegistered': False,
    'v123RoadsGeoregistered': False,
    'historicalRoadsVerified': False,
    'bridgeBanksVerified': False,
    'historic1780Certified': False,
    'periodArtComplete': False,
    'physicalIPhoneApproved': False,
    'productionApproved': False,
}

def require(ok, why):
    if not ok:
        raise ValueError(why)

def plan():
    cx, cy = lonlat_to_xyz(*ANCHOR, ZOOM)
    x0, y0 = cx - 4, cy - 1
    samples = []
    for row in range(4):
        for col in range(6):
            if row >= 2 and col < 3:
                continue  # Never fabricate southwest source.
            x, y = x0 + col, y0 + row
            samples.append({
                'name': f'r{row}c{col}', 'row': row, 'col': col,
                'tileXYZ': [x, y, ZOOM], 'boundsLonLat': xyz_bounds(x, y, ZOOM),
                'url': f'{BASE}/{ZOOM}/{y}/{x}.jpeg',
            })
    west, south, _, north = xyz_bounds(x0, y0, ZOOM)
    _, bottom, east, _ = xyz_bounds(x0 + 5, y0 + 3, ZOOM)
    require(south > bottom, 'invalid north/south tile order')
    return {
        'version': 180, 'purpose': 'Modern Matrei-area SOURCE L only, NOT three GAME octagons',
        'anchorId': 'matrei-am-brenner', 'anchorLonLat': list(ANCHOR),
        'anchorEvidence': 'https://en.wikipedia.org/wiki/Matrei_am_Brenner',
        'sourceComparison': 'V168 Navis L is a different geographic footprint',
        'provider': 'basemap.at', 'sourceUrl': SOURCE,
        'license': 'CC BY 4.0', 'licenseUrl': LICENSE,
        'requiredAttribution': ATTRIBUTION, 'crs': 'EPSG:3857',
        'zoom': ZOOM, 'pixelDimensions': [WIDTH, HEIGHT],
        'tileOriginXYZ': [x0, y0, ZOOM],
        'mosaicBoundsLonLat': [west, bottom, east, north],
        'unobservedSouthwestBoundsPixels': [0, 512, 768, 1024],
        'sourceSectors': {
            'matrei-source-west': [0, 0, 768, 512],
            'matrei-source-center': [768, 0, 1536, 512],
            'matrei-source-south': [768, 512, 1536, 1024],
        },
        'samples': samples, **REJECTED,
    }

def validate(m):
    expected = plan()
    require(set(m) - set(expected) <= {'mosaicFile', 'mosaicSha256', 'seamDiagnostics'},
            'unexpected certification/source metadata')
    for key, val in expected.items():
        if key != 'samples':
            require(m.get(key) == val, 'source identity or approval changed: ' + key)
    records = m.get('samples')
    require(isinstance(records, list) and len(records) == 18,
            'missing/duplicated Matrei source tile')
    for got, correct in zip(records, expected['samples']):
        require(isinstance(got, dict), 'invalid source record')
        for key, val in correct.items():
            require(got.get(key) == val, 'source tile identity/position changed')
        require(set(got) - set(correct) <= {'imageFile', 'sha256', 'byteCount'},
                'unexpected source tile metadata')
        if 'imageFile' in got:
            require(got['imageFile'] == correct['name'] + '.jpeg',
                    'source image filename mismatches XYZ')
    return True

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def compose(m, folder):
    validate(m)
    folder = Path(folder)
    canvas = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 0))
    for item in m['samples']:
        require(item.get('imageFile') == item['name'] + '.jpeg' and
                isinstance(item.get('sha256'), str) and len(item['sha256']) == 64,
                'unverified source JPEG')
        path = folder / item['imageFile']
        require(path.is_file() and sha(path) == item['sha256'],
                'missing/tampered source JPEG')
        with Image.open(path) as original:
            require(original.format == 'JPEG' and original.size == (256, 256),
                    'not a native 256px JPEG')
            tile = original.convert('RGBA')
        canvas.paste(tile, (item['col'] * PIXEL, item['row'] * PIXEL))
    require(canvas.getpixel((384, 768))[3] == 0 and
            canvas.getpixel((1152, 768))[3] == 255 and
            canvas.getpixel((384, 256))[3] == 255,
            'source holes/coverage incorrectly filled')
    return canvas

def seams(canvas):
    """Adjacent source-pixel differences are diagnostics, NOT visual approval."""
    result = []
    for label, a, b, step, n in (
        ('west/center', (767, 0), (768, 0), (0, 1), 512),
        ('center/south', (768, 511), (768, 512), (1, 0), 768),
    ):
        deltas = []
        for i in range(n):
            p = canvas.getpixel((a[0]+i*step[0], a[1]+i*step[1]))
            q = canvas.getpixel((b[0]+i*step[0], b[1]+i*step[1]))
            require(p[3] == q[3] == 255, 'gap at observed source seam')
            deltas.append(sum(abs(p[k]-q[k]) for k in range(3)) / 3)
        result.append({'edge': label, 'samples': n,
                       'meanRGBDifference': round(sum(deltas)/n, 4),
                       'sourcePixelAdjacencyVerified': True,
                       'gameArtSeamApproved': False})
    return result

def produce(m, folder):
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    image = compose(m, folder)
    name = 'matrei-modern-source-L.png'
    image.save(folder/name, optimize=True)
    m['mosaicFile'] = name
    m['mosaicSha256'] = sha(folder/name)
    m['seamDiagnostics'] = seams(image)
    (folder/'manifest.json').write_text(json.dumps(m, indent=2)+'\n')
    verify(folder)
    return m

def verify(folder):
    folder = Path(folder)
    m = json.loads((folder/'manifest.json').read_text())
    source = compose(m, folder)
    require(m.get('mosaicFile') == 'matrei-modern-source-L.png' and
            sha(folder/m['mosaicFile']) == m.get('mosaicSha256'),
            'mosaic checksum changed')
    with Image.open(folder/m['mosaicFile']) as original:
        require(original.mode == 'RGBA' and original.size == source.size and
                original.tobytes() == source.tobytes(),
                'mosaic pixels differ from 18 native JPEG tiles')
    require(m.get('seamDiagnostics') == seams(source), 'seam diagnostics changed')
    return True

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default='qa/v180-matrei-source')
    parser.add_argument('--download', action='store_true')
    parser.add_argument('--verify', action='store_true')
    args = parser.parse_args()
    folder = Path(args.output)
    if args.verify:
        verify(folder)
    else:
        m = plan()
        folder.mkdir(parents=True, exist_ok=True)
        if args.download:
            fetch_images(m, folder)
            produce(m, folder)
        else:
            (folder/'manifest.json').write_text(json.dumps(m, indent=2)+'\n')
    print('V180 Matrei SOURCE only: 18 unique native tiles; no historical GAME approval.')

if __name__ == '__main__':
    main()

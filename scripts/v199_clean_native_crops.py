#!/usr/bin/env python3
"""V199: pixel-faithful, georeferenced clean *source-reference* crops.

No inpainting, game-world mapping, road invention, or historical certification.
The V197/V198 sources must be independently verified upstream in CI.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

CROP_SIZE = 160
MASK_CLEARANCE = 12
ZOOM = 18
TILE_SIZE = 256
# Manually chosen from inspected V197 source + V198 red quarantine contact.
# Each is (left, top) of a 160px native image crop. Not V123 game positions.
CROPS = {
    'western_forest_reference': ((40, 65), (335, 65), (40, 290)),
    'eastern_ridge_reference': ((20, 35), (150, 230), (335, 300)),
    'southern_forest_reference': ((20, 30), (255, 30), (15, 250)),
}
FORBIDDEN_TRUE = ('periodSafe', 'productionApproved', 'gameArtApproved',
                  'gameOctagonsGeoregistered', 'historicalRoadsVerified',
                  'bridgeBanksVerified', 'physicalIPhoneApproved')


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def lonlat_bounds(tile_xyz, rect):
    """Native EPSG:3857 XYZ pixels -> lon/lat. No historical/game transform."""
    tx, ty, zoom = tile_xyz
    require(zoom == ZOOM and 0 <= tx < 2**zoom and 0 <= ty < 2**zoom,
            'invalid native XYZ origin')
    left, top, right, bottom = rect
    n = 2**zoom
    def lon(px):
        return ((tx + px/TILE_SIZE)/n)*360 - 180
    def lat(py):
        return math.degrees(math.atan(math.sinh(math.pi *
            (1 - 2*(ty + py/TILE_SIZE)/n))))
    return [lon(left), lat(bottom), lon(right), lat(top)]


def load_verified_sources(v197_dir, v198_dir):
    v197_dir, v198_dir = Path(v197_dir), Path(v198_dir)
    p197, p198 = v197_dir/'manifest.json', v198_dir/'manifest.json'
    m197, m198 = json.loads(p197.read_text()), json.loads(p198.read_text())
    require(m197.get('version') == 197 and m198.get('version') == 198,
            'wrong source generations')
    require(m197.get('requiredAttribution') == m198.get('requiredAttribution')
            == 'Datenquelle: basemap.at' and m197.get('license') == m198.get('license')
            == 'CC BY 4.0', 'license or attribution mismatch')
    require(m198.get('sourceManifestSha256') == sha(p197), 'parent source changed')
    require(m197.get('notGameOctagonCenters') is True
            and m198.get('geographicRegistrationToV123') is False
            and m198.get('unreviewedModernFeaturesRemain') is True,
            'incorrect geographic/period status')
    require(all(m198.get(k) is False for k in FORBIDDEN_TRUE),
            'false approval in V198 input')
    names = tuple(CROPS)
    s197, s198 = m197.get('samples', []), m198.get('samples', [])
    require(len(s197) == len(s198) == len(names)
            and tuple(s.get('name') for s in s197) == names
            and tuple(s.get('name') for s in s198) == names,
            'source order or identity changed')
    sources = []
    for a, b in zip(s197, s198):
        name = a['name']
        source_path = v197_dir/a['image']
        qpath = v198_dir/b['quarantinedImage']
        mask_path = v198_dir/b['maskImage']
        require(sha(source_path) == a['imageSha256'] == b['sourceImageSha256'],
                'source pixel provenance changed')
        require(sha(qpath) == b['quarantinedImageSha256']
                and sha(mask_path) == b['maskImageSha256'],
                'quarantine or mask modified')
        with Image.open(source_path) as im: source = im.copy()
        with Image.open(qpath) as im: quarantined = im.copy()
        with Image.open(mask_path) as im: mask = im.copy()
        require(source.mode == 'RGB' and quarantined.mode == 'RGBA'
                and mask.mode == 'L' and source.size == quarantined.size
                == mask.size == (512, 512), 'unexpected source format')
        require(source.tobytes() == quarantined.convert('RGB').tobytes(),
                'quarantine altered source RGB')
        require(set(mask.tobytes()) <= {0, 255}
                and quarantined.getchannel('A').tobytes()
                == mask.point(lambda p: 255-p).tobytes(),
                'quarantine alpha mismatch')
        require(mask.tobytes().count(255) == b['excludedPixelCount']
                and mask.tobytes().count(0) == b['retainedPixelCount'],
                'mask count mismatch')
        origin = a['nativeOriginXYZ']
        require(len(origin) == 3 and origin[2] == ZOOM,
                'wrong geographic registration')
        require(a['footprintLonLat'] == lonlat_bounds(origin, (0, 0, 512, 512)),
                'sample footprint does not match XYZ origin')
        sources.append((a, source, mask))
    return m197, m198, sources


def plan(v197_dir, v198_dir):
    m197, m198, sources = load_verified_sources(v197_dir, v198_dir)
    crops = []
    for a, source, mask in sources:
        name = a['name']
        forbidden = mask.filter(ImageFilter.MaxFilter(2*MASK_CLEARANCE+1))
        rectangles = []
        for index, (x, y) in enumerate(CROPS[name]):
            rect = (x, y, x+CROP_SIZE, y+CROP_SIZE)
            require(x >= 0 and y >= 0 and rect[2] <= 512 and rect[3] <= 512,
                    'crop out of source bounds')
            require(forbidden.crop(rect).getbbox() is None,
                    'crop too near quarantined modern feature')
            require(all(rect[2] <= r[0] or r[2] <= rect[0]
                        or rect[3] <= r[1] or r[3] <= rect[1]
                        for r in rectangles), 'duplicate/overlapping crops')
            rectangles.append(rect)
            native = source.crop(rect)
            bounds = lonlat_bounds(a['nativeOriginXYZ'], rect)
            require(a['footprintLonLat'][0] <= bounds[0] < bounds[2]
                    <= a['footprintLonLat'][2]
                    and a['footprintLonLat'][1] <= bounds[1] < bounds[3]
                    <= a['footprintLonLat'][3], 'crop geographic escape')
            crops.append({
                'name': f'{name}-clean-reference-{index+1:02d}.png',
                'sourceSample': name,
                'sourceImageSha256': a['imageSha256'],
                'nativeOriginXYZ': a['nativeOriginXYZ'],
                'sourcePixelRect': list(rect),
                'footprintLonLat': bounds,
                'pixelRGBSha256': hashlib.sha256(native.tobytes()).hexdigest(),
                'maskClearancePixels': MASK_CLEARANCE,
                'annotatedFeaturePixelsInside': 0,
                'historicalNaturalCoverVerified': False,
                'modernFeaturesFullyExcluded': False,
                'eligibleForGameArt': False,
            })
    require(len(crops) == 9, 'nine independently sourced clean crops required')
    return {
        'version': 199,
        'purpose': 'Native georeferenced modern-source visual reference crops only; NOT 1780 game art',
        'parentV197ManifestSha256': sha(Path(v197_dir)/'manifest.json'),
        'parentV198ManifestSha256': sha(Path(v198_dir)/'manifest.json'),
        'crs': 'EPSG:3857',
        'nativeZoom': ZOOM,
        'nativeCropPixels': [CROP_SIZE, CROP_SIZE],
        'requiredAttribution': m197['requiredAttribution'],
        'license': m197['license'],
        'onlyAnnotatedFeaturesExcluded': True,
        'gameWorldRegistrationKnown': False,
        'periodSafe': False,
        'gameArtApproved': False,
        'historicalRoadsVerified': False,
        'bridgeBanksVerified': False,
        'physicalIPhoneApproved': False,
        'productionApproved': False,
        'crops': crops,
    }


def expected_render(v197_dir, v198_dir):
    m = plan(v197_dir, v198_dir)
    _, _, sources = load_verified_sources(v197_dir, v198_dir)
    by_name = {a['name']: source for a, source, _ in sources}
    sheet = Image.new('RGB', (CROP_SIZE*3, (CROP_SIZE+28)*3), (18, 33, 27))
    draw = ImageDraw.Draw(sheet)
    renders = []
    for i, item in enumerate(m['crops']):
        native = by_name[item['sourceSample']].crop(tuple(item['sourcePixelRect']))
        sheet.paste(native, ((i%3)*CROP_SIZE, (i//3)*(CROP_SIZE+28)))
        draw.text(((i%3)*CROP_SIZE+5, (i//3)*(CROP_SIZE+28)+CROP_SIZE+5),
                  f'{item["sourceSample"].split("_")[0]} #{i%3+1} | SOURCE',
                  fill=(240, 225, 205))
        renders.append(native)
    return m, renders, sheet


def produce(v197_dir, v198_dir, output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    m, renders, sheet = expected_render(v197_dir, v198_dir)
    for item, im in zip(m['crops'], renders):
        im.save(output/item['name'])
        item['pngSha256'] = sha(output/item['name'])
    sheet_name = 'v199-nine-native-clean-reference-crops.png'
    sheet.save(output/sheet_name)
    m['contactSheet'] = sheet_name
    m['contactSheetSha256'] = sha(output/sheet_name)
    (output/'manifest.json').write_text(json.dumps(m, indent=2)+'
')
    verify(v197_dir, v198_dir, output)
    return m


def verify(v197_dir, v198_dir, output):
    output = Path(output)
    got = json.loads((output/'manifest.json').read_text())
    expected, renders, sheet = expected_render(v197_dir, v198_dir)
    require(set(got) == set(expected) | {'contactSheet', 'contactSheetSha256'},
            'unexpected top-level fields')
    for k, v in expected.items():
        if k != 'crops':
            require(got.get(k) == v, 'source provenance or approval changed: '+k)
    require(len(got.get('crops', [])) == len(renders), 'missing crops')
    for entry, expected_entry, im in zip(got['crops'], expected['crops'], renders):
        require(set(entry) == set(expected_entry) | {'pngSha256'},
                'unexpected crop fields')
        for k, v in expected_entry.items():
            require(entry.get(k) == v, 'crop registration/pixel claim changed: '+k)
        p = output/entry['name']
        require(p.is_file() and sha(p) == entry['pngSha256'],
                'crop file or digest modified')
        with Image.open(p) as saved:
            require(saved.mode == 'RGB' and saved.size == im.size
                    and saved.tobytes() == im.tobytes(),
                    'crop pixels not original native source')
    require(got.get('contactSheet') == 'v199-nine-native-clean-reference-crops.png',
            'unexpected contact filename')
    p = output/got['contactSheet']
    require(p.is_file() and sha(p) == got.get('contactSheetSha256'),
            'contact digest altered')
    with Image.open(p) as saved:
        require(saved.mode == 'RGB' and saved.size == sheet.size
                and saved.tobytes() == sheet.tobytes(),
                'contact preview modified')
    return True


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--source', default='qa/v197-highres-source-materials')
    p.add_argument('--quarantine', default='qa/v198-source-exclusions')
    p.add_argument('--output', default='qa/v199-clean-native-crops')
    p.add_argument('--verify', action='store_true')
    a = p.parse_args()
    if a.verify:
        verify(a.source, a.quarantine, a.output)
    else:
        produce(a.source, a.quarantine, a.output)
    print('V199 native clean SOURCE crops verified; no historic/game visual approval')


if __name__ == '__main__':
    main()

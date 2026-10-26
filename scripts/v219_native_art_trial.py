#!/usr/bin/env python3
"""V219: opt-in real native Alpine photo art trial, never V123 registration.

Only original V218 retained RGB is used. Unknown/modern areas remain alpha=0;
a boundary feather reduces alpha but never fills, invents or upscales pixels.
"""
import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image

SITES = ((5, 'west', 110, 90), (6, 'west', 835, 360),
         (3, 'south', 135, 105), (8, 'south', 845, 390))
FALSE_FLAGS = ('sourceRegisteredToV123', 'historicRoadsVerified',
               'periodSafe', 'gameArtApproved', 'physicalIPhoneApproved',
               'productionApproved')
SIZE, FEATHER = 512, 58

def sha(data):
    return hashlib.sha256(data).hexdigest()

def require(ok, message):
    if not ok:
        raise ValueError(message)

def feather(im):
    require(im.mode == 'RGBA' and im.size == (SIZE, SIZE), 'native source required')
    out = im.copy()
    pix = out.load()
    for y in range(SIZE):
        for x in range(SIZE):
            r, g, b, a = pix[x, y]
            edge = min(x, y, SIZE - 1 - x, SIZE - 1 - y)
            t = max(0., min(1., edge / FEATHER))
            pix[x, y] = r, g, b, round(a * t * t * (3 - 2 * t))
    return out

def generate(source, target):
    source, target = Path(source), Path(target)
    upstream = json.loads((source / 'manifest.json').read_text())
    require(upstream['version'] == 218 and all(upstream[f] is False for f in
            ('registeredToV123', 'historicalRoadsVerified', 'periodSafe',
             'gameArtApproved', 'productionApproved')), 'upstream approval false required')
    require(upstream['source'] == 'basemap.at modern 2023 aerial; CC BY 4.0; Datenquelle: basemap.at',
            'source attribution changed')
    target.mkdir(parents=True, exist_ok=True)
    by_index = {s['siteIndex']: s for s in upstream['sites']}
    entries = []
    for idx, tile, x, y in SITES:
        s = by_index[idx]
        raw = (source / s['quarantineFile']).read_bytes()
        require(sha(raw) == s['quarantineSha256'], 'upstream quarantine bytes changed')
        with Image.open(source / s['quarantineFile']) as im:
            src = im.convert('RGBA')
        with Image.open(source / s['originalFile']) as original:
            orig = original.convert('RGB')
        require(sha((source / s['originalFile']).read_bytes()) == s['sourceSha256'],
                'original source changed')
        native, natural = src.load(), orig.load()
        for py in range(SIZE):
            for px in range(SIZE):
                rgb = native[px, py]
                if rgb[3]:
                    require(rgb[:3] == natural[px, py] and rgb[3] == 255,
                            'source colors altered or alpha not native')
        result = feather(src)
        filename = f'site-{idx:02d}-native-feather.webp'
        result.save(target / filename, format='WEBP', lossless=True, method=6)
        with Image.open(target / filename) as decoded:
            saved = decoded.convert('RGBA')
        for py in range(SIZE):
            for px in range(SIZE):
                a, b = result.getpixel((px, py)), saved.getpixel((px, py))
                require(a[3] == b[3] and (a[3] == 0 or a[:3] == b[:3]),
                        'encoded photographic source changed')
        require(x >= 0 and y >= 0 and x + SIZE <= 1536 and y + SIZE <= 1024,
                'trial placement leaves source cell')
        entries.append(dict(siteIndex=idx, tile=tile, x=x, y=y,
                            width=SIZE, height=SIZE, file=filename,
                            sha256=sha((target / filename).read_bytes()),
                            originalSha256=s['sourceSha256'],
                            quarantineSha256=s['quarantineSha256'],
                            sourceFootprintLonLat=s['sourceFootprintLonLat'],
                            artisticPlacementNotGeoregistration=True))
    manifest = dict(version=219, kind='OPT_IN_UNREGISTERED_PHOTO_MATERIAL_ART_STUDY',
                    attribution='Datenquelle: basemap.at | CC BY 4.0',
                    sourceYear=2023, nativePixels=[SIZE, SIZE],
                    alphaFeatherPixels=FEATHER, sourceQuarantineStillUnknown=True,
                    noUpscaling=True, noDuplicatedSourcePanels=True,
                    centerMatreiArtworkUnchanged=True, roadGraphUnchanged=True,
                    entries=entries, **{flag: False for flag in FALSE_FLAGS})
    (target / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    return manifest

def verify(source, target):
    target = Path(target)
    expected = generate(source, target.parent / '_v219_verify_rebuild')
    stored = json.loads((target / 'manifest.json').read_text())
    require(stored == expected, 'manifest or geographic/approval flags changed')
    for e in expected['entries']:
        actual = (target / e['file']).read_bytes()
        rebuild = (target.parent / '_v219_verify_rebuild' / e['file']).read_bytes()
        require(actual == rebuild and sha(actual) == e['sha256'],
                'native art candidate was altered')
    return True

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--source', type=Path, default=Path('qa/v218-modern-quarantine'))
    p.add_argument('--output', type=Path, default=Path('terrain-v219/assets'))
    p.add_argument('--verify', action='store_true')
    a = p.parse_args()
    print(json.dumps(verify(a.source, a.output) if a.verify else generate(a.source, a.output), indent=2))

if __name__ == '__main__':
    main()

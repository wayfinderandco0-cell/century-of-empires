#!/usr/bin/env python3
"""V181: evidence-limited modern-feature exclusion, SOURCE study only.

Coordinates are native V180 Matrei source pixels, manually reviewed against
GitHub Actions artifact 12593190495. No historical feature is synthesized.
"""
import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageChops

SIZE = (1536, 1024)
ORIGIN = [69701, 46030, 17]
ATTRIBUTION = 'Datenquelle: basemap.at'
FALSE_FLAGS = ('sourceSectorsAreGameOctagons','v121ToGeographyRegistered',
               'v123RoadsGeoregistered','historicalRoadsVerified',
               'bridgeBanksVerified','historic1780Certified','periodArtComplete',
               'physicalIPhoneApproved','productionApproved')
# Deliberately conservative; approximate source-image exclusions, NOT surveys.
FEATURES = (
    {'id':'modern-motorway', 'kind':'line', 'width':64,
     'points':[(979,0),(972,240),(968,480),(972,710),(990,1023)],
     'basis':'visually identified divided motorway and paved shoulders'},
    {'id':'modern-railway', 'kind':'line', 'width':32,
     'points':[(1432,0),(1415,160),(1388,310),(1363,460),(1327,620),(1285,810),(1208,1023)],
     'basis':'visually identified rail tracks; does not establish historical rail alignment'},
    {'id':'north-sports-ground', 'kind':'polygon',
     'points':[(1241,0),(1360,0),(1361,171),(1238,171),(1224,59)],
     'basis':'marked contemporary athletic field'},
    {'id':'south-sports-ground', 'kind':'polygon',
     'points':[(1070,392),(1195,390),(1195,650),(1068,647)],
     'basis':'marked sports pitches and tennis courts'},
)

def require(ok, message):
    if not ok: raise ValueError(message)

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def read_source(folder):
    folder = Path(folder)
    m = json.loads((folder/'manifest.json').read_text())
    require(m.get('version') == 180 and m.get('tileOriginXYZ') == ORIGIN
            and m.get('pixelDimensions') == list(SIZE)
            and m.get('requiredAttribution') == ATTRIBUTION
            and m.get('provider') == 'basemap.at'
            and m.get('license') == 'CC BY 4.0', 'unrecognized V180 source identity')
    require(all(m.get(k) is False for k in FALSE_FLAGS), 'source has false GAME approval')
    records = m.get('samples')
    require(isinstance(records, list) and len(records) == 18, 'wrong source tile count')
    require(m.get('mosaicFile') == 'matrei-modern-source-L.png'
            and sha(folder/m['mosaicFile']) == m.get('mosaicSha256'),
            'source mosaic checksum invalid')
    with Image.open(folder/m['mosaicFile']) as image:
        require(image.mode == 'RGBA' and image.size == SIZE, 'invalid source PNG')
        source = image.copy()
    positions = set()
    for item in records:
        row, col = item.get('row'), item.get('col')
        require(type(row) is int and type(col) is int and 0 <= row < 4
                and 0 <= col < 6 and not (row >= 2 and col < 3),
                'invalid tile position')
        require(item.get('name') == f'r{row}c{col}'
                and item.get('tileXYZ') == [ORIGIN[0]+col, ORIGIN[1]+row, ORIGIN[2]]
                and item.get('imageFile') == f'r{row}c{col}.jpeg',
                'source tile identity changed')
        require((row,col) not in positions, 'duplicate source tile')
        positions.add((row,col))
        path = folder/item['imageFile']
        require(path.is_file() and sha(path) == item.get('sha256'),
                'source JPEG missing or tampered')
        with Image.open(path) as tile:
            require(tile.format == 'JPEG' and tile.size == (256,256),
                    'non-native source tile')
            native = tile.convert('RGBA')
        require(source.crop((col*256,row*256,(col+1)*256,(row+1)*256)).tobytes()
                == native.tobytes(), 'source PNG differs from native JPEG')
    require(len(positions) == 18, 'incomplete source L')
    require(source.getpixel((250,800))[3] == 0
            and source.getpixel((250,250))[3] == 255,
            'unacquired southwest improperly filled')
    return m, source

def exclusion_mask():
    mask = Image.new('L', SIZE, 0)
    draw = ImageDraw.Draw(mask)
    for feature in FEATURES:
        pts = feature['points']
        require(len(pts) >= 2 and all(0 <= x < SIZE[0] and 0 <= y < SIZE[1]
                                       for x,y in pts), 'invalid native feature points')
        if feature['kind'] == 'line':
            draw.line(pts, fill=255, width=feature['width'], joint='curve')
            r = feature['width']//2
            for x,y in pts:
                draw.ellipse((x-r,y-r,x+r,y+r),fill=255)
        else:
            require(feature['kind'] == 'polygon' and len(pts)>=3, 'invalid feature kind')
            draw.polygon(pts,fill=255)
    return mask

def build(folder, output):
    m, source = read_source(folder)
    mask = exclusion_mask()
    keep = ImageChops.multiply(source.getchannel('A'),ImageChops.invert(mask))
    result = Image.new('RGBA', SIZE, (0,0,0,0))
    result.paste(source,(0,0),keep)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    result.save(output/'matrei-modern-excluded-SOURCE.png',optimize=True)
    mask.save(output/'matrei-modern-exclusion-mask.png',optimize=True)
    excluded = sum(1 for a,b in zip(source.getchannel('A').getdata(),mask.getdata()) if a and b)
    observed = sum(1 for a in source.getchannel('A').getdata() if a)
    report = {
        'version':181, 'purpose':'Modern Matrei SOURCE exclusions; NOT period GAME art',
        'sourceMosaicSha256':m['mosaicSha256'], 'sourceTileOriginXYZ':ORIGIN,
        'sourceAttribution':ATTRIBUTION, 'sourceLicense':'CC BY 4.0',
        'reviewedImageArtifact':'https://github.com/wayfinderandco0-cell/century-of-empires/actions/runs/40176746873/artifacts/12593190495',
        'featureAnnotations':list(FEATURES),
        'excludedObservedPixels':excluded, 'observedSourcePixels':observed,
        'excludedPercentOfObserved':round(100*excluded/observed,3),
        'unreviewedBuiltEnvironmentStillPresent':True,
        'exclusionBoundsAreApproximate':True,
        'unobservedSouthwestRemainsTransparent':True,
        'excludedOutputSha256':sha(output/'matrei-modern-excluded-SOURCE.png'),
        'exclusionMaskSha256':sha(output/'matrei-modern-exclusion-mask.png'),
        **{k:False for k in FALSE_FLAGS},
    }
    (output/'manifest.json').write_text(json.dumps(report,indent=2)+'\n')
    verify(folder,output)
    return report

def verify(folder,output):
    m, source = read_source(folder)
    output = Path(output)
    report = json.loads((output/'manifest.json').read_text())
    require(report.get('version') == 181 and report.get('sourceMosaicSha256') == m['mosaicSha256']
            and report.get('sourceTileOriginXYZ') == ORIGIN
            and report.get('sourceAttribution') == ATTRIBUTION
            and report.get('featureAnnotations') == json.loads(json.dumps(FEATURES))
            and report.get('unreviewedBuiltEnvironmentStillPresent') is True
            and report.get('exclusionBoundsAreApproximate') is True
            and all(report.get(k) is False for k in FALSE_FLAGS),
            'V181 provenance or approval forged')
    require(sha(output/'matrei-modern-excluded-SOURCE.png') == report.get('excludedOutputSha256')
            and sha(output/'matrei-modern-exclusion-mask.png') == report.get('exclusionMaskSha256'),
            'V181 image hash mismatch')
    with Image.open(output/'matrei-modern-exclusion-mask.png') as img:
        require(img.mode == 'L' and img.size == SIZE and img.tobytes() == exclusion_mask().tobytes(),
                'mask pixels differ from reviewed exclusion geometry')
    with Image.open(output/'matrei-modern-excluded-SOURCE.png') as img:
        require(img.mode == 'RGBA' and img.size == SIZE, 'invalid excluded output')
        result = img.copy()
    mask = exclusion_mask()
    excluded = observed = 0
    for a,b,c in zip(source.getdata(),mask.getdata(),result.getdata()):
        observed += (a[3] != 0)
        excluded += (a[3] != 0 and b != 0)
        expected = a if a[3] and not b else (0,0,0,0)
        require(c == expected, 'output altered, filled holes or invented source pixels')
    require(excluded == report.get('excludedObservedPixels')
            and observed == report.get('observedSourcePixels')
            and report.get('excludedPercentOfObserved') == round(100*excluded/observed,3),
            'exclusion pixel counts changed')
    return True

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--source',default='qa/v180-matrei-source')
    p.add_argument('--output',default='qa/v181-matrei-exclusions')
    p.add_argument('--verify',action='store_true')
    a=p.parse_args()
    if a.verify: verify(a.source,a.output)
    else: build(a.source,a.output)
    print('V181 modern SOURCE exclusion verified; period GAME art and roads remain unapproved.')

if __name__ == '__main__': main()

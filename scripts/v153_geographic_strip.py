#!/usr/bin/env python3
"""V153: three adjacent modern geographic SOURCE sectors, not game octagons.

Builds 3 rows x 9 columns of original-pixel basemap.at orthophotos around
V102's Navis inspection point. Every sector is 768x768 source pixels and the
three sectors touch exactly; neither V121/V123 nor historical roads are mapped.
"""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image
from v146_orthophoto_sample import (BASE, LICENSE, SOURCE, fetch_images,
                                   lonlat_to_xyz, xyz_bounds)

ROWS, COLS, PIXELS, ZOOM = 3, 9, 256, 17
CENTER = (11.520, 47.130)
ATTRIBUTION = 'Datenquelle: basemap.at'
UNAPPROVED = {
    'gameOctagonCentersCertified': False,
    'gameRouteGeoregistered': False,
    'historic1780Certified': False,
    'navigableRouteCertified': False,
    'bridgeBanksVerified': False,
    'productionApproved': False,
}


def plan(source):
    bounds = source['boundsLonLat']
    if not (len(bounds) == 4 and bounds[0] < bounds[2] and bounds[1] < bounds[3]):
        raise ValueError('Invalid V102 geographic source bounds')
    cx, cy = lonlat_to_xyz(*CENTER, ZOOM)
    samples = []
    for row in range(ROWS):
        for col in range(COLS):
            x, y = cx + col - COLS // 2, cy + row - ROWS // 2
            box = xyz_bounds(x, y, ZOOM)
            if not (bounds[0] <= box[0] < box[2] <= bounds[2] and
                    bounds[1] <= box[1] < box[3] <= bounds[3]):
                raise ValueError('Source strip exceeds V102 bounds')
            samples.append({'name': f'r{row}c{col}', 'gridRow': row,
                            'gridCol': col, 'tileXYZ': [x, y, ZOOM],
                            'tileBoundsLonLat': box,
                            'url': f'{BASE}/{ZOOM}/{y}/{x}.jpeg'})
    return {'version': 153, 'purpose': 'Modern contiguous geographic source study only',
            'geographicSource': 'terrain-v102/manifest.json',
            'sourceBoundsLonLat': bounds, 'crs': 'EPSG:3857',
            'provider': 'basemap.at', 'sourceUrl': SOURCE,
            'license': 'CC BY 4.0', 'licenseUrl': LICENSE,
            'requiredAttribution': ATTRIBUTION, 'centerLonLat': list(CENTER),
            'grid': [ROWS, COLS], 'pixelDimensions': [COLS * PIXELS, ROWS * PIXELS],
            'mosaicBoundsLonLat': [samples[0]['tileBoundsLonLat'][0],
                                   samples[-1]['tileBoundsLonLat'][1],
                                   samples[-1]['tileBoundsLonLat'][2],
                                   samples[0]['tileBoundsLonLat'][3]],
            'sectors': [{'name': n, 'columnRange': [3*i, 3*i+3],
                         'pixelBounds': [768*i, 0, 768*(i+1), 768]}
                        for i, n in enumerate(('source-west', 'source-center', 'source-east'))],
            **UNAPPROVED, 'samples': samples}


def validate(manifest, source):
    expected = plan(source)
    # Require every planning field to match exactly; permit only downloaded-image
    # metadata on individual tiles and explicitly documented raster diagnostics.
    allowed_extra = {'sourceImageSeamDiagnostics', 'mosaicFile', 'mosaicSha256',
                     'sectorFiles', 'sectorSha256'}
    if set(manifest) - set(expected) - allowed_extra:
        raise ValueError('Unexpected source or certification fields')
    for key, value in expected.items():
        if key == 'samples':
            continue
        if manifest.get(key) != value:
            raise ValueError('Source strip geometry/provenance/certification changed: '+key)
    tiles = manifest.get('samples')
    if not isinstance(tiles, list) or len(tiles) != ROWS*COLS:
        raise ValueError('Missing or extra source tile')
    for got, correct in zip(tiles, expected['samples']):
        if any(got.get(k) != v for k,v in correct.items()):
            raise ValueError('Source XYZ/URL/geography/position changed')
        if set(got) - set(correct) - {'imageFile', 'sha256', 'byteCount'}:
            raise ValueError('Untrusted source tile fields')
        if 'imageFile' in got and got['imageFile'] != got['name']+'.jpeg':
            raise ValueError('Source filename does not match its position')
    return True


def assemble(manifest, source, directory):
    validate(manifest, source)
    out = Image.new('RGB', (COLS*PIXELS, ROWS*PIXELS))
    source_tiles = {}
    for tile in manifest['samples']:
        if not tile.get('sha256') or not tile.get('imageFile'):
            raise ValueError('Missing source image provenance')
        data = (directory / tile['imageFile']).read_bytes()
        if hashlib.sha256(data).hexdigest() != tile['sha256']:
            raise ValueError('Source JPEG SHA256 mismatch')
        with Image.open(directory / tile['imageFile']) as image:
            if image.format != 'JPEG' or image.size != (PIXELS,PIXELS):
                raise ValueError('Invalid source tile image')
            rgb = image.convert('RGB')
        row, col = tile['gridRow'], tile['gridCol']
        out.paste(rgb, (col*PIXELS, row*PIXELS))
        source_tiles[row,col] = rgb
    seams=[]
    for row in range(ROWS):
        for col in range(COLS):
            here=source_tiles[row,col]
            if col+1<COLS:
                nxt=source_tiles[row,col+1]
                d=sum(abs(a-b) for y in range(PIXELS)
                      for a,b in zip(here.getpixel((255,y)),nxt.getpixel((0,y))))
                seams.append({'orientation':'vertical','row':row,'col':col,
                              'sectorBoundary':col in (2,5),
                              'meanRgbChannelDelta':round(d/(PIXELS*3),3)})
            if row+1<ROWS:
                nxt=source_tiles[row+1,col]
                d=sum(abs(a-b) for x in range(PIXELS)
                      for a,b in zip(here.getpixel((x,255)),nxt.getpixel((x,0))))
                seams.append({'orientation':'horizontal','row':row,'col':col,
                              'sectorBoundary':False,
                              'meanRgbChannelDelta':round(d/(PIXELS*3),3)})
    return out, seams


def write_images(manifest, source, directory):
    mosaic, seams = assemble(manifest, source, directory)
    mosaic_path=directory/'modern-source-strip.png'
    mosaic.save(mosaic_path,optimize=True)
    manifest['mosaicFile']=mosaic_path.name
    manifest['mosaicSha256']=hashlib.sha256(mosaic_path.read_bytes()).hexdigest()
    manifest['sourceImageSeamDiagnostics']=seams
    manifest['sectorFiles']={}
    manifest['sectorSha256']={}
    for sector in manifest['sectors']:
        name=sector['name']; x0,y0,x1,y1=sector['pixelBounds']
        crop=mosaic.crop((x0,y0,x1,y1))
        filename=name+'.png'
        crop.save(directory/filename,optimize=True)
        manifest['sectorFiles'][name]=filename
        manifest['sectorSha256'][name]=hashlib.sha256((directory/filename).read_bytes()).hexdigest()
    return mosaic


def verify_files(manifest, source, directory):
    rebuilt,_=assemble(manifest, source, directory)
    if len(manifest.get('sourceImageSeamDiagnostics',[])) != ROWS*(COLS-1)+(ROWS-1)*COLS:
        raise ValueError('Missing seam diagnostics')
    for name in [manifest['mosaicFile'],*manifest['sectorFiles'].values()]:
        data=(directory/name).read_bytes()
        expected=(manifest['mosaicSha256'] if name==manifest['mosaicFile'] else
                  manifest['sectorSha256'][name.removesuffix('.png')])
        if hashlib.sha256(data).hexdigest()!=expected:
            raise ValueError('Source PNG SHA256 mismatch')
    with Image.open(directory/manifest['mosaicFile']) as im:
        if im.size!=rebuilt.size or im.convert('RGB').tobytes()!=rebuilt.tobytes():
            raise ValueError('Source mosaic pixel mismatch')
    for sector in manifest['sectors']:
        with Image.open(directory/manifest['sectorFiles'][sector['name']]) as im:
            if im.size!=(768,768) or im.convert('RGB').tobytes()!=rebuilt.crop(tuple(sector['pixelBounds'])).tobytes():
                raise ValueError('Source sector pixel mismatch')
    return True


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--manifest',default='terrain-v102/manifest.json')
    p.add_argument('--output',default='qa/v153-geographic-strip')
    p.add_argument('--download',action='store_true')
    p.add_argument('--verify',action='store_true')
    a=p.parse_args()
    source=json.loads(Path(a.manifest).read_text())
    out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
    if a.verify:
        report=json.loads((out/'manifest.json').read_text())
        verify_files(report,source,out)
        print('V153 VERIFIED: 27 authentic adjacent source tiles, 3 original-pixel geographic sectors; game and history UNAPPROVED')
        return
    report=plan(source)
    if a.download:
        fetch_images(report,out)
        write_images(report,source,out)
    (out/'manifest.json').write_text(json.dumps(report,indent=2)+'\n')
    print('V153:',len(report['samples']),'source tiles planned;',
          sum('sha256' in t for t in report['samples']),'actual JPEGs;',
          'game roads, historical geography, and production NOT certified')


if __name__=='__main__':
    main()

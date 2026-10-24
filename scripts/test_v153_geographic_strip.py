#!/usr/bin/env python3
"""Offline deterministic V153 geographic source and integrity regression."""
import copy
import hashlib
import tempfile
from pathlib import Path
from PIL import Image
from v153_geographic_strip import (plan,validate,assemble,write_images,
                                   verify_files,ROWS,COLS,PIXELS)

SOURCE={'boundsLonLat':[11.43,47.075,11.625,47.19]}
manifest=plan(SOURCE)
assert manifest['grid']==[3,9]
assert manifest['pixelDimensions']==[2304,768]
assert len(manifest['samples'])==27
assert manifest['mosaicBoundsLonLat'][0]<11.52<manifest['mosaicBoundsLonLat'][2]
assert manifest['mosaicBoundsLonLat'][1]<47.13<manifest['mosaicBoundsLonLat'][3]
assert len({tuple(t['tileXYZ']) for t in manifest['samples']})==27
assert all(v is False for k,v in manifest.items() if k.endswith('Certified') or k in ('productionApproved','bridgeBanksVerified','gameRouteGeoregistered'))
assert [s['pixelBounds'] for s in manifest['sectors']]==[[0,0,768,768],[768,0,1536,768],[1536,0,2304,768]]
validate(manifest,SOURCE)
negatives=0

def reject(mutate):
    global negatives
    bad=copy.deepcopy(manifest);mutate(bad)
    try: validate(bad,SOURCE)
    except (ValueError,KeyError,TypeError): negatives+=1
    else: raise AssertionError('Tampered source manifest was accepted')

reject(lambda m:m.update(productionApproved=True))
reject(lambda m:m.update(historic1780Certified=True))
reject(lambda m:m.update(gameRouteGeoregistered=True))
reject(lambda m:m.update(bridgeBanksVerified=True))
reject(lambda m:m.update(gameOctagonCentersCertified=True))
reject(lambda m:m['samples'][5]['tileXYZ'].__setitem__(0,123))
reject(lambda m:m['samples'][8].update(url='https://example.com/fake.jpg'))
reject(lambda m:m['samples'][10]['tileBoundsLonLat'].__setitem__(0,0))
reject(lambda m:m['samples'].pop())
reject(lambda m:m['samples'].append(copy.deepcopy(m['samples'][0])))
reject(lambda m:m['sectors'][1]['pixelBounds'].__setitem__(0,777))
reject(lambda m:m.update(fakeRoadContinuity=True))
reject(lambda m:m['samples'][0].update(imageFile='../traversal.jpeg'))

with tempfile.TemporaryDirectory() as tmp:
    folder=Path(tmp)
    # 27 independent source-like JPEGs; no network or fabricated historical art.
    for tile in manifest['samples']:
        r,c=tile['gridRow'],tile['gridCol']
        im=Image.new('RGB',(PIXELS,PIXELS),(20+c*19,25+r*40,50+(r*COLS+c)*3))
        name=tile['name']+'.jpeg';im.save(folder/name,format='JPEG')
        data=(folder/name).read_bytes()
        tile.update(imageFile=name,sha256=hashlib.sha256(data).hexdigest(),byteCount=len(data))
    raster=write_images(manifest,SOURCE,folder)
    assert raster.size==(2304,768)
    assert len(manifest['sourceImageSeamDiagnostics'])==42
    assert sum(x['sectorBoundary'] for x in manifest['sourceImageSeamDiagnostics'])==6
    assert len(manifest['sectorFiles'])==3
    assert verify_files(manifest,SOURCE,folder)
    (folder/manifest['samples'][0]['imageFile']).write_bytes(b'broken')
    try: assemble(manifest,SOURCE,folder)
    except ValueError as exc: assert 'SHA256' in str(exc)
    else: raise AssertionError('Tampered JPEG passed source integrity')
    negatives+=1
print('V153 PASS: 27 exact geographic source tiles, 3 contiguous 768px sectors, 42 measured seams, '+str(negatives)+' fail-closed tamper cases; no historical/game-road approval')

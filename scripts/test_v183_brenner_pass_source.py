#!/usr/bin/env python3
"""Synthetic integrity and fail-closed provenance tests for V183 source imagery."""
import copy
import json
import tempfile
from pathlib import Path
from PIL import Image
import v183_brenner_pass_source as v

count=0
def test(name,fn):
    global count
    fn()
    count+=1
    print('PASS',name)
def reject(fn):
    try: fn()
    except (ValueError,FileNotFoundError,KeyError): return
    raise AssertionError('invalid source or forged GAME approval accepted')
def fixture(folder):
    m=v.plan()
    for i,item in enumerate(m['samples']):
        path=folder/(item['name']+'.jpeg')
        Image.new('RGB',(256,256),((i*23)%256,(i*39)%256,(i*57)%256)).save(path)
        item.update(imageFile=path.name,sha256=v.sha(path),byteCount=path.stat().st_size)
    return m

def geometry():
    m=v.plan()
    assert m['version']==183 and len(m['samples'])==9
    assert len({tuple(x['tileXYZ']) for x in m['samples']})==9
    assert m['tileOriginXYZ'][:2]==[v.tile_at(*v.ANCHOR)[0]-1,v.tile_at(*v.ANCHOR)[1]-1]
    w,s,e,n=m['mosaicBoundsLonLat']
    assert w<v.ANCHOR[0]<e and s<v.ANCHOR[1]<n
    assert 10 < m['matreiToPassStraightLineKm'] < 20
    assert m['doesNotProveContinuousTerrainCoverage'] is True
    assert m['sourceRoadsNotPeriodRoutes'] is True
    assert v.validate(m)

def distinct():
    m=v.plan()
    mx,my=v.tile_at(*v.MATREI)
    assert all(abs(x['tileXYZ'][1]-my)>10 for x in m['samples'])
    assert not m['sourceSectorsAreGameOctagons']

def immutable():
    for edit in (
        lambda x:x.update(productionApproved=True),
        lambda x:x.update(bridgeBanksVerified=True),
        lambda x:x.update(v123RoadsGeoregistered=True),
        lambda x:x.update(sourceSectorsAreGameOctagons=True),
        lambda x:x.update(doesNotProveContinuousTerrainCoverage=False),
        lambda x:x.update(anchorLonLat=[11.5,47.1]),
        lambda x:x.update(requiredAttribution=''),
        lambda x:x['samples'][0].update(tileXYZ=x['samples'][1]['tileXYZ']),
        lambda x:x['samples'][0].update(url='https://invalid.example'),
        lambda x:x['samples'].pop(),
        lambda x:x.update(historicRoadPolyline=[(0,0),(1,1)]),
    ):
        m=copy.deepcopy(v.plan());edit(m);reject(lambda:v.validate(m))

def roundtrip():
    with tempfile.TemporaryDirectory() as t:
        folder=Path(t)
        m=fixture(folder)
        v.produce(m,folder)
        assert v.verify(folder)
        with Image.open(folder/'brenner-pass-modern-source.png') as im:
            assert im.size==(768,768) and im.mode=='RGBA'
            assert im.getpixel((50,50))[3]==255
            assert im.getpixel((700,700))[3]==255
        report=json.loads((folder/'manifest.json').read_text())
        assert len(report['seamDiagnostics'])==4
        assert all(x['nativeSourcePixelAdjacencyVerified'] and not x['gameArtSeamApproved'] for x in report['seamDiagnostics'])
        assert all(report[k] is False for k in v.FALSE_FLAGS)

def tamper_jpeg():
    with tempfile.TemporaryDirectory() as t:
        folder=Path(t);m=fixture(folder);v.produce(m,folder)
        (folder/'r0c0.jpeg').write_bytes(b'forged')
        reject(lambda:v.verify(folder))

def tamper_mosaic():
    with tempfile.TemporaryDirectory() as t:
        folder=Path(t);m=fixture(folder);v.produce(m,folder)
        path=folder/'brenner-pass-modern-source.png'
        with Image.open(path) as im: img=im.copy()
        img.putpixel((300,300),(255,0,0,255));img.save(path)
        reject(lambda:v.verify(folder))

def missing_tile():
    with tempfile.TemporaryDirectory() as t:
        folder=Path(t);m=fixture(folder)
        (folder/'r2c2.jpeg').unlink()
        reject(lambda:v.compose(m,folder))

def forged_manifest():
    with tempfile.TemporaryDirectory() as t:
        folder=Path(t);m=fixture(folder);v.produce(m,folder)
        path=folder/'manifest.json'
        data=json.loads(path.read_text());data['historicalRoadsVerified']=True
        path.write_text(json.dumps(data))
        reject(lambda:v.verify(folder))

for name,fn in [
    ('real geographic pass anchor and nine unique native tiles',geometry),
    ('Brenner Pass source does not reuse Matrei source',distinct),
    ('forged historic road, bridge, game and provenance fields rejected',immutable),
    ('synthetic native JPEG compose, four seams and false approvals',roundtrip),
    ('tampered source JPEG rejected',tamper_jpeg),
    ('tampered source mosaic rejected',tamper_mosaic),
    ('missing tile rejected',missing_tile),
    ('forged historic certification rejected',forged_manifest),
]: test(name,fn)
print(f'V183 {count} tests passed; source-only, not historical GAME artwork')

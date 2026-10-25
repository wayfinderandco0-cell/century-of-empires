#!/usr/bin/env python3
"""Fail-closed synthetic tests for geographically contiguous V184 SOURCE overview."""
import copy
import json
import tempfile
from pathlib import Path
from PIL import Image
import v184_matrei_brenner_overview as v

passed=0
def check(name,fn):
    global passed
    fn();passed+=1;print('PASS',name)
def reject(fn):
    try:fn()
    except (ValueError,FileNotFoundError,KeyError):return
    raise AssertionError('invalid source or forged historic approval accepted')
def fixture(folder):
    m=v.plan()
    for i,item in enumerate(m['samples']):
        path=folder/(item['name']+'.jpeg')
        Image.new('RGB',(256,256),((i*11)%256,(i*17)%256,(i*29)%256)).save(path)
        item.update(imageFile=path.name,sha256=v.sha(path),byteCount=path.stat().st_size)
    return m

def geometry():
    m=v.plan();a=v.tile_at(*v.MATREI);b=v.tile_at(*v.BRENNER)
    assert m['gridTiles']==[abs(a[0]-b[0])+3,abs(a[1]-b[1])+3]
    assert m['gridTiles']==[5,12] and len(m['samples'])==60
    assert m['pixelDimensions']==[1280,3072]
    assert m['tileOriginXYZ']==[min(a[0],b[0])-1,min(a[1],b[1])-1,14]
    assert len({tuple(s['tileXYZ']) for s in m['samples']})==60
    assert m['plannedGridFullyContiguous'] and m['straightLineAnchorCoverageOnly']
    w,s,e,n=m['mosaicBoundsLonLat']
    for lon,lat in (v.MATREI,v.BRENNER):assert w<lon<e and s<lat<n
    assert v.validate(m)

def not_game():
    m=v.plan()
    assert all(m[k] is False for k in v.FALSE_FLAGS)
    assert m['doesNotProveHistoricalOrTraversableRoadCorridor']
    assert m['doesNotReplaceHighResolutionGameTerrain']
    assert m['modernInfrastructureRequiresExclusion']

def immutable():
    for edit in (
        lambda m:m.update(productionApproved=True),
        lambda m:m.update(v123RoadsGeoregistered=True),
        lambda m:m.update(historicalRoadsVerified=True),
        lambda m:m.update(bridgeBanksVerified=True),
        lambda m:m.update(straightLineAnchorCoverageOnly=False),
        lambda m:m.update(anchorsLonLat={'matrei':[11,47],'brenner':[11,46]}),
        lambda m:m.update(requiredAttribution=''),
        lambda m:m['samples'].pop(),
        lambda m:m['samples'][0].update(tileXYZ=m['samples'][1]['tileXYZ']),
        lambda m:m['samples'][0].update(url='https://fake.invalid/1.jpeg'),
        lambda m:m.update(surveyedRoad=[(1,2),(3,4)]),
    ):
        m=copy.deepcopy(v.plan());edit(m);reject(lambda:v.validate(m))

def roundtrip():
    with tempfile.TemporaryDirectory() as d:
        folder=Path(d);m=fixture(folder);v.produce(m,folder)
        assert v.verify(folder)
        with Image.open(folder/m['mosaicFile']) as image:
            assert image.size==(1280,3072) and image.mode=='RGBA'
            assert image.getpixel((100,100))[3]==255
            assert image.getpixel((1200,3000))[3]==255
        s=json.loads((folder/'manifest.json').read_text())['seamDiagnostics']
        assert s['horizontalTilePairs']==48 and s['verticalTilePairs']==55
        assert s['nativeRasterFullyObserved'] and not s['gameArtSeamApproved']

def tamper_source():
    with tempfile.TemporaryDirectory() as d:
        folder=Path(d);m=fixture(folder);v.produce(m,folder)
        (folder/'r00c00.jpeg').write_bytes(b'forged')
        reject(lambda:v.verify(folder))

def tamper_mosaic():
    with tempfile.TemporaryDirectory() as d:
        folder=Path(d);m=fixture(folder);v.produce(m,folder)
        path=folder/m['mosaicFile']
        with Image.open(path) as image:changed=image.copy()
        changed.putpixel((500,500),(255,0,0,255));changed.save(path)
        reject(lambda:v.verify(folder))

def missing_tile():
    with tempfile.TemporaryDirectory() as d:
        folder=Path(d);m=fixture(folder);(folder/'r06c02.jpeg').unlink()
        reject(lambda:v.compose(m,folder))

def forged_manifest():
    with tempfile.TemporaryDirectory() as d:
        folder=Path(d);m=fixture(folder);v.produce(m,folder)
        path=folder/'manifest.json';data=json.loads(path.read_text())
        data['historic1780Certified']=True;path.write_text(json.dumps(data))
        reject(lambda:v.verify(folder))

def forged_seams():
    with tempfile.TemporaryDirectory() as d:
        folder=Path(d);m=fixture(folder);v.produce(m,folder)
        path=folder/'manifest.json';data=json.loads(path.read_text())
        data['seamDiagnostics']['gameArtSeamApproved']=True
        path.write_text(json.dumps(data));reject(lambda:v.verify(folder))

for name,fn in [
    ('two independent anchors inside 60 native contiguous zoom14 tiles',geometry),
    ('no historic, road, bridge or GAME approvals',not_game),
    ('forged coordinates, routes and approval fields rejected',immutable),
    ('synthetic 60 JPEG raster, 103 seams, complete alpha coverage',roundtrip),
    ('tampered native source JPEG rejected',tamper_source),
    ('tampered composite rejected',tamper_mosaic),
    ('missing center tile rejected',missing_tile),
    ('forged historic approval rejected',forged_manifest),
    ('forged GAME-art seam approval rejected',forged_seams),
]:check(name,fn)
print(f'V184 {passed} tests passed; modern SOURCE coverage only')

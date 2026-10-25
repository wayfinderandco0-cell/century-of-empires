#!/usr/bin/env python3
"""V180 synthetic regression suite: geographic identity and native-pixel integrity."""
import copy
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
import v180_matrei_source as v
from v146_orthophoto_sample import lonlat_to_xyz
from v168_source_first_l_octagons import plan as navis_plan

ROOT = Path(__file__).resolve().parent.parent
count = 0

def test(name, fn):
    global count
    fn()
    count += 1
    print('PASS', name)

def raises(fn):
    try:
        fn()
    except (ValueError, FileNotFoundError, KeyError):
        return
    raise AssertionError('expected fail-closed error')

def fixture(folder):
    m = v.plan()
    for i, tile in enumerate(m['samples']):
        path = folder / (tile['name'] + '.jpeg')
        Image.new('RGB', (256,256), ((i*17)%256, (i*31)%256, (i*47)%256)).save(path)
        tile['imageFile'] = path.name
        tile['sha256'] = v.sha(path)
        tile['byteCount'] = path.stat().st_size
    return m

def plan_geometry():
    m = v.plan()
    assert m['version'] == 180
    assert m['tileOriginXYZ'] == [lonlat_to_xyz(*v.ANCHOR,v.ZOOM)[0]-4,
                                  lonlat_to_xyz(*v.ANCHOR,v.ZOOM)[1]-1,v.ZOOM]
    assert len(m['samples']) == 18
    assert len({tuple(s['tileXYZ']) for s in m['samples']}) == 18
    assert m['unobservedSouthwestBoundsPixels'] == [0,512,768,1024]
    assert m['mosaicBoundsLonLat'][0] < v.ANCHOR[0] < m['mosaicBoundsLonLat'][2]
    assert m['mosaicBoundsLonLat'][1] < v.ANCHOR[1] < m['mosaicBoundsLonLat'][3]
    assert v.validate(m)

def independent_anchor():
    code = "const a=require('./terrain-grid/v179-real-landmark-coverage.js').ANCHORS[0];process.stdout.write(JSON.stringify([a.lon,a.lat]))"
    real = json.loads(subprocess.check_output(['node','-e',code],cwd=ROOT))
    assert real == list(v.ANCHOR)
    assert v.plan()['anchorId'] == 'matrei-am-brenner'

def not_navis():
    source = json.loads((ROOT/'terrain-v102/manifest.json').read_text())
    navis = navis_plan(source)
    old = {tuple(t['tileXYZ']) for t in navis['samples']}
    new = {tuple(t['tileXYZ']) for t in v.plan()['samples']}
    assert not old.intersection(new), 'Matrei cannot reuse Navis JPEG coordinates'

def strict_identity():
    m=v.plan()
    for edit in (
        lambda x: x.update(productionApproved=True),
        lambda x: x.update(sourceSectorsAreGameOctagons=True),
        lambda x: x.update(v123RoadsGeoregistered=True),
        lambda x: x.update(anchorLonLat=[11.520,47.130]),
        lambda x: x.update(requiredAttribution=''),
        lambda x: x['samples'][0].update(url='https://unverified.invalid/0.jpeg'),
        lambda x: x['samples'][1].update(tileXYZ=x['samples'][0]['tileXYZ']),
        lambda x: x['samples'].pop(),
        lambda x: x.update(unobservedSouthwestBoundsPixels=[]),
        lambda x: x.update(fakeRoadSurvey=True),
    ):
        bad=copy.deepcopy(m)
        edit(bad)
        raises(lambda: v.validate(bad))

def real_native_fixture():
    with tempfile.TemporaryDirectory() as t:
        folder=Path(t)
        m=fixture(folder)
        v.produce(m,folder)
        assert v.verify(folder)
        with Image.open(folder/'matrei-modern-source-L.png') as image:
            assert image.size==(1536,1024)
            assert image.getpixel((384,768))[3]==0
            assert image.getpixel((384,256))[3]==255
            assert image.getpixel((1152,768))[3]==255
        m2=json.loads((folder/'manifest.json').read_text())
        assert len(m2['seamDiagnostics'])==2
        assert all(not s['gameArtSeamApproved'] for s in m2['seamDiagnostics'])

def tampered_source_fails():
    with tempfile.TemporaryDirectory() as t:
        folder=Path(t)
        m=fixture(folder)
        v.produce(m,folder)
        (folder/m['samples'][0]['imageFile']).write_bytes(b'forged')
        raises(lambda: v.verify(folder))

def tampered_mosaic_fails():
    with tempfile.TemporaryDirectory() as t:
        folder=Path(t)
        m=fixture(folder)
        v.produce(m,folder)
        with Image.open(folder/'matrei-modern-source-L.png') as image:
            img=image.copy()
        img.putpixel((1152,256),(255,0,0,255))
        img.save(folder/'matrei-modern-source-L.png')
        raises(lambda: v.verify(folder))

def missing_tile_fails():
    with tempfile.TemporaryDirectory() as t:
        folder=Path(t)
        m=fixture(folder)
        (folder/m['samples'][4]['imageFile']).unlink()
        raises(lambda: v.compose(m,folder))

def no_approval():
    m=v.plan()
    for key in v.REJECTED:
        assert m[key] is False, key
    assert m['purpose'].endswith('NOT three GAME octagons')

for name, fn in [
    ('18 geographically distinct Matrei tiles, source L shape',plan_geometry),
    ('independent V179 Matrei anchor is unchanged',independent_anchor),
    ('Matrei acquisition is not the Navis source reused',not_navis),
    ('provenance, geometry and false approvals rejected',strict_identity),
    ('native-pixel synthetic 18-JPEG compose/verify and unknown SW',real_native_fixture),
    ('tampered source JPEG rejected',tampered_source_fails),
    ('tampered PNG mosaic rejected',tampered_mosaic_fails),
    ('missing source tile rejected',missing_tile_fails),
    ('no historical, road, GAME or production approvals',no_approval),
]:
    test(name,fn)
print(f'V180 source-only acquisition tests: {count} passed; GAME art unapproved.')

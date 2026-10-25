#!/usr/bin/env python3
"""V185 fail-closed geometry, license, non-stitch and image integrity tests."""
import copy
import io
import tempfile
from pathlib import Path
from PIL import Image, ImageDraw
import v184_matrei_brenner_overview as parent
import v185_south_tyrol_probe as v

passed = 0

def check(name, fn):
    global passed
    fn(); passed += 1; print('PASS', name)

def reject(fn):
    try:
        fn()
    except (ValueError, FileNotFoundError, KeyError):
        return
    raise AssertionError('invalid source/false historical claim accepted')

def jpg(image):
    out = io.BytesIO(); image.convert('RGB').save(out, format='JPEG', quality=95)
    return out.getvalue()

def fixture(folder):
    folder.mkdir(parents=True, exist_ok=True)
    m = parent.plan()
    for i, item in enumerate(m['samples']):
        im = Image.new('RGB', (256, 256), ((i * 19) % 230, (i * 31) % 230, (i * 43) % 230))
        if item['name'] == v.TARGET:
            ImageDraw.Draw(im).rectangle((0, 0, 255, 229), fill='white')
        p = folder / (item['name'] + '.jpeg'); p.write_bytes(jpg(im))
        item.update(imageFile=p.name, sha256=parent.sha(p), byteCount=p.stat().st_size)
    parent.produce(m, folder)
    return folder

def geometry():
    m = v.plan()
    assert m['v184TileXYZ'] == [8715, 5763, 14]
    assert m['wmsCRS'] == 'EPSG:3857'
    assert m['wmsBoundsEPSG3857'] == [1279250.105381, 5938851.349645,
                                      1281696.090286, 5941297.33455]
    assert 'REQUEST=GetMap' in m['wmsRequestUrl']
    assert 'LAYERS=Aerial-2023-RGB' in m['wmsRequestUrl']
    assert 'CRS=EPSG%3A3857' in m['wmsRequestUrl']
    assert '2023' in m['sourceMetadata']
    assert m['license'].startswith('CC BY 4.0')
    assert v.validate(m)

def false_approvals():
    m = v.plan()
    assert not m['alternativeCoverageApproved'] and not m['alternativeUsableForPeriodArt']
    assert all(m[k] is False for k in v.FALSE_FLAGS)
    for change in (
        lambda x: x.update(productionApproved=True),
        lambda x: x.update(historicalRoadsVerified=True),
        lambda x: x.update(bridgeBanksVerified=True),
        lambda x: x.update(alternativeCoverageApproved=True),
        lambda x: x.update(wmsCRS='EPSG:4326'),
        lambda x: x.update(wmsLayer='invented-road'),
        lambda x: x.update(wmsBoundsEPSG3857=[0, 0, 1, 1]),
        lambda x: x.update(sourceMetadata=''),
        lambda x: x.update(historicRoad=[(1, 2), (3, 4)]),
    ):
        candidate = copy.deepcopy(m); change(candidate)
        reject(lambda: v.validate(candidate))

def synthetic_audit():
    original = Image.new('RGB', (256, 256), 'white')
    alternative = Image.new('RGB', (256, 256), (55, 93, 71))
    audit = v.audit(original, alternative)
    assert audit['candidateSupplementalPixels'] == 65536
    assert audit['v184OriginalNearWhitePixels'] == 65536
    assert not audit['gameArtCoverageApproved']
    assert audit['candidateOnlyNotStitched']
    assert v.audit(original, Image.new('RGB', (256, 256), 'white'))['candidateSupplementalPixels'] == 0

def bad_wms():
    reject(lambda: v.inspect_jpeg(b'<ServiceException>invalid</ServiceException>'))
    reject(lambda: v.inspect_jpeg(jpg(Image.new('RGB', (200, 256), 'green'))))

def real_roundtrip_synthetic():
    with tempfile.TemporaryDirectory() as d:
        root = Path(d); source = fixture(root / 'parent'); out = root / 'v185'
        alt = jpg(Image.new('RGB', (256, 256), (46, 100, 58)))
        m = v.produce(source, out, alt)
        assert m['coverageAudit']['candidateSupplementalPixels'] > 50000
        assert m['coverageAudit']['candidateOnlyNotStitched']
        assert all(m[k] is False for k in v.FALSE_FLAGS)
        assert v.verify(source, out)
        p = out / m['alternativeFile']; p.write_bytes(b'bad')
        reject(lambda: v.verify(source, out))

def reject_blank_alternative():
    with tempfile.TemporaryDirectory() as d:
        root = Path(d); source = fixture(root / 'parent')
        reject(lambda: v.produce(source, root / 'v185', jpg(Image.new('RGB', (256, 256), 'white'))))

def reject_parent_change():
    with tempfile.TemporaryDirectory() as d:
        root = Path(d); source = fixture(root / 'parent'); out = root / 'v185'
        v.produce(source, out, jpg(Image.new('RGB', (256, 256), (46, 100, 58))))
        (source / 'r11c03.jpeg').write_bytes(b'tampered')
        reject(lambda: v.verify(source, out))

for name, fn in [
    ('independent Italian WMS tile registered exactly to V184 pixel frame', geometry),
    ('license, CRS, road/bridge/GAME approvals fail closed', false_approvals),
    ('only candidate source coverage measured, no automatic stitch', synthetic_audit),
    ('WMS XML and wrong-sized JPEG rejected', bad_wms),
    ('source plus candidate image hashes verified on synthetic raster', real_roundtrip_synthetic),
    ('blank WMS response cannot certify candidate coverage', reject_blank_alternative),
    ('changed V184 parent source rejected', reject_parent_change),
]:
    check(name, fn)
print(f'V185 {passed} tests passed; modern supplemental SOURCE only')

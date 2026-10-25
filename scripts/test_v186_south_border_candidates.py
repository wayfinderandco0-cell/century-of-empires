#!/usr/bin/env python3
"""V186 fail-closed candidate-only cross-border source tests (synthetic imagery)."""
import copy
import io
import json
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw
import v184_matrei_brenner_overview as parent
import v185_south_tyrol_probe as previous
import v186_south_border_candidates as v

passed = 0


def check(label, fn):
    global passed
    fn()
    passed += 1
    print('PASS', label)


def reject(fn):
    try:
        fn()
    except (ValueError, FileNotFoundError, KeyError, OSError):
        return
    raise AssertionError('tampered source or false approval accepted')


def jpeg(im):
    buf = io.BytesIO()
    im.save(buf, format='JPEG', quality=94)
    return buf.getvalue()


def fixture(root):
    root.mkdir(parents=True, exist_ok=True)
    manifest = parent.plan()
    for i, item in enumerate(manifest['samples']):
        im = Image.new('RGB', (256, 256), ((i * 19) % 210, 80, 65))
        if item['row'] in v.ROWS:
            ImageDraw.Draw(im).rectangle((20, 20, 210, 210), fill=(255, 255, 255))
        if item['name'] == previous.TARGET:
            ImageDraw.Draw(im).rectangle((0, 0, 255, 229), fill='white')
        path = root / (item['name'] + '.jpeg')
        path.write_bytes(jpeg(im))
        item.update(imageFile=path.name, sha256=parent.sha(path),
                    byteCount=path.stat().st_size)
    parent.produce(manifest, root)
    return root


def alternatives():
    samples = {}
    for i, item in enumerate(v.plan()['sourceTileCandidates']):
        im = Image.new('RGB', (256, 256), (40 + i, 95, 55))
        draw = ImageDraw.Draw(im)
        for k in range(16):
            draw.line((k * 16, 0, k * 16 + 70, 255),
                      fill=(55 + k * 3, 110, 60 + k * 2), width=3)
        samples[item['name']] = jpeg(im)
    return samples


def geometry():
    m = v.plan()
    assert m['sampleCount'] == 10
    assert m['sampleRows'] == [10, 11]
    assert m['candidateDimensions'] == [1280, 512]
    assert m['candidateOffsetInParentPixels'] == [0, 2560]
    assert len({tuple(t['tileXYZ']) for t in m['sourceTileCandidates']}) == 10
    assert all(t['tileXYZ'][2] == 14 for t in m['sourceTileCandidates'])
    assert next(t for t in m['sourceTileCandidates']
                if t['name'] == previous.TARGET)['wmsUrl'] == previous.plan()['wmsRequestUrl']
    assert v.validate(m)


def no_approvals():
    m = v.plan()
    assert all(m[f] is False for f in v.FALSE_FLAGS)
    assert m['neverOverwriteObservedAustrianSourcePixels']
    assert m['unreviewedSnowOrCloudMayBeMisclassified']
    for mutation in (
        lambda x: x.update(productionApproved=True),
        lambda x: x.update(bridgeBanksVerified=True),
        lambda x: x.update(crossBorderSeamsApproved=True),
        lambda x: x.update(modernGeographicCoverageApproved=True),
        lambda x: x.update(sampleRows=[9, 10]),
        lambda x: x.update(requiredAttribution=''),
        lambda x: x['sourceTileCandidates'][0].update(tileXYZ=[0, 0, 14]),
        lambda x: x.update(historicalRoad=[(0, 0), (1, 1)]),
    ):
        candidate = copy.deepcopy(m)
        mutation(candidate)
        reject(lambda: v.validate(candidate))


def synthetic_roundtrip():
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        source = fixture(root / 'parent')
        out = root / 'v186'
        m = v.produce(source, out, alternatives())
        assert v.verify(source, out)
        assert m['candidateAudit']['candidatePixels'] > 10000
        assert m['candidateAudit']['candidateOnlyNotStitched']
        assert all(m[f] is False for f in v.FALSE_FLAGS)
        with Image.open(out / v.OUTPUT_IMAGE) as image:
            assert image.mode == 'RGBA' and image.size == (1280, 512)
            assert image.getpixel((5, 5))[3] == 0  # observed Austrian source
            assert image.getpixel((80, 80))[3] == 255  # only suspected white source
            assert image.getpixel((256 + 5, 5))[3] == 0


def reject_source_tamper():
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        source = fixture(root / 'parent')
        out = root / 'v186'
        v.produce(source, out, alternatives())
        (source / 'r10c00.jpeg').write_bytes(b'tampered')
        reject(lambda: v.verify(source, out))


def reject_candidate_tamper():
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        source = fixture(root / 'parent')
        out = root / 'v186'
        v.produce(source, out, alternatives())
        (out / 'italian-r10c00.jpeg').write_bytes(b'tampered')
        reject(lambda: v.verify(source, out))


def reject_overlay_tamper():
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        source = fixture(root / 'parent')
        out = root / 'v186'
        v.produce(source, out, alternatives())
        path = out / v.OUTPUT_IMAGE
        with Image.open(path) as image:
            altered = image.copy()
        altered.putpixel((5, 5), (255, 0, 0, 255))
        altered.save(path)
        reject(lambda: v.verify(source, out))


def reject_manifest_forgery():
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        source = fixture(root / 'parent')
        out = root / 'v186'
        v.produce(source, out, alternatives())
        path = out / 'manifest.json'
        m = json.loads(path.read_text())
        m['candidateAudit']['geographicSourceCoverageApproved'] = True
        path.write_text(json.dumps(m))
        reject(lambda: v.verify(source, out))


def reject_missing_or_wrong_jpeg():
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        source = fixture(root / 'parent')
        samples = alternatives()
        samples.pop('r10c00')
        reject(lambda: v.produce(source, root / 'out', samples))
        samples = alternatives()
        samples['r10c00'] = jpeg(Image.new('RGB', (100, 100), 'red'))
        reject(lambda: v.produce(source, root / 'out', samples))


for label, fn in (
    ('10 independently georegistered southern tiles and V185 consistency', geometry),
    ('source metadata and all false historical/road/GAME approvals immutable', no_approvals),
    ('real RGBA candidate mask preserves observed source pixels', synthetic_roundtrip),
    ('altered Austrian parent source rejected', reject_source_tamper),
    ('altered independent Italian source rejected', reject_candidate_tamper),
    ('opaque overwrite of observed source rejected', reject_overlay_tamper),
    ('forged candidate coverage approval rejected', reject_manifest_forgery),
    ('missing and malformed WMS source rejected', reject_missing_or_wrong_jpeg),
):
    check(label, fn)
print(f'V186 {passed} tests passed; source candidates only, NOT GAME ART')

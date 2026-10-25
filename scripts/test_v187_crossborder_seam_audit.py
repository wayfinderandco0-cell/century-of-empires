#!/usr/bin/env python3
"""V187 fail-closed seam audit tests; synthetic modern-source fixtures only."""
import copy
import io
import json
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw
import v184_matrei_brenner_overview as v184
import v186_south_border_candidates as v186
import v187_crossborder_seam_audit as v187


def jpeg(image):
    out = io.BytesIO()
    image.save(out, format='JPEG', quality=94)
    return out.getvalue()


def fixture(root, contrast=False):
    parent = root / 'v184'
    parent.mkdir(parents=True)
    manifest = v184.plan()
    colors = {}
    for i, tile in enumerate(manifest['samples']):
        color = (35 + (i * 3) % 150, 60 + (i * 5) % 130,
                 70 + (i * 7) % 120)
        colors[tile['name']] = color
        im = Image.new('RGB', (256, 256), color)
        if tile['row'] >= 10:
            ImageDraw.Draw(im).rectangle((128, 0, 255, 255),
                                         fill=(255, 255, 255))
        ImageDraw.Draw(im).rectangle((0, 0, 3, 3),
                                    fill=((i * 37) % 256, (i * 79) % 256,
                                          (i * 121) % 256))
        file = parent / (tile['name'] + '.jpeg')
        file.write_bytes(jpeg(im))
        tile.update(imageFile=file.name, sha256=v184.sha(file),
                    byteCount=file.stat().st_size)
    v184.produce(manifest, parent)
    alternatives = {}
    for tile in v186.plan()['sourceTileCandidates']:
        color = (12, 14, 18) if contrast else colors[tile['name']]
        alternatives[tile['name']] = jpeg(Image.new('RGB', (256, 256), color))
    candidate = root / 'v186'
    v186.produce(parent, candidate, alternatives)
    return parent, candidate


def reject(action):
    try:
        action()
    except (ValueError, OSError, KeyError):
        return
    raise AssertionError('tampering or false historical approval was accepted')


def roundtrip():
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        parent, candidate = fixture(root)
        output = root / 'v187'
        result = v187.produce(parent, candidate, output)
        assert v187.verify(parent, candidate, output)
        assert result['nativeGridPixels'] == [1280, 512]
        assert result['boundaryRGBDifference']['count'] > 0
        assert result['overlapRGBDifference']['count'] > 0
        assert sum(v['candidatePixels'] for v in result['perTile'].values()) == (
            json.loads((candidate / 'manifest.json').read_text())
            ['candidateAudit']['candidatePixels'])
        assert all(result[k] is False for k in v187.FALSE_APPROVALS)
        assert set(p.name for p in output.iterdir()) == {v187.REPORT}


def contrast_warning():
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        p1, c1 = fixture(root / 'low')
        p2, c2 = fixture(root / 'high', contrast=True)
        low = v187.audit(p1, c1)
        high = v187.audit(p2, c2)
        assert high['boundaryRGBDifference']['p90RGB'] > (
            low['boundaryRGBDifference']['p90RGB'] + 30)
        assert high['overlapRGBDifference']['p90RGB'] > (
            low['overlapRGBDifference']['p90RGB'] + 30)
        assert not high['crossBorderSeamsApproved']


def reject_report_forgery():
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        p, c = fixture(root)
        out = root / 'v187'
        v187.produce(p, c, out)
        path = out / v187.REPORT
        report = json.loads(path.read_text())
        report['crossBorderSeamsApproved'] = True
        path.write_text(json.dumps(report))
        reject(lambda: v187.verify(p, c, out))


def reject_boundary_forgery():
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        p, c = fixture(root)
        out = root / 'v187'
        v187.produce(p, c, out)
        path = out / v187.REPORT
        report = json.loads(path.read_text())
        report['boundaryRGBDifference']['p90RGB'] = 0
        path.write_text(json.dumps(report))
        reject(lambda: v187.verify(p, c, out))


def reject_source_tamper():
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        p, c = fixture(root)
        out = root / 'v187'
        v187.produce(p, c, out)
        (p / 'r11c03.jpeg').write_bytes(b'bad source')
        reject(lambda: v187.verify(p, c, out))


def reject_alternative_tamper():
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        p, c = fixture(root)
        out = root / 'v187'
        v187.produce(p, c, out)
        (c / 'italian-r11c03.jpeg').write_bytes(b'bad alternative')
        reject(lambda: v187.verify(p, c, out))


for name, test in (
    ('exact 10-tile native source seam and overlap diagnostics', roundtrip),
    ('large cross-provider color mismatch remains a warning', contrast_warning),
    ('forged GAME/bridge/source seam approval rejected', reject_report_forgery),
    ('falsified seam statistics rejected', reject_boundary_forgery),
    ('altered original Austrian JPEG rejected', reject_source_tamper),
    ('altered South Tyrol JPEG rejected', reject_alternative_tamper),
):
    test()
    print('PASS', name)
print('V187 6 tests passed; modern-source seam evidence only, GAME ART NOT APPROVED')

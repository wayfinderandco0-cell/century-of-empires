#!/usr/bin/env python3
"""V181 fail-closed SOURCE mask tests; no historical or GAME approvals."""
import argparse
import json
import shutil
import tempfile
from pathlib import Path
from PIL import Image
import v181_matrei_exclusions as v

def rejected(fn):
    try: fn()
    except (ValueError, FileNotFoundError, KeyError): return
    raise AssertionError('unsafe source or forged output was accepted')

def run(source):
    passed=0
    def test(label, fn):
        nonlocal passed
        fn(); passed+=1; print('PASS',label)
    source=Path(source)
    def geometry():
        m,img=v.read_source(source)
        assert m['tileOriginXYZ']==[69701,46030,17]
        assert len(m['samples'])==18 and img.size==v.SIZE
        assert img.getpixel((250,800))[3]==0
    test('V180 18-JPEG original source provenance and southwest hole',geometry)
    with tempfile.TemporaryDirectory() as tmp:
        out=Path(tmp)/'output'
        report=v.build(source,out)
        def output():
            assert v.verify(source,out)
            assert 0 < report['excludedObservedPixels'] < report['observedSourcePixels']
            assert report['excludedPercentOfObserved']<30
            assert report['unreviewedBuiltEnvironmentStillPresent']
            assert all(report[k] is False for k in v.FALSE_FLAGS)
        test('native-source mask generated and independently reverified',output)
        def probes():
            with Image.open(out/'matrei-modern-excluded-SOURCE.png') as img:
                for point in [(972,100),(969,500),(989,900),(1430,40),
                              (1364,470),(1250,900),(1290,80),(1115,470)]:
                    assert img.getpixel(point)==(0,0,0,0),('modern feature still visible',point)
                for point in [(250,250),(650,340),(850,600),(1450,850)]:
                    assert img.getpixel(point)[3]==255,('unrelated natural source removed',point)
                assert img.getpixel((250,800))==(0,0,0,0)
        test('motorway, rail and sports removed; forest, meadow and river preserved',probes)
        def output_tamper():
            path=out/'matrei-modern-excluded-SOURCE.png'
            with Image.open(path) as im: edited=im.copy()
            edited.putpixel((250,250),(255,0,0,255)); edited.save(path)
            rejected(lambda:v.verify(source,out))
        test('tampered output PNG rejected',output_tamper)
        v.build(source,out)
        def mask_tamper():
            path=out/'matrei-modern-exclusion-mask.png'
            with Image.open(path) as im: edited=im.copy()
            edited.putpixel((250,250),255); edited.save(path)
            rejected(lambda:v.verify(source,out))
        test('invented extra exclusion geometry rejected',mask_tamper)
        v.build(source,out)
        def false_approval():
            path=out/'manifest.json'
            m=json.loads(path.read_text());m['periodArtComplete']=True
            path.write_text(json.dumps(m))
            rejected(lambda:v.verify(source,out))
        test('false period-art approval rejected',false_approval)
    with tempfile.TemporaryDirectory() as tmp:
        copied=Path(tmp)/'source';shutil.copytree(source,copied)
        def bad_mosaic():
            path=copied/'matrei-modern-source-L.png'
            with Image.open(path) as im: changed=im.copy()
            changed.putpixel((250,250),(0,0,0,255));changed.save(path)
            rejected(lambda:v.read_source(copied))
        test('altered original V180 mosaic rejected',bad_mosaic)
        shutil.rmtree(copied);shutil.copytree(source,copied)
        def bad_jpeg():
            (copied/'r0c0.jpeg').write_bytes(b'not a source JPEG')
            rejected(lambda:v.read_source(copied))
        test('altered native JPEG rejected',bad_jpeg)
    print(f'V181 {passed} source-only regression tests passed; GAME art remains unapproved.')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',default='qa/v180-matrei-source')
    run(p.parse_args().source)

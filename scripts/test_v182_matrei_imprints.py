#!/usr/bin/env python3
"""Fail-closed tests for source-only date-stamp removal."""
import argparse
import json
import shutil
import tempfile
from pathlib import Path
from PIL import Image
import v182_matrei_imprints as v

def reject(fn):
    try:
        fn()
    except (ValueError,FileNotFoundError,KeyError):
        return
    raise AssertionError('forged source or approval was accepted')

def run(source,previous):
    source,previous=Path(source),Path(previous)
    count=0
    def test(label,fn):
        nonlocal count
        fn()
        count+=1
        print('PASS',label)
    with tempfile.TemporaryDirectory() as tmp:
        out=Path(tmp)/'out'
        m=v.build(source,previous,out)
        test('verified V180 and V181 provenance',lambda:v.read_verified(source,previous))
        test('date-imprint SOURCE output independently reverified',lambda:v.verify(source,previous,out))
        def stamps():
            with Image.open(out/'matrei-no-date-imprints-SOURCE.png') as im:
                for x,y in v.STAMP_CENTERS:
                    assert im.getpixel((x,y))==(0,0,0,0),(x,y)
            assert 0<m['newlyExcludedObservedPixels']<10000
            assert len(v.STAMP_CENTERS)==7
        test('seven image-reviewed date stamps are transparent',stamps)
        def retention():
            with Image.open(previous/'matrei-modern-excluded-SOURCE.png') as old, Image.open(out/'matrei-no-date-imprints-SOURCE.png') as new:
                for xy in ((250,250),(650,340),(850,600),(1450,850)):
                    assert new.getpixel(xy)==old.getpixel(xy),xy
                assert new.getpixel((250,800))==(0,0,0,0)
                assert new.getpixel((972,100))==(0,0,0,0)
        test('forest/meadow/river and previous holes preserved',retention)
        def approvals():
            assert all(m[k] is False for k in v.FALSE_FLAGS)
        test('all GAME/historic/production approval remains false',approvals)
        def tamper_output():
            f=out/'matrei-no-date-imprints-SOURCE.png'
            with Image.open(f) as im:
                x=im.copy()
            x.putpixel((320,96),(255,255,255,255))
            x.save(f)
            reject(lambda:v.verify(source,previous,out))
        test('tampered output rejected',tamper_output)
        v.build(source,previous,out)
        def tamper_mask():
            f=out/'matrei-date-imprint-mask.png'
            with Image.open(f) as im:
                x=im.copy()
            x.putpixel((250,250),255)
            x.save(f)
            reject(lambda:v.verify(source,previous,out))
        test('invented stamp area rejected',tamper_mask)
        v.build(source,previous,out)
        def forged_approval():
            f=out/'manifest.json'
            data=json.loads(f.read_text())
            data['periodArtComplete']=True
            f.write_text(json.dumps(data))
            reject(lambda:v.verify(source,previous,out))
        test('forged period approval rejected',forged_approval)
        v.build(source,previous,out)
        with tempfile.TemporaryDirectory() as altered:
            p=Path(altered)/'previous'
            shutil.copytree(previous,p)
            f=p/'matrei-modern-excluded-SOURCE.png'
            with Image.open(f) as im:
                x=im.copy()
            x.putpixel((250,250),(0,0,0,255))
            x.save(f)
            test('tampered V181 input rejected',lambda:reject(lambda:v.verify(source,p,out)))
    print(f'V182 {count} tests passed; historic roads and GAME art not certified')

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--source',default='qa/v180-matrei-source')
    p.add_argument('--previous',default='qa/v181-matrei-exclusions')
    a=p.parse_args()
    run(a.source,a.previous)

#!/usr/bin/env python3
"""Fail-closed V220 offline tests; no network and no visual approval shortcuts."""
import copy
import io
import tempfile
from pathlib import Path
from PIL import Image
import v220_contiguous_native_cells as v

def must_reject(fn):
    try: fn()
    except (ValueError, KeyError, AssertionError): return
    raise AssertionError('invalid source/geography/approval input accepted')

def test():
    p=v.plan()
    assert v.assert_plan(p)
    assert p['version']==220 and len(p['cells'])==2
    assert p['nativeCellPixels']==[1536,1024]
    assert all(p[f] is False for f in v.FLAGS)
    assert p['sourceAreasNotGameGeography'] and p['unreviewedModernFeaturesMayRemain']
    xyz=[]
    for cell in p['cells']:
        assert len(cell['tiles'])==24
        x,y,z=cell['originXYZ']
        for tile in cell['tiles']:
            assert tile['xyz']==[x+tile['col'],y+tile['row'],z]
            xyz.append(tuple(tile['xyz']))
    assert len(set(xyz))==48
    wrong=copy.deepcopy(p);wrong['gameArtApproved']=True
    must_reject(lambda:v.assert_plan(wrong))
    wrong=copy.deepcopy(p);wrong['sourceAreasNotGameGeography']=False
    must_reject(lambda:v.assert_plan(wrong))
    wrong=copy.deepcopy(p);wrong['cells'][1]['tiles'][0]['xyz']=p['cells'][0]['tiles'][0]['xyz']
    must_reject(lambda:v.assert_plan(wrong))
    wrong=copy.deepcopy(p);wrong['cells'][0]['nativePixels']=[768,512]
    must_reject(lambda:v.assert_plan(wrong))
    with tempfile.TemporaryDirectory() as tmp:
        folder=Path(tmp)
        cell=copy.deepcopy(p['cells'][0])
        for t in cell['tiles']:
            # Native 256x256 JPEGs with distinguishable row/column colors.
            color=(t['col']*34+20,t['row']*54+18,120)
            im=Image.new('RGB',(256,256),color)
            buff=io.BytesIO();im.save(buff,format='JPEG',quality=95)
            raw=buff.getvalue()
            (folder/t['name']).write_bytes(raw)
            t['sha256']=v.sha(raw);t['byteCount']=len(raw)
        out=v.source_image(cell,folder)
        assert out.size==(1536,1024)
        assert out.getpixel((5,5))!=out.getpixel((261,5))
        assert out.getpixel((5,5))!=out.getpixel((5,261))
        assert out.getpixel((1280+4,768+4))!=out.getpixel((4,4))
        first=cell['tiles'][0]
        first['sha256']='0'*64
        must_reject(lambda:v.source_image(cell,folder))
    print('V220 offline source geometry/48 distinct tiles/native pixel/false approval tests PASS')

if __name__=='__main__':test()
